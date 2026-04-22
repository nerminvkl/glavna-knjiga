from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import PoslovniPartner
from django.http import JsonResponse
from django.utils import timezone
from .models import *
import json
from django.db.models import Max

def home_view(request):
    partneri = PoslovniPartner.objects.filter(aktivan=True).order_by('sifra')
    return render(request, 'a_home/home.html', {'partneri': partneri,
     'show_header': False,
     })
    
def get_selected_godina(request):
    godina_id = request.session.get('selected_year')

    if not godina_id:
        godina = PoslovnaGodina.objects.filter(aktivna=True).first()
        if not godina:
            return None
        request.session['selected_year'] = godina.godina
        return godina

    godina = PoslovnaGodina.objects.filter(godina=godina_id).first()

    if not godina:
        godina = PoslovnaGodina.objects.filter(aktivna=True).first()
        if godina:
            request.session['selected_year'] = godina.godina

    return godina

def partneri_search(request):
    q = request.GET.get('q', '').strip()
    print(f"Query: '{q}'")  # <-- debug
    if len(q) < 1:
        return JsonResponse({'results': []})
    
    partneri = PoslovniPartner.objects.filter(
        aktivan=True
    ).filter(
        Q(naziv_1__icontains=q) |
        Q(naziv_2__icontains=q) |
        Q(sifra__icontains=q)
    )[:10]
    
    print(f"Pronađeno: {partneri.count()}")  # <-- debug
    for p in partneri:
        print(f"  -> {p.sifra} {p.naziv_1} aktivan={p.aktivan}")  # <-- debug
    
    results = [
        {'id': p.id, 'sifra': p.sifra, 'naziv': p.naziv_1, 'mjesto': p.mjesto}
        for p in partneri
    ]
    return JsonResponse({'results': results})

from .models import PoslovnaGodina

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    years = PoslovnaGodina.objects.filter(aktivna=True)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        year = request.POST.get('year')

        user = authenticate(request, username=username, password=password)

        if user is not None and year:
            login(request, user)

            request.session['selected_year'] = int(year)

            return redirect('home')

        return render(request, 'login.html', {
            'form': {'errors': True},
            'years': years
        })

    return render(request, 'login.html', {
        'show_header': False,
        'years': years,
    })

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .services import ZakljucivanjeGodineService, InventuraService
from .models import GlavnaKnjiga, PoslovnaGodina, PoslovniPartner


@login_required
def zakljuci_godinu(request, knjiga_id):
    knjiga = get_object_or_404(GlavnaKnjiga, pk=knjiga_id)

    if request.method == 'POST':
        try:
            ZakljucivanjeGodineService.zakljuci_godinu(knjiga, request.user)
            messages.success(request, f"Godina {knjiga.godina} uspješno zaključena.")
        except ValueError as e:
            messages.error(request, str(e))

    return redirect('pregled_knjige', knjiga_id=knjiga_id)


@login_required
def prenesi_stanje(request):
    if request.method == 'POST':
        partner_id   = request.POST.get('partner_id')
        iz_godine_id = request.POST.get('iz_godine_id')
        u_godinu_id  = request.POST.get('u_godinu_id')

        partner    = get_object_or_404(PoslovniPartner, pk=partner_id)
        iz_godine  = get_object_or_404(PoslovnaGodina, pk=iz_godine_id)
        u_godinu   = get_object_or_404(PoslovnaGodina, pk=u_godinu_id)

        try:
            prenos = ZakljucivanjeGodineService.prenesi_stanje(
                partner, iz_godine, u_godinu, request.user
            )
            messages.success(request, f"Preneseno {prenos.broj_stavki} stavki u {u_godinu.godina}. godinu.")
        except ValueError as e:
            messages.error(request, str(e))

    return redirect('dashboard')


@login_required
def zakljuci_inventuru(request, inventura_id):
    from .models import Inventura
    inventura = get_object_or_404(Inventura, pk=inventura_id)

    if request.method == 'POST':
        try:
            InventuraService.zakljuci_inventuru(inventura, request.user)
            messages.success(request, "Inventura uspješno zaključena.")
        except ValueError as e:
            messages.error(request, str(e))

    return redirect('pregled_inventure', inventura_id=inventura_id)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import PoslovnaGodina, PoslovniPartner, Artikal
from .forms import PoslovnaGodinaForm, PoslovniPartnerForm, ArtikalForm


# ── Poslovne godine ──────────────────────────────────

@login_required
def godine(request, edit_id=None):
    instance = get_object_or_404(PoslovnaGodina, pk=edit_id) if edit_id else None
    form = PoslovnaGodinaForm(request.POST or None, instance=instance)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Godina uspješno sačuvana.")
            return redirect('godine')
        else:
            messages.error(request, "Ispravite greške u formi.")

    return render(request, 'a_home/godine.html', {
        'form':        form,
        'lista':       PoslovnaGodina.objects.all(),
        'edit_obj':    instance,
        'show_header': False,   # ← ovo sakriva stari navbar
    })


@login_required
def godina_delete(request, pk):
    obj = get_object_or_404(PoslovnaGodina, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Godina obrisana.")
    return redirect('godine')


# ── Poslovni partneri ────────────────────────────────

@login_required
def partneri(request, edit_id=None):
    instance = get_object_or_404(PoslovniPartner, pk=edit_id) if edit_id else None
    form = PoslovniPartnerForm(request.POST or None, instance=instance)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Partner uspješno sačuvan.")
            return redirect('partneri')
        else:
            messages.error(request, "Ispravite greške u formi.")

    return render(request, 'a_home/partneri.html', {
        'form': form,
        'lista': PoslovniPartner.objects
                    .filter(aktivan=True)
                    .order_by('-kreiran'),
        'show_header': False,
    })


@login_required
def partner_delete(request, pk):
    obj = get_object_or_404(PoslovniPartner, pk=pk)
    if request.method == 'POST':
        obj.aktivan = False
        obj.save()
        messages.success(request, "Partner deaktiviran.")
    return redirect('partneri')

@login_required
def partner_detalj(request, pk):
    partner = get_object_or_404(PoslovniPartner, pk=pk)
    form = PoslovniPartnerForm(request.POST or None, instance=partner)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f"Partner {partner.naziv_1} uspješno ažuriran.")
            return redirect('partner_detalj', pk=pk)
        else:
            messages.error(request, "Ispravite greške u formi.")

    return render(request, 'a_home/partner_detalj.html', {
        'partner':     partner,
        'form':        form,
        'show_header': False,
    })


# ── Artikli ──────────────────────────────────────────

@login_required
def artikli(request, edit_id=None):
    instance = get_object_or_404(Artikal, pk=edit_id) if edit_id else None
    form = ArtikalForm(request.POST or None, instance=instance)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Artikal uspješno sačuvan.")
            return redirect('artikli')
        else:
            messages.error(request, "Ispravite greške u formi.")

    return render(request, 'a_home/artikli.html', {
        'form': form,
        'lista': Artikal.objects
                    .filter(aktivan=True)
                    .order_by('-kreiran'),
        'show_header': False,
    })



@login_required
def artikal_delete(request, pk):
    obj = get_object_or_404(Artikal, pk=pk)
    if request.method == 'POST':
        obj.aktivan = False
        obj.save()
        messages.success(request, "Artikal deaktiviran.")
    return redirect('artikli')

def glavna_knjiga_view(request, partner_id):
    partner = get_object_or_404(PoslovniPartner, id=partner_id, aktivan=True)
    request.session['aktivni_partner_id'] = partner_id
    request.session['aktivni_partner_naziv'] = partner.naziv_1
    return render(request, 'a_home/dashboard.html', {'partner': partner, 'show_header': False,},
    
    )

@login_required
def unos_prometa(request, partner_id, knjizenje_id=None):
    partner = get_object_or_404(PoslovniPartner, id=partner_id, aktivan=True)

    godina = get_selected_godina(request)
    if not godina:
        return redirect('login')

    glavna_knjiga, _ = GlavnaKnjiga.objects.get_or_create(
        partner=partner, godina=godina
    )

    if knjizenje_id:
        knjizenje = get_object_or_404(
            Knjizenje,
            id=knjizenje_id,
            glavna_knjiga=glavna_knjiga
        )
    else:
        knjizenje = Knjizenje.objects.filter(
            glavna_knjiga=glavna_knjiga
        ).order_by('-kreirano').first()

        if not knjizenje:
            knjizenje = Knjizenje.objects.create(
                glavna_knjiga=glavna_knjiga,
                broj_naloga=1,
                datum=timezone.now().date(),
                opis='',
                kreirao=request.user
            )

    stavke = knjizenje.stavke.select_related('konto').all()
    konta = Konto.objects.filter(aktivan=True).order_by('broj')

    return render(request, 'a_home/unos_prometa.html', {
        'partner': partner,
        'knjizenje': knjizenje,
        'stavke': stavke,
        'konta': konta,
        'ukupno_duguje': knjizenje.ukupno_duguje,
        'ukupno_potrazuje': knjizenje.ukupno_potrazuje,
        'razlika': knjizenje.ukupno_duguje - knjizenje.ukupno_potrazuje,
        'show_header': False,
    })

@login_required  
def dodaj_stavku(request, knjizenje_id):
    if request.method == 'POST':
        knjizenje = get_object_or_404(Knjizenje, id=knjizenje_id)
        data = json.loads(request.body)
        
        konto = get_object_or_404(Konto, id=data.get('konto_id'))
        stavka = StavkaKnjizenja.objects.create(
            knjizenje=knjizenje,
            konto=konto,
            opis=data.get('opis', ''),
            duguje=data.get('duguje', 0),
            potrazuje=data.get('potrazuje', 0),
        )
        
        return JsonResponse({
            'success': True,
            'stavka_id': stavka.id,
            'konto_broj': stavka.konto.broj,
            'konto_naziv': stavka.konto.naziv,
            'opis': stavka.opis,
            'duguje': str(stavka.duguje),
            'potrazuje': str(stavka.potrazuje),
            'ukupno_duguje': str(knjizenje.ukupno_duguje),
            'ukupno_potrazuje': str(knjizenje.ukupno_potrazuje),
            'razlika': str(knjizenje.ukupno_duguje - knjizenje.ukupno_potrazuje),
        })
    return JsonResponse({'success': False})

@login_required
def obrisi_stavku(request, stavka_id):
    if request.method == 'POST':
        stavka = get_object_or_404(StavkaKnjizenja, id=stavka_id)
        knjizenje = stavka.knjizenje
        stavka.delete()
        return JsonResponse({
            'success': True,
            'ukupno_duguje': str(knjizenje.ukupno_duguje),
            'ukupno_potrazuje': str(knjizenje.ukupno_potrazuje),
            'razlika': str(knjizenje.ukupno_duguje - knjizenje.ukupno_potrazuje),
        })
    return JsonResponse({'success': False})

@login_required
def novo_knjizenje(request, partner_id):
    if request.method == 'POST':
        partner = get_object_or_404(PoslovniPartner, id=partner_id)
        godina_id = request.session.get('selected_year')
        godina = get_object_or_404(PoslovnaGodina, godina=godina_id)
        glavna_knjiga, _ = GlavnaKnjiga.objects.get_or_create(partner=partner, godina=godina)

        zadnji = Knjizenje.objects.filter(
            glavna_knjiga=glavna_knjiga
        ).aggregate(max_broj=Max('broj_naloga'))['max_broj'] or 0
        
        knjizenje = Knjizenje.objects.create(
            glavna_knjiga=glavna_knjiga,
            broj_naloga=zadnji + 1,
            datum=timezone.now().date(),
            opis=request.POST.get('opis', ''),          # prazan string ako nije unesen
            dokument_broj=request.POST.get('dokument_broj', ''),  # isto
            kreirao=request.user
        )
        return redirect('unos_prometa_knjizenje', partner_id=partner_id, knjizenje_id=knjizenje.id)
    return redirect('unos_prometa', partner_id=partner_id)

@login_required
def print_knjizenje(request, knjizenje_id):
    knjizenje = get_object_or_404(Knjizenje, id=knjizenje_id)
    partner = knjizenje.glavna_knjiga.partner
    godina = knjizenje.glavna_knjiga.godina
    stavke = knjizenje.stavke.select_related('konto').all()
    
    return render(request, 'a_home/print_nalog.html', {
        'knjizenje': knjizenje,
        'partner': partner,
        'godina': godina,
        'stavke': stavke,
        'ukupno_duguje': knjizenje.ukupno_duguje,
        'ukupno_potrazuje': knjizenje.ukupno_potrazuje,
        'razlika': knjizenje.ukupno_duguje - knjizenje.ukupno_potrazuje,
    })

from .models import SintetickiKonto, AnalitickiKonto

@login_required
def sintetika_view(request, partner_id, edit_id=None):
    partner = get_object_or_404(PoslovniPartner, id=partner_id)
    godina_id = request.session.get('selected_year')
    godina = get_object_or_404(PoslovnaGodina, godina=godina_id)
    glavna_knjiga, _ = GlavnaKnjiga.objects.get_or_create(partner=partner, godina=godina)

    edit_obj = None
    if edit_id:
        edit_obj = get_object_or_404(SintetickiKonto, id=edit_id, glavna_knjiga=glavna_knjiga)

    if request.method == 'POST':
        konto_id = request.POST.get('konto')
        naziv = request.POST.get('naziv', '').strip()
        aktivan = request.POST.get('aktivan') == 'on'

        if konto_id and naziv:
            konto = get_object_or_404(Konto, id=konto_id)
            if edit_obj:
                edit_obj.konto = konto
                edit_obj.naziv = naziv
                edit_obj.aktivan = aktivan
                edit_obj.save()
            else:
                SintetickiKonto.objects.get_or_create(
                    glavna_knjiga=glavna_knjiga,
                    konto=konto,
                    defaults={'naziv': naziv, 'aktivan': aktivan}
                )
        return redirect('sintetika', partner_id=partner_id)

    lista = SintetickiKonto.objects.filter(glavna_knjiga=glavna_knjiga).select_related('konto')
    konta = Konto.objects.filter(aktivan=True).order_by('broj')

    return render(request, 'gk/sintetika.html', {
        'partner': partner,
        'edit_obj': edit_obj,
        'lista': lista,
        'konta': konta,
        'show_header': False,
    })

@login_required
def sintetika_delete(request, partner_id, pk):
    obj = get_object_or_404(SintetickiKonto, id=pk)
    obj.delete()
    return redirect('sintetika', partner_id=partner_id)

@login_required
def analitika_view(request, partner_id, edit_id=None):
    partner = get_object_or_404(PoslovniPartner, id=partner_id)
    godina_id = request.session.get('selected_year')
    godina = get_object_or_404(PoslovnaGodina, godina=godina_id)
    glavna_knjiga, _ = GlavnaKnjiga.objects.get_or_create(partner=partner, godina=godina)

    edit_obj = None
    if edit_id:
        edit_obj = get_object_or_404(AnalitickiKonto, id=edit_id, glavna_knjiga=glavna_knjiga)

    if request.method == 'POST':
        sifra = request.POST.get('sifra', '').strip()
        naziv = request.POST.get('naziv', '').strip()
        sinteticki_id = request.POST.get('sinteticki_konto')
        partner_fk_id = request.POST.get('partner')
        aktivan = request.POST.get('aktivan') == 'on'

        if sifra and naziv:
            sinteticki = SintetickiKonto.objects.filter(id=sinteticki_id).first() if sinteticki_id else None
            partner_fk = PoslovniPartner.objects.filter(id=partner_fk_id).first() if partner_fk_id else None

            if edit_obj:
                edit_obj.sifra = sifra
                edit_obj.naziv = naziv
                edit_obj.sinteticki_konto = sinteticki
                edit_obj.partner = partner_fk
                edit_obj.aktivan = aktivan
                edit_obj.save()
            else:
                AnalitickiKonto.objects.create(
                    glavna_knjiga=glavna_knjiga,
                    sifra=sifra,
                    naziv=naziv,
                    sinteticki_konto=sinteticki,
                    partner=partner_fk,
                    aktivan=aktivan,
                )
        return redirect('analitika', partner_id=partner_id)

    lista = AnalitickiKonto.objects.filter(glavna_knjiga=glavna_knjiga).select_related('sinteticki_konto', 'partner')
    sinteticki_konti = SintetickiKonto.objects.filter(glavna_knjiga=glavna_knjiga)
    svi_partneri = PoslovniPartner.objects.filter(aktivan=True)

    return render(request, 'gk/analitika.html', {
        'partner': partner,
        'edit_obj': edit_obj,
        'lista': lista,
        'sinteticki_konti': sinteticki_konti,
        'svi_partneri': svi_partneri,
        'show_header': False,
    })

@login_required
def analitika_delete(request, partner_id, pk):
    obj = get_object_or_404(AnalitickiKonto, id=pk)
    obj.delete()
    return redirect('analitika', partner_id=partner_id)

def konto_search(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 1:
        return JsonResponse({'results': []})
    konta = Konto.objects.filter(
        aktivan=True
    ).filter(
        Q(broj__startswith=q) | Q(naziv__icontains=q)
    )[:15]
    return JsonResponse({'results': [{'id': k.id, 'broj': k.broj, 'naziv': k.naziv} for k in konta]})

@login_required
def kartica_view(request, partner_id):
    partner = get_object_or_404(PoslovniPartner, id=partner_id)
    godina_id = request.session.get('selected_year')
    godina = get_object_or_404(PoslovnaGodina, godina=godina_id)
    glavna_knjiga = GlavnaKnjiga.objects.filter(partner=partner, godina=godina).first()

    konta = Konto.objects.filter(aktivan=True).order_by('broj')
    stavke = None
    odabrani_konto = None
    ukupno_duguje = 0
    ukupno_potrazuje = 0
    saldo = 0

    konto_id = request.GET.get('konto')
    if konto_id and glavna_knjiga:
        odabrani_konto = get_object_or_404(Konto, id=konto_id)
        stavke = StavkaKnjizenja.objects.filter(
            knjizenje__glavna_knjiga=glavna_knjiga,
            konto=odabrani_konto
        ).select_related('knjizenje').order_by('knjizenje__datum', 'knjizenje__id')

        ukupno_duguje = sum(s.duguje for s in stavke)
        ukupno_potrazuje = sum(s.potrazuje for s in stavke)
        saldo = ukupno_duguje - ukupno_potrazuje

    return render(request, 'a_home/kartica.html', {
        'partner': partner,
        'konta': konta,
        'stavke': stavke,
        'odabrani_konto': odabrani_konto,
        'ukupno_duguje': ukupno_duguje,
        'ukupno_potrazuje': ukupno_potrazuje,
        'saldo': saldo,
        'godina': godina,
        'show_header': False,
    })

@login_required
def kartica_print(request, partner_id, konto_id):
    partner = get_object_or_404(PoslovniPartner, id=partner_id)
    godina_id = request.session.get('selected_year')
    godina = get_object_or_404(PoslovnaGodina, godina=godina_id)
    glavna_knjiga = get_object_or_404(GlavnaKnjiga, partner=partner, godina=godina)
    konto = get_object_or_404(Konto, id=konto_id)

    stavke = StavkaKnjizenja.objects.filter(
        knjizenje__glavna_knjiga=glavna_knjiga,
        konto=konto
    ).select_related('knjizenje').order_by('knjizenje__datum', 'knjizenje__id')

    ukupno_duguje = sum(s.duguje for s in stavke)
    ukupno_potrazuje = sum(s.potrazuje for s in stavke)
    saldo = ukupno_duguje - ukupno_potrazuje

    return render(request, 'a_home/kartica_print.html', {
        'partner': partner,
        'godina': godina,
        'konto': konto,
        'stavke': stavke,
        'ukupno_duguje': ukupno_duguje,
        'ukupno_potrazuje': ukupno_potrazuje,
        'saldo': saldo,
    })

from .models import Kalkulacija, StavkaKalkulacije
import json

@login_required
def kalkulacije_view(request, partner_id):
    partner = get_object_or_404(PoslovniPartner, id=partner_id)
    godina_id = request.session.get('selected_year')
    godina = get_object_or_404(PoslovnaGodina, godina=godina_id)
    lista = Kalkulacija.objects.filter(partner=partner, godina=godina).order_by('-kreirano')
    return render(request, 'maloprodaja/kalkulacije.html', {
        'partner': partner,
        'lista': lista,
        'godina': godina,
        'show_header': False,
    })

@login_required
def nova_kalkulacija(request, partner_id):
    partner = get_object_or_404(PoslovniPartner, id=partner_id)
    godina_id = request.session.get('selected_year')
    godina = get_object_or_404(PoslovnaGodina, godina=godina_id)
    dobavljaci = PoslovniPartner.objects.filter(aktivan=True).order_by('naziv_1')

    if request.method == 'POST':
        kalk = Kalkulacija.objects.create(
            partner=partner,
            godina=godina,
            primalac=request.POST.get('primalac', ''),
            broj_prij_lista=request.POST.get('broj_prij_lista', ''),
            datum_prij_lista=request.POST.get('datum_prij_lista') or None,
            dobavljac_id=request.POST.get('dobavljac') or None,
            dokument=request.POST.get('dokument', ''),
            datum_dokumenta=request.POST.get('datum_dokumenta') or None,
            datum_dospijeca=request.POST.get('datum_dospijeca') or None,
            datum_prijema=request.POST.get('datum_prijema') or None,
            knjiga=request.POST.get('knjiga', '01'),
            kuf=request.POST.get('kuf', ''),
            iznos_racuna=request.POST.get('iznos_racuna') or 0,
            iznos_pdv=request.POST.get('iznos_pdv') or 0,
            pdv_za_odbiti=request.POST.get('pdv_za_odbiti') or 0,
            pdv_ne_odbiti=request.POST.get('pdv_ne_odbiti') or 0,
            kreirao=request.user,
        )
        return redirect('uredi_kalkulaciju', partner_id=partner_id, kalk_id=kalk.id)

    return render(request, 'maloprodaja/nova_kalkulacija.html', {
        'partner': partner,
        'dobavljaci': dobavljaci,
        'danas': timezone.now().date(),
        'show_header': False,
    })

@login_required
def uredi_kalkulaciju(request, partner_id, kalk_id):
    partner = get_object_or_404(PoslovniPartner, id=partner_id)
    kalk = get_object_or_404(Kalkulacija, id=kalk_id, partner=partner)
    stavke = kalk.stavke.all()
    porezi = Porez.objects.filter(aktivan=True)  # ← dodano

    return render(request, 'maloprodaja/uredi_kalkulaciju.html', {
        'partner': partner,
        'kalk': kalk,
        'stavke': stavke,
        'porezi': porezi,
        'ukupno_nabavna': kalk.ukupno_nabavna,
        'ukupno_mpc': kalk.ukupno_mpc,
        'ukupno_marza': kalk.ukupno_marza,
        'show_header': False,
    })

@login_required
def dodaj_stavku_kalk(request, kalk_id):
    if request.method == 'POST':
        kalk = get_object_or_404(Kalkulacija, id=kalk_id)
        data = json.loads(request.body)

        fakturna = Decimal(str(data.get('fakturna_cijena', 0)))
        nabavna = Decimal(str(data.get('nabavna_cijena', 0)))
        kolicina = Decimal(str(data.get('kolicina', 1)))
        mpc = Decimal(str(data.get('mpc', 0)))

        marza_v = mpc * kolicina - nabavna * kolicina
        marza_p = (marza_v / (nabavna * kolicina) * 100) if nabavna * kolicina > 0 else Decimal('0')

        stavka = StavkaKalkulacije.objects.create(
            kalkulacija=kalk,
            porezna_grupa=data.get('porezna_grupa', ''),
            naziv_artikla=data.get('naziv_artikla', ''),
            jedinica_mjere=data.get('jedinica_mjere', ''),
            kolicina=kolicina,
            fakturna_cijena=fakturna,
            nabavna_cijena=nabavna,
            marza_postotak=marza_p.quantize(Decimal('0.01')),
            marza_vrijednost=marza_v.quantize(Decimal('0.001')),
            porez=data.get('porez', 'P'),
            mpc=mpc,
        )

        return JsonResponse({
            'success': True,
            'stavka_id': stavka.id,
            'porezna_grupa': stavka.porezna_grupa,
            'naziv_artikla': stavka.naziv_artikla,
            'jedinica_mjere': stavka.jedinica_mjere,
            'kolicina': str(stavka.kolicina),
            'fakturna_cijena': str(stavka.fakturna_cijena),
            'nabavna_cijena': str(stavka.nabavna_cijena),
            'marza_postotak': str(stavka.marza_postotak),
            'marza_vrijednost': str(stavka.marza_vrijednost),
            'porez': stavka.porez,
            'mpc': str(stavka.mpc),
            'ukupno_nabavna': str(kalk.ukupno_nabavna),
            'ukupno_mpc': str(kalk.ukupno_mpc),
            'ukupno_marza': str(kalk.ukupno_marza),
            'show_header': False,
        })
    return JsonResponse({'success': False})

@login_required
def obrisi_stavku_kalk(request, stavka_id):
    if request.method == 'POST':
        stavka = get_object_or_404(StavkaKalkulacije, id=stavka_id)
        kalk = stavka.kalkulacija
        stavka.delete()
        return JsonResponse({
            'success': True,
            'ukupno_nabavna': str(kalk.ukupno_nabavna),
            'ukupno_mpc': str(kalk.ukupno_mpc),
            'ukupno_marza': str(kalk.ukupno_marza),
            'show_header': False,
        })
    return JsonResponse({'success': False})

@login_required
def print_kalkulacija(request, kalk_id):
    kalk = get_object_or_404(Kalkulacija, id=kalk_id)
    stavke = kalk.stavke.all()
    return render(request, 'maloprodaja/print_kalkulacija.html', {
        'kalk': kalk,
        'stavke': stavke,
        'partner': kalk.partner,
        'ukupno_nabavna': kalk.ukupno_nabavna,
        'ukupno_mpc': kalk.ukupno_mpc,
        'ukupno_marza': kalk.ukupno_marza,
        'show_header': False,
    })

def partneri_search_api(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 1:
        return JsonResponse({'results': []})
    partneri = PoslovniPartner.objects.filter(
        aktivan=True
    ).filter(
        Q(naziv_1__icontains=q) | Q(sifra__icontains=q)
    )[:10]
    return JsonResponse({'results': [
        {'id': p.id, 'sifra': p.sifra, 'naziv': p.naziv_1, 'mjesto': p.mjesto}
        for p in partneri
    ]})

def artikli_search_api(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 1:
        return JsonResponse({'results': []})
    artikli = Artikal.objects.filter(
        aktivan=True
    ).filter(
        Q(naziv__icontains=q) | Q(sifra__icontains=q)
    ).select_related('jedinica_mjere', 'porez', 'grupa')[:15]
    return JsonResponse({'results': [
        {
            'id': a.id,
            'sifra': a.sifra,
            'naziv': a.naziv,
            'jm': a.jedinica_mjere.sifra if a.jedinica_mjere else '',
            'cijena': str(a.cijena),
            'porez': a.porez.naziv if a.porez else 'P',
            'grupa': a.grupa.sifra if a.grupa else '',
        }
        for a in artikli
    ]})

@login_required
def zakljuci_kalkulaciju(request, kalk_id):
    kalk = get_object_or_404(Kalkulacija, id=kalk_id)
    partner_id = kalk.partner.id
    if request.method == 'POST':
        kalk.status = 'zakljucena'
        kalk.save()
    return redirect('nova_kalkulacija', partner_id=partner_id)


@login_required
def obrisi_kalkulaciju(request, pk):
    kalk = get_object_or_404(Kalkulacija, id=pk)
    partner_id = kalk.partner.id
    if request.method == 'POST':
        kalk.delete()
    return redirect('kalkulacije', partner_id=partner_id)
