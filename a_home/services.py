from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
from .models import (
    GlavnaKnjiga, PoslovnaGodina, PoslovniPartner,
    SaldoKonta, PrenosStanja, Knjizenje, StavkaKnjizenja,
    Inventura
)


class ZakljucivanjeGodineService:

    @staticmethod
    @transaction.atomic
    def izracunaj_salda(glavna_knjiga):
        """
        Izračunava saldo po svakom kontu i partneru
        na osnovu svih knjiženja u glavnoj knjizi.
        """
        # Obriši stare preračunate salde
        SaldoKonta.objects.filter(glavna_knjiga=glavna_knjiga).delete()

        # Grupiši stavke knjiženja po kontu
        from django.db.models import Q
        stavke = StavkaKnjizenja.objects.filter(
            knjizenje__glavna_knjiga=glavna_knjiga
        ).values('konto').annotate(
            ukupno_duguje=Sum('duguje'),
            ukupno_potrazuje=Sum('potrazuje')
        )

        salda = []
        for stavka in stavke:
            duguje    = stavka['ukupno_duguje'] or Decimal('0')
            potrazuje = stavka['ukupno_potrazuje'] or Decimal('0')
            saldo     = duguje - potrazuje

            salda.append(SaldoKonta(
                glavna_knjiga=glavna_knjiga,
                konto_id=stavka['konto'],
                partner=glavna_knjiga.partner,
                duguje=duguje,
                potrazuje=potrazuje,
                saldo=saldo,
            ))

        SaldoKonta.objects.bulk_create(salda)
        return salda

    @staticmethod
    @transaction.atomic
    def zakljuci_godinu(glavna_knjiga, korisnik):
        """
        1. Izračunava salda
        2. Zaključuje glavnu knjigu
        """
        if glavna_knjiga.zakljucena:
            raise ValueError("Glavna knjiga je već zaključena.")

        # Provjeri da li postoji otvorena inventura
        otvorene = Inventura.objects.filter(
            glavna_knjiga=glavna_knjiga,
            status__in=['otvorena', 'u_toku']
        )
        if otvorene.exists():
            raise ValueError("Postoje nezaključene inventure. Zaključite inventuru prije zatvaranja godine.")

        # Izračunaj salda
        ZakljucivanjeGodineService.izracunaj_salda(glavna_knjiga)

        # Zaključi
        glavna_knjiga.zakljucena = True
        glavna_knjiga.save()

        return glavna_knjiga

    @staticmethod
    @transaction.atomic
    def prenesi_stanje(partner, iz_godine, u_godinu, korisnik):
        """
        Prenosi zaključna salda iz jedne godine u novu
        i automatski kreira knjiženje prenosa.
        """
        # Dohvati zaključenu knjigu iz stare godine
        try:
            stara_knjiga = GlavnaKnjiga.objects.get(
                partner=partner,
                godina=iz_godine,
                zakljucena=True
            )
        except GlavnaKnjiga.DoesNotExist:
            raise ValueError(f"Glavna knjiga za {iz_godine} nije zaključena ili ne postoji.")

        # Provjeri da prenos već nije izvršen
        if PrenosStanja.objects.filter(
            partner=partner,
            iz_godine=iz_godine,
            u_godinu=u_godinu,
            status='izvrseno'
        ).exists():
            raise ValueError("Prenos stanja za ovu godinu je već izvršen.")

        # Kreiraj ili dohvati novu glavnu knjigu
        nova_knjiga, _ = GlavnaKnjiga.objects.get_or_create(
            partner=partner,
            godina=u_godinu
        )

        # Dohvati salda koja treba prenijeti (samo nenulta)
        salda = SaldoKonta.objects.filter(
            glavna_knjiga=stara_knjiga,
            preneseno=False
        ).exclude(saldo=0)

        if not salda.exists():
            raise ValueError("Nema salda za prenos.")

        # Kreiraj log prenosa
        prenos = PrenosStanja.objects.create(
            iz_godine=iz_godine,
            u_godinu=u_godinu,
            partner=partner,
            status='priprema',
            kreirao=korisnik,
        )

        # Kreiraj knjiženje prenosa u novoj godini
        knjizenje = Knjizenje.objects.create(
            glavna_knjiga=nova_knjiga,
            datum=u_godinu.datum_pocetka if hasattr(u_godinu, 'datum_pocetka') else
                  __import__('datetime').date(u_godinu.godina, 1, 1),
            opis=f"Prenos početnog stanja iz {iz_godine.godina}. godine",
            dokument_broj=f"PRENOS-{iz_godine.godina}",
            kreirao=korisnik,
        )

        # Kreiraj stavke knjiženja za svaki saldo
        stavke = []
        for saldo in salda:
            if saldo.saldo > 0:
                # Pozitivni saldo → duguje u novoj godini
                stavke.append(StavkaKnjizenja(
                    knjizenje=knjizenje,
                    konto=saldo.konto,
                    opis=f"Početno stanje — prenos iz {iz_godine.godina}.",
                    duguje=abs(saldo.saldo),
                    potrazuje=Decimal('0'),
                ))
            elif saldo.saldo < 0:
                # Negativni saldo → potražuje u novoj godini
                stavke.append(StavkaKnjizenja(
                    knjizenje=knjizenje,
                    konto=saldo.konto,
                    opis=f"Početno stanje — prenos iz {iz_godine.godina}.",
                    duguje=Decimal('0'),
                    potrazuje=abs(saldo.saldo),
                ))

        StavkaKnjizenja.objects.bulk_create(stavke)

        # Označi salde kao prenesene
        salda.update(preneseno=True, datum_prenosa=timezone.now())

        # Ažuriraj prenos log
        prenos.status     = 'izvrseno'
        prenos.knjizenje  = knjizenje
        prenos.broj_stavki = len(stavke)
        prenos.save()

        return prenos


class InventuraService:

    @staticmethod
    @transaction.atomic
    def zakljuci_inventuru(inventura, korisnik):
        """Zaključuje inventuru — nakon toga se ne može mijenjati."""
        if inventura.status == 'zakljucena':
            raise ValueError("Inventura je već zaključena.")

        inventura.status       = 'zakljucena'
        inventura.zakljucena_u = timezone.now()
        inventura.save()

        return inventura

    @staticmethod
    def getSummary(inventura):
        """Vraća sumarni pregled inventure."""
        stavke = inventura.stavke.select_related('artikal').all()
        return {
            'ukupno_artikala': stavke.count(),
            'visak_artikala':  stavke.filter(kolicina_popis__gt=models.F('kolicina_knjig')).count(),
            'manjak_artikala': stavke.filter(kolicina_popis__lt=models.F('kolicina_knjig')).count(),
            'uskladjeno':      stavke.filter(kolicina_popis=models.F('kolicina_knjig')).count(),
            'ukupni_visak':    inventura.ukupni_visak,
            'ukupni_manjak':   inventura.ukupni_manjak,
        }