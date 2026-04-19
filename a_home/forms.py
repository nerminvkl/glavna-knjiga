from django import forms
from .models import PoslovnaGodina, PoslovniPartner, Artikal, GrupaArtikla, JedinicaMjere, Porez


class PoslovnaGodinaForm(forms.ModelForm):
    class Meta:
        model = PoslovnaGodina
        fields = ['godina', 'aktivna', 'napomena']
        widgets = {
            'godina':   forms.NumberInput(attrs={'placeholder': 'npr. 2025'}),
            'napomena': forms.TextInput(attrs={'placeholder': 'Opcionalna napomena'}),
        }


class PoslovniPartnerForm(forms.ModelForm):
    class Meta:
        model = PoslovniPartner
        exclude = ['kreiran', 'izmijenjen']
        widgets = {
            'sifra':               forms.TextInput(attrs={'placeholder': 'npr. 00001'}),
            'naziv_1':             forms.TextInput(attrs={'placeholder': 'Puni naziv firme'}),
            'naziv_2':             forms.TextInput(attrs={'placeholder': 'Nastavak naziva'}),
            'ptt':                 forms.TextInput(attrs={'placeholder': 'npr. 77230'}),
            'mjesto':              forms.TextInput(attrs={'placeholder': 'npr. Velika Kladuša'}),
            'ulica':               forms.TextInput(attrs={'placeholder': 'Ulica i broj'}),
            'telefon':             forms.TextInput(attrs={'placeholder': '+387 37 ...'}),
            'fax':                 forms.TextInput(attrs={'placeholder': 'Fax broj'}),
            'ziro_racun':          forms.TextInput(attrs={'placeholder': '1234567890123456'}),
            'sifra_sjedista':      forms.TextInput(attrs={'placeholder': 'Šifra sjedišta'}),
            'sinteticki_konto':    forms.TextInput(attrs={'placeholder': 'npr. 2000'}),
            'maticni_broj':        forms.TextInput(attrs={'placeholder': 'Matični broj'}),
            'porezni_broj':        forms.TextInput(attrs={'placeholder': 'Porezni/JIB broj'}),
            'broj_upisa_sud_reg':  forms.TextInput(attrs={'placeholder': 'Broj upisa u sud. reg.'}),
        }


class ArtikalForm(forms.ModelForm):
    class Meta:
        model = Artikal
        exclude = ['kreiran', 'izmijenjen']
        widgets = {
            'sifra':  forms.TextInput(attrs={'placeholder': 'npr. ART-001'}),
            'naziv':  forms.TextInput(attrs={'placeholder': 'Naziv artikla'}),
            'cijena': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
        }