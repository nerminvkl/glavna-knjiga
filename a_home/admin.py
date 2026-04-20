from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import *


# ─────────────────────────────────────────
#  ŠIFARNICI
# ─────────────────────────────────────────

@admin.register(PoslovnaGodina)
class PoslovnaGodinaAdmin(admin.ModelAdmin):
    list_display = ('godina', 'aktivna', 'kreirana')
    list_filter = ('aktivna',)
    search_fields = ('godina',)
    ordering = ('-godina',)


@admin.register(PoslovniPartner)
class PoslovniPartnerAdmin(admin.ModelAdmin):
    list_display = ('sifra', 'naziv_1', 'mjesto', 'telefon', 'entitet', 'aktivan')
    list_filter = ('aktivan', 'entitet', 'u_sustavu_pdv')
    search_fields = ('sifra', 'naziv_1', 'naziv_2', 'mjesto', 'porezni_broj')


@admin.register(Porez)
class PorezAdmin(admin.ModelAdmin):
    list_display = ('naziv', 'stopa', 'aktivan')
    list_filter = ('aktivan',)
    search_fields = ('naziv',)  


@admin.register(GrupaArtikla)
class GrupaArtiklaAdmin(admin.ModelAdmin):
    list_display = ('sifra', 'naziv')
    search_fields = ('sifra', 'naziv')


@admin.register(JedinicaMjere)
class JedinicaMjereAdmin(admin.ModelAdmin):
    list_display = ('sifra', 'naziv')
    search_fields = ('sifra', 'naziv')  


@admin.register(Artikal)
class ArtikalAdmin(admin.ModelAdmin):
    list_display = ('sifra', 'naziv', 'grupa', 'cijena', 'porez', 'aktivan')
    list_filter = ('aktivan', 'grupa', 'porez')
    search_fields = ('sifra', 'naziv')
    autocomplete_fields = ('grupa', 'jedinica_mjere', 'porez')


# ─────────────────────────────────────────
#  KONTNI PLAN
# ─────────────────────────────────────────

@admin.register(Konto)
class KontoAdmin(admin.ModelAdmin):
    list_display = ('broj', 'naziv', 'tip', 'aktivan')
    list_filter = ('tip', 'aktivan')
    search_fields = ('broj', 'naziv')


# ─────────────────────────────────────────
#  GLAVNA KNJIGA
# ─────────────────────────────────────────

class StavkaKnjizenjaInline(admin.TabularInline):
    model = StavkaKnjizenja
    extra = 1
    autocomplete_fields = ('konto',)


@admin.register(GlavnaKnjiga)
class GlavnaKnjigaAdmin(admin.ModelAdmin):
    list_display = ('partner', 'godina', 'zakljucena', 'kreirana')
    list_filter = ('zakljucena', 'godina')
    autocomplete_fields = ('partner', 'godina')
    search_fields = ('partner__naziv_1', 'godina__godina')  


@admin.register(Knjizenje)
class KnjizenjeAdmin(admin.ModelAdmin):
    list_display = (
        'datum',
        'glavna_knjiga',
        'dokument_broj',
        'ukupno_duguje',
        'ukupno_potrazuje',
        'je_uravnotezeno'
    )
    list_filter = ('datum', 'glavna_knjiga__godina')
    search_fields = ('opis', 'dokument_broj')
    autocomplete_fields = ('glavna_knjiga', 'kreirao')
    inlines = [StavkaKnjizenjaInline]

    readonly_fields = (
        'ukupno_duguje',
        'ukupno_potrazuje',
        'je_uravnotezeno',
        'kreirano',
        'izmijenjeno'
    )

    def save_model(self, request, obj, form, change):
        if obj.glavna_knjiga.zakljucena:
            raise ValidationError("Glavna knjiga je zaključena — izmjene nisu dozvoljene.")
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance

        if not obj.je_uravnotezeno:
            raise ValidationError("Knjiženje nije uravnoteženo (duguje ≠ potražuje).")


@admin.register(StavkaKnjizenja)
class StavkaKnjizenjaAdmin(admin.ModelAdmin):
    list_display = ('knjizenje', 'konto', 'duguje', 'potrazuje')
    search_fields = ('konto__naziv', 'knjizenje__opis')
    autocomplete_fields = ('knjizenje', 'konto')


# ─────────────────────────────────────────
#  PRENOS STANJA
# ─────────────────────────────────────────

@admin.register(SaldoKonta)
class SaldoKontaAdmin(admin.ModelAdmin):
    list_display = ('glavna_knjiga', 'konto', 'partner', 'saldo', 'preneseno')
    list_filter = ('preneseno', 'konto')
    search_fields = ('konto__naziv', 'partner__naziv_1')
    autocomplete_fields = ('glavna_knjiga', 'konto', 'partner')


@admin.register(PrenosStanja)
class PrenosStanjaAdmin(admin.ModelAdmin):
    list_display = ('partner', 'iz_godine', 'u_godinu', 'status', 'broj_stavki', 'kreirano')
    list_filter = ('status',)
    search_fields = ('partner__naziv_1',)
    autocomplete_fields = ('partner', 'iz_godine', 'u_godinu', 'knjizenje', 'kreirao')


# ─────────────────────────────────────────
#  INVENTURA
# ─────────────────────────────────────────

class StavkaInventureInline(admin.TabularInline):
    model = StavkaInventure
    extra = 1
    autocomplete_fields = ('artikal',)


@admin.register(Inventura)
class InventuraAdmin(admin.ModelAdmin):
    list_display = ('naziv', 'datum', 'status', 'glavna_knjiga')
    list_filter = ('status', 'datum')
    autocomplete_fields = ('glavna_knjiga', 'kreirao')
    inlines = [StavkaInventureInline]

    search_fields = ('naziv', 'glavna_knjiga__partner__naziv_1') 

    readonly_fields = (
        'ukupni_visak',
        'ukupni_manjak',
        'kreirano',
        'zakljucena_u'
    )


@admin.register(StavkaInventure)
class StavkaInventureAdmin(admin.ModelAdmin):
    list_display = (
        'inventura',
        'artikal',
        'kolicina_knjig',
        'kolicina_popis',
        'razlika_kolicine'
    )
    search_fields = ('artikal__naziv', 'inventura__naziv') 
    autocomplete_fields = ('inventura', 'artikal')

# ─────────────────────────────────────────
#  KALKULACIJA
# ─────────────────────────────────────────

from django.contrib import admin
from .models import Kalkulacija, StavkaKalkulacije

class StavkaKalkulacijeInline(admin.TabularInline):
    model = StavkaKalkulacije
    extra = 0

@admin.register(Kalkulacija)
class KalkulacijaAdmin(admin.ModelAdmin):
    list_display = ['id', 'partner', 'godina', 'broj_prij_lista', 'dobavljac', 'datum_dokumenta', 'iznos_racuna', 'status', 'kreirano']
    list_filter = ['status', 'godina', 'partner']
    search_fields = ['broj_prij_lista', 'dokument', 'partner__naziv_1', 'dobavljac__naziv_1']
    inlines = [StavkaKalkulacijeInline]
    actions = ['obrisi_odabrane']

    def obrisi_odabrane(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'Obrisano {count} kalkulacija.')
    obrisi_odabrane.short_description = 'Obriši odabrane kalkulacije'