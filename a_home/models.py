from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


# ─────────────────────────────────────────
#  ŠIFARNICI
# ─────────────────────────────────────────

class PoslovnaGodina(models.Model):
    godina = models.IntegerField(unique=True, verbose_name="Godina")
    aktivna = models.BooleanField(default=True, verbose_name="Aktivna")
    napomena = models.CharField(max_length=255, blank=True, verbose_name="Napomena")
    kreirana = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-godina']
        verbose_name = "Poslovna godina"
        verbose_name_plural = "Poslovne godine"

    def __str__(self):
        return str(self.godina)


class Entitet(models.TextChoices):
    FBIH   = '01', 'FBiH'
    RS     = '02', 'RS'
    BRCKO  = '03', 'Brčko'


class PoslovniPartner(models.Model):
    # Osnovno
    sifra              = models.CharField(max_length=20, unique=True, verbose_name="Šifra partnera")
    naziv_1            = models.CharField(max_length=255, verbose_name="Naziv partnera (1)")
    naziv_2            = models.CharField(max_length=255, blank=True, verbose_name="Naziv partnera (2)")

    # Adresa
    ptt                = models.CharField(max_length=10, blank=True, verbose_name="PTT")
    mjesto             = models.CharField(max_length=100, blank=True, verbose_name="Mjesto")
    ulica              = models.CharField(max_length=255, blank=True, verbose_name="Ulica")

    # Kontakt
    telefon            = models.CharField(max_length=50, blank=True, verbose_name="Telefon")
    fax                = models.CharField(max_length=50, blank=True, verbose_name="Fax")

    # Finansijski
    ziro_racun         = models.CharField(max_length=50, blank=True, verbose_name="Žiro-račun")
    sifra_sjedista     = models.CharField(max_length=20, blank=True, verbose_name="Šifra sjedišta")
    sinteticki_konto   = models.CharField(max_length=20, blank=True, verbose_name="Sintetički konto")

    # Registracija
    maticni_broj       = models.CharField(max_length=20, blank=True, verbose_name="Matični broj")
    porezni_broj       = models.CharField(max_length=20, blank=True, verbose_name="Porezni broj")
    broj_upisa_sud_reg = models.CharField(max_length=50, blank=True, verbose_name="Br. upisa u sud. reg.")

    # PDV i entitet
    u_sustavu_pdv      = models.BooleanField(default=False, verbose_name="U sustavu PDV-a")
    entitet            = models.CharField(max_length=2, choices=Entitet.choices, default=Entitet.FBIH, verbose_name="Entitet")

    # Meta
    aktivan            = models.BooleanField(default=True, verbose_name="Aktivan")
    kreiran            = models.DateTimeField(auto_now_add=True)
    izmijenjen         = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sifra']
        verbose_name = "Poslovni partner"
        verbose_name_plural = "Poslovni partneri"

    def __str__(self):
        return f"{self.sifra} — {self.naziv_1}"


class Porez(models.Model):
    naziv  = models.CharField(max_length=100, verbose_name="Naziv poreza")
    stopa  = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Stopa (%)"
    )
    aktivan = models.BooleanField(default=True, verbose_name="Aktivan")

    class Meta:
        ordering = ['stopa']
        verbose_name = "Porez"
        verbose_name_plural = "Porezi"

    def __str__(self):
        return f"{self.naziv} ({self.stopa}%)"


class GrupaArtikla(models.Model):
    sifra  = models.CharField(max_length=20, unique=True, verbose_name="Šifra grupe")
    naziv  = models.CharField(max_length=255, verbose_name="Naziv grupe")

    class Meta:
        ordering = ['sifra']
        verbose_name = "Grupa artikla"
        verbose_name_plural = "Grupe artikala"

    def __str__(self):
        return f"{self.sifra} — {self.naziv}"


class JedinicaMjere(models.Model):
    sifra  = models.CharField(max_length=10, unique=True, verbose_name="Šifra")
    naziv  = models.CharField(max_length=50, verbose_name="Naziv")

    class Meta:
        ordering = ['sifra']
        verbose_name = "Jedinica mjere"
        verbose_name_plural = "Jedinice mjere"

    def __str__(self):
        return self.sifra


class Artikal(models.Model):
    sifra          = models.CharField(max_length=20, unique=True, verbose_name="Šifra artikla")
    naziv          = models.CharField(max_length=255, verbose_name="Naziv artikla")
    grupa          = models.ForeignKey(GrupaArtikla, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Grupa")
    jedinica_mjere = models.ForeignKey(JedinicaMjere, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Jedinica mjere")
    cijena         = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))], verbose_name="Cijena")
    porez          = models.ForeignKey(Porez, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Porez")
    aktivan        = models.BooleanField(default=True, verbose_name="Aktivan")
    kreiran        = models.DateTimeField(auto_now_add=True)
    izmijenjen     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sifra']
        verbose_name = "Artikal"
        verbose_name_plural = "Artikli"

    def __str__(self):
        return f"{self.sifra} — {self.naziv}"

    @property
    def cijena_sa_porezom(self):
        if self.porez:
            return self.cijena * (1 + self.porez.stopa / 100)
        return self.cijena


# ─────────────────────────────────────────
#  KONTNI PLAN
# ─────────────────────────────────────────

class Konto(models.Model):
    TIP_CHOICES = [
        ('aktiva',   'Aktiva'),
        ('pasiva',   'Pasiva'),
        ('prihod',   'Prihod'),
        ('rashod',   'Rashod'),
        ('izvanbil', 'Izvanbilansna'),
    ]

    broj    = models.CharField(max_length=10, unique=True, verbose_name="Broj konta")
    naziv   = models.CharField(max_length=255, verbose_name="Naziv konta")
    tip     = models.CharField(max_length=10, choices=TIP_CHOICES, verbose_name="Tip konta")
    aktivan = models.BooleanField(default=True, verbose_name="Aktivan")

    class Meta:
        ordering = ['broj']
        verbose_name = "Konto"
        verbose_name_plural = "Konta"

    def __str__(self):
        return f"{self.broj} — {self.naziv}"


# ─────────────────────────────────────────
#  GLAVNA KNJIGA
# ─────────────────────────────────────────

class GlavnaKnjiga(models.Model):
    partner    = models.ForeignKey(PoslovniPartner, on_delete=models.PROTECT, related_name='glavne_knjige', verbose_name="Partner")
    godina     = models.ForeignKey(PoslovnaGodina, on_delete=models.PROTECT, related_name='glavne_knjige', verbose_name="Godina")
    zakljucena = models.BooleanField(default=False, verbose_name="Zaključena")
    kreirana   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('partner', 'godina')
        verbose_name = "Glavna knjiga"
        verbose_name_plural = "Glavne knjige"

    def __str__(self):
        return f"{self.partner.naziv_1} — {self.godina.godina}"


class Knjizenje(models.Model):
    glavna_knjiga  = models.ForeignKey(GlavnaKnjiga, on_delete=models.PROTECT, related_name='knjizenja', verbose_name="Glavna knjiga")
    broj_naloga    = models.IntegerField(default=1, verbose_name="Broj naloga")  
    datum          = models.DateField(verbose_name="Datum")
    opis           = models.CharField(max_length=500, verbose_name="Opis")
    dokument_broj  = models.CharField(max_length=50, blank=True, verbose_name="Broj dokumenta")
    kreirao = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Kreirao")
    kreirano       = models.DateTimeField(auto_now_add=True)
    izmijenjeno    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-datum', '-kreirano']
        unique_together = ('glavna_knjiga', 'broj_naloga')
        verbose_name = "Knjiženje"
        verbose_name_plural = "Knjiženja"

    def __str__(self):
        return f"{self.datum} | {self.dokument_broj} — {self.opis}"

    @property
    def ukupno_duguje(self):
        return sum(s.duguje for s in self.stavke.all())

    @property
    def ukupno_potrazuje(self):
        return sum(s.potrazuje for s in self.stavke.all())

    @property
    def je_uravnotezeno(self):
        return self.ukupno_duguje == self.ukupno_potrazuje


class StavkaKnjizenja(models.Model):
    knjizenje  = models.ForeignKey(Knjizenje, on_delete=models.CASCADE, related_name='stavke', verbose_name="Knjiženje")
    konto      = models.ForeignKey(Konto, on_delete=models.PROTECT, verbose_name="Konto")
    opis       = models.CharField(max_length=255, blank=True, verbose_name="Opis stavke")
    duguje     = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))], verbose_name="Duguje")
    potrazuje  = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))], verbose_name="Potražuje")

    class Meta:
        verbose_name = "Stavka knjiženja"
        verbose_name_plural = "Stavke knjiženja"

    def __str__(self):
        return f"{self.konto} | D: {self.duguje} P: {self.potrazuje}"

# ─────────────────────────────────────────
#  PRENOS STANJA
# ─────────────────────────────────────────

class SaldoKonta(models.Model):
    """Zaključni saldo po kontu i partneru za određenu godinu."""
    glavna_knjiga  = models.ForeignKey(GlavnaKnjiga, on_delete=models.PROTECT, related_name='salda', verbose_name="Glavna knjiga")
    konto          = models.ForeignKey(Konto, on_delete=models.PROTECT, verbose_name="Konto")
    partner        = models.ForeignKey(PoslovniPartner, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Partner")
    duguje         = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Duguje")
    potrazuje      = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Potražuje")
    saldo          = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Saldo")
    preneseno      = models.BooleanField(default=False, verbose_name="Preneseno u novu godinu")
    datum_prenosa  = models.DateTimeField(null=True, blank=True, verbose_name="Datum prenosa")

    class Meta:
        unique_together = ('glavna_knjiga', 'konto', 'partner')
        ordering = ['konto__broj']
        verbose_name = "Saldo konta"
        verbose_name_plural = "Salda konta"

    def __str__(self):
        return f"{self.konto} | {self.glavna_knjiga} | Saldo: {self.saldo}"


class PrenosStanja(models.Model):
    """Log prenosa stanja iz jedne godine u drugu."""
    STATUS_CHOICES = [
        ('priprema',  'U pripremi'),
        ('izvrseno',  'Izvršeno'),
        ('greska',    'Greška'),
    ]

    iz_godine      = models.ForeignKey(PoslovnaGodina, on_delete=models.PROTECT, related_name='prenosi_iz', verbose_name="Iz godine")
    u_godinu       = models.ForeignKey(PoslovnaGodina, on_delete=models.PROTECT, related_name='prenosi_u', verbose_name="U godinu")
    partner        = models.ForeignKey(PoslovniPartner, on_delete=models.PROTECT, verbose_name="Partner")
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='priprema', verbose_name="Status")
    knjizenje      = models.ForeignKey('Knjizenje', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Knjiženje prenosa")
    broj_stavki    = models.IntegerField(default=0, verbose_name="Broj prenesenih stavki")
    kreirao        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Kreirao")
    kreirano       = models.DateTimeField(auto_now_add=True)
    napomena       = models.TextField(blank=True, verbose_name="Napomena")

    class Meta:
        ordering = ['-kreirano']
        verbose_name = "Prenos stanja"
        verbose_name_plural = "Prenosi stanja"

    def __str__(self):
        return f"Prenos {self.partner} | {self.iz_godine} → {self.u_godinu}"


# ─────────────────────────────────────────
#  INVENTURA
# ─────────────────────────────────────────

class Inventura(models.Model):
    STATUS_CHOICES = [
        ('otvorena',    'Otvorena'),
        ('u_toku',      'U toku'),
        ('zakljucena',  'Zaključena'),
    ]

    glavna_knjiga  = models.ForeignKey(GlavnaKnjiga, on_delete=models.PROTECT, related_name='inventure', verbose_name="Glavna knjiga")
    naziv          = models.CharField(max_length=255, verbose_name="Naziv inventure")
    datum          = models.DateField(verbose_name="Datum inventure")
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='otvorena', verbose_name="Status")
    napomena       = models.TextField(blank=True, verbose_name="Napomena")
    kreirao = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Kreirao")
    kreirano       = models.DateTimeField(auto_now_add=True)
    zakljucena_u   = models.DateTimeField(null=True, blank=True, verbose_name="Zaključena u")

    class Meta:
        ordering = ['-datum']
        verbose_name = "Inventura"
        verbose_name_plural = "Inventure"

    def __str__(self):
        return f"{self.naziv} — {self.datum}"

    @property
    def ukupni_visak(self):
        return sum(s.vrijednost_viska for s in self.stavke.all())

    @property
    def ukupni_manjak(self):
        return sum(s.vrijednost_manjka for s in self.stavke.all())


class StavkaInventure(models.Model):
    inventura        = models.ForeignKey(Inventura, on_delete=models.CASCADE, related_name='stavke', verbose_name="Inventura")
    artikal          = models.ForeignKey(Artikal, on_delete=models.PROTECT, verbose_name="Artikal")

    # Knjigvodstveno stanje
    kolicina_knjig   = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="Količina po knjizi")
    cijena_knjig     = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Cijena po knjizi")

    # Stvarno stanje (popis)
    kolicina_popis   = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="Količina po popisu")
    cijena_popis     = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Cijena po popisu")

    napomena         = models.CharField(max_length=255, blank=True, verbose_name="Napomena")

    class Meta:
        unique_together = ('inventura', 'artikal')
        ordering = ['artikal__sifra']
        verbose_name = "Stavka inventure"
        verbose_name_plural = "Stavke inventure"

    def __str__(self):
        return f"{self.artikal} | Knjiga: {self.kolicina_knjig} | Popis: {self.kolicina_popis}"

    @property
    def razlika_kolicine(self):
        return self.kolicina_popis - self.kolicina_knjig

    @property
    def vrijednost_viska(self):
        razlika = self.razlika_kolicine
        return razlika * self.cijena_popis if razlika > 0 else 0

    @property
    def vrijednost_manjka(self):
        razlika = self.razlika_kolicine
        return abs(razlika * self.cijena_popis) if razlika < 0 else 0

class SintetickiKonto(models.Model):
    glavna_knjiga = models.ForeignKey(GlavnaKnjiga, on_delete=models.CASCADE, related_name='sinteticki_konti', verbose_name="Glavna knjiga")
    konto         = models.ForeignKey(Konto, on_delete=models.PROTECT, verbose_name="Konto")
    naziv         = models.CharField(max_length=255, verbose_name="Naziv")
    aktivan       = models.BooleanField(default=True, verbose_name="Aktivan")
    kreiran       = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('glavna_knjiga', 'konto')
        ordering = ['konto__broj']
        verbose_name = "Sintetički konto"
        verbose_name_plural = "Sintetički konti"

    def __str__(self):
        return f"{self.konto.broj} — {self.naziv}"


class AnalitickiKonto(models.Model):
    glavna_knjiga    = models.ForeignKey(GlavnaKnjiga, on_delete=models.CASCADE, related_name='analiticki_konti', verbose_name="Glavna knjiga")
    sinteticki_konto = models.ForeignKey(SintetickiKonto, on_delete=models.CASCADE, related_name='analitika', verbose_name="Sintetički konto", null=True, blank=True)
    sifra            = models.CharField(max_length=20, verbose_name="Šifra")
    naziv            = models.CharField(max_length=255, verbose_name="Naziv")
    partner          = models.ForeignKey(PoslovniPartner, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Partner")
    aktivan          = models.BooleanField(default=True, verbose_name="Aktivan")
    kreiran          = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('glavna_knjiga', 'sifra')
        ordering = ['sifra']
        verbose_name = "Analitički konto"
        verbose_name_plural = "Analitički konti"

    def __str__(self):
        return f"{self.sifra} — {self.naziv}"

# ─────────────────────────────────────────
#  KALKULACIJA (MALOPRODAJA)
# ─────────────────────────────────────────

class Kalkulacija(models.Model):
    STATUS_CHOICES = [
        ('otvorena',    'Otvorena'),
        ('zakljucena',  'Zaključena'),
    ]

    partner           = models.ForeignKey(PoslovniPartner, on_delete=models.PROTECT, related_name='kalkulacije', verbose_name="Firma/Partner")
    godina            = models.ForeignKey(PoslovnaGodina, on_delete=models.PROTECT, verbose_name="Godina")
    primalac          = models.CharField(max_length=100, blank=True, verbose_name="Primalac")
    broj_prij_lista   = models.CharField(max_length=50, blank=True, verbose_name="Broj prijemnog lista")
    datum_prij_lista  = models.DateField(null=True, blank=True, verbose_name="Datum prijemnog lista")
    dobavljac         = models.ForeignKey(PoslovniPartner, on_delete=models.SET_NULL, null=True, blank=True, related_name='kalkulacije_dobavljac', verbose_name="Dobavljač")
    dokument          = models.CharField(max_length=100, blank=True, verbose_name="Dokument")
    datum_dokumenta   = models.DateField(null=True, blank=True, verbose_name="Datum dokumenta")
    datum_dospijeca   = models.DateField(null=True, blank=True, verbose_name="Datum dospijeća")
    datum_prijema     = models.DateField(null=True, blank=True, verbose_name="Datum prijema")
    knjiga            = models.CharField(max_length=10, default='01', verbose_name="Knjiga")
    kuf               = models.CharField(max_length=50, blank=True, verbose_name="KUF")
    iznos_racuna      = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="Iznos računa")
    iznos_pdv         = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="Iznos PDV-a")
    pdv_za_odbiti     = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="PDV za odbiti")
    pdv_ne_odbiti     = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="PDV ne odbiti")
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='otvorena', verbose_name="Status")
    kreirao           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Kreirao")
    kreirano          = models.DateTimeField(auto_now_add=True)
    izmijenjeno       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-kreirano']
        verbose_name = "Kalkulacija"
        verbose_name_plural = "Kalkulacije"

    def __str__(self):
        return f"Kalk. {self.broj_prij_lista} — {self.partner.naziv_1}"

    @property
    def ukupno_nabavna(self):
        return sum(s.nabavna_vrijednost for s in self.stavke.all())

    @property
    def ukupno_mpc(self):
        return sum(s.mpc_vrijednost for s in self.stavke.all())

    @property
    def ukupno_marza(self):
        return sum(s.marza_vrijednost for s in self.stavke.all())


class StavkaKalkulacije(models.Model):
    kalkulacija      = models.ForeignKey(Kalkulacija, on_delete=models.CASCADE, related_name='stavke', verbose_name="Kalkulacija")
    porezna_grupa    = models.CharField(max_length=20, blank=True, verbose_name="Porezna grupa")
    naziv_artikla    = models.CharField(max_length=255, verbose_name="Naziv artikla")
    jedinica_mjere   = models.CharField(max_length=20, blank=True, verbose_name="Jedinica mjere")
    kolicina         = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="Količina")
    fakturna_cijena  = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="Fakturna cijena")
    nabavna_cijena   = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="Nabavna cijena")
    marza_postotak   = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Marža %")
    marza_vrijednost = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="Marža vrijednost")
    porez            = models.CharField(max_length=10, default='P', verbose_name="Porez")
    mpc              = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="MPC")

    class Meta:
        verbose_name = "Stavka kalkulacije"
        verbose_name_plural = "Stavke kalkulacije"

    def __str__(self):
        return f"{self.naziv_artikla} | {self.kolicina} x {self.fakturna_cijena}"

    @property
    def nabavna_vrijednost(self):
        return self.nabavna_cijena * self.kolicina

    @property
    def mpc_vrijednost(self):
        return self.mpc * self.kolicina