"""
URL configuration for _core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from a_home.views import *
from a_users.views import profile_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', logout_view, name='logout'),
    path('accounts/', include('allauth.urls')),
    path('postavke/pozadina/', promijeni_pozadinu, name='promijeni_pozadinu'),
    path('glavna-knjiga/', home_view, name="home"),
    path('glavna-knjiga/<int:partner_id>/', glavna_knjiga_view, name='glavna_knjiga'),
    path('', login_view, name="login"),
    path('profile/', include('a_users.urls')),
    path('@<username>/', profile_view, name="profile"),
    path('knjiga/<int:knjiga_id>/zakljuci/', zakljuci_godinu, name='zakljuci_godinu'),
    path('prenos-stanja/', prenesi_stanje, name='prenesi_stanje'),
    path('inventura/<int:inventura_id>/zakljuci/', zakljuci_inventuru, name='zakljuci_inventuru'),
    path('glavna-knjiga/<int:partner_id>/zaposlenici/print/', print_zaposlenici, name='print_zaposlenici'),

    # Godine
    path('godine/',                godine,        name='godine'),
    path('godine/edit/<int:edit_id>/', godine,    name='godina_edit'),
    path('godine/delete/<int:pk>/',    godina_delete, name='godina_delete'),
    path('glavna-knjiga/<int:partner_id>/partneri-firme/', partneri_firme_view, name='partneri_firme'),

    # Partneri
    path('partneri/',                    partneri,       name='partneri'),
    path('partneri/edit/<int:edit_id>/', partneri,       name='partner_edit'),
    path('partneri/delete/<int:pk>/',    partner_delete, name='partner_delete'),
    path('partneri/<int:pk>/', partner_detalj, name='partner_detalj'),
    path('partneri/search/', partneri_search, name='partneri_search'),

    # Artikli
    path('artikli/',                    artikli,       name='artikli'),
    path('artikli/edit/<int:edit_id>/', artikli,       name='artikal_edit'),
    path('artikli/delete/<int:pk>/',    artikal_delete, name='artikal_delete'),

     # Unos prometa
    path('glavna-knjiga/<int:partner_id>/unos-prometa/', unos_prometa, name='unos_prometa'),
    path('glavna-knjiga/<int:partner_id>/unos-prometa/<int:knjizenje_id>/', unos_prometa, name='unos_prometa_knjizenje'),
    path('knjizenje/<int:knjizenje_id>/dodaj-stavku/', dodaj_stavku, name='dodaj_stavku'),
    path('stavka/<int:stavka_id>/obrisi/', obrisi_stavku, name='obrisi_stavku'),
    path('glavna-knjiga/<int:partner_id>/novo-knjizenje/', novo_knjizenje, name='novo_knjizenje'),
    path('knjizenje/<int:knjizenje_id>/print/', print_knjizenje, name='print_knjizenje'),
    path('glavna-knjiga/<int:partner_id>/nalozi/', nalozi_view, name='nalozi'),
    path('nalog/<int:nalog_id>/obrisi/', obrisi_nalog, name='obrisi_nalog'),

    # Matični podaci - Sintetika i Analitika
    path('glavna-knjiga/<int:partner_id>/sintetika/', sintetika_view, name='sintetika'),
    path('glavna-knjiga/<int:partner_id>/sintetika/edit/<int:edit_id>/', sintetika_view, name='sintetika_edit'),
    path('glavna-knjiga/<int:partner_id>/sintetika/delete/<int:pk>/', sintetika_delete, name='sintetika_delete'),
    path('glavna-knjiga/<int:partner_id>/analitika/', analitika_view, name='analitika'),
    path('glavna-knjiga/<int:partner_id>/analitika/edit/<int:edit_id>/', analitika_view, name='analitika_edit'),
    path('glavna-knjiga/<int:partner_id>/analitika/delete/<int:pk>/', analitika_delete, name='analitika_delete'),
    path('konto/search/', konto_search, name='konto_search'),
    path('glavna-knjiga/<int:partner_id>/kartica/', kartica_view, name='kartica'),
    path('knjizenje/kartica/<int:partner_id>/<int:konto_id>/print/', kartica_print, name='kartica_print'),

    # Kalkulacije
    path('glavna-knjiga/<int:partner_id>/kalkulacije/', kalkulacije_view, name='kalkulacije'),
    path('glavna-knjiga/<int:partner_id>/kalkulacije/nova/', nova_kalkulacija, name='nova_kalkulacija'),
    path('glavna-knjiga/<int:partner_id>/kalkulacije/<int:kalk_id>/', uredi_kalkulaciju, name='uredi_kalkulaciju'),
    path('kalkulacija/<int:kalk_id>/dodaj-stavku/', dodaj_stavku_kalk, name='dodaj_stavku_kalk'),
    path('kalkulacija/stavka/<int:stavka_id>/obrisi/', obrisi_stavku_kalk, name='obrisi_stavku_kalk'),
    path('kalkulacija/<int:kalk_id>/print/', print_kalkulacija, name='print_kalkulacija'),
    path('api/<int:partner_id>/partneri-firme/search/', partneri_firme_search_api, name='partneri_firme_search_api'),
    path('api/artikli/search/', artikli_search_api, name='artikli_search_api'),
    path('kalkulacija/<int:pk>/obrisi/', obrisi_kalkulaciju, name='obrisi_kalkulaciju'),
    path('kalkulacija/<int:kalk_id>/zakljuci/', zakljuci_kalkulaciju, name='zakljuci_kalkulaciju'),
    path('api/<int:partner_id>/partneri-firme/search/', partneri_firme_search, name='partneri_firme_search'),

    # maloprodaja maticni podaci
    path('maloprodaja/grupe-artikala/', grupe_artikala_view, name='grupe_artikala'),
    path('maloprodaja/grupe-artikala/delete/<int:pk>/', grupa_artikala_delete, name='grupa_artikala_delete'),
    path('maloprodaja/porezi/', porezi_view, name='porezi'),
    path('maloprodaja/porezi/delete/<int:pk>/', porez_delete, name='porez_delete'),
    path('glavna-knjiga/<int:partner_id>/bruto-bilanca/', bruto_bilanca_view, name='bruto_bilanca'),
    path('glavna-knjiga/<int:partner_id>/bruto-bilanca/print/', bruto_bilanca_print, name='bruto_bilanca_print'),
    path('glavna-knjiga/<int:partner_id>/analitika-izvjestaj/', analitika_izvjestaj_view, name='analitika_izvjestaj'),
    path('glavna-knjiga/<int:partner_id>/analitika-izvjestaj/print/', analitika_izvjestaj_print, name='analitika_izvjestaj_print'),

    # inventura linkovi
    path('glavna-knjiga/<int:partner_id>/inventure/', inventure_view, name='inventure'),
    path('glavna-knjiga/<int:partner_id>/inventure/nova/', nova_inventura, name='nova_inventura_gk'),
    path('inventura/<int:inventura_id>/uredi/', uredi_inventuru, name='uredi_inventuru'),
    path('inventura/<int:inventura_id>/obrisi/', obrisi_inventuru, name='obrisi_inventuru_gk'),
    path('inventura/<int:inventura_id>/print/', print_inventura, name='print_inventura'),

    # obracun plata
    path('glavna-knjiga/<int:partner_id>/zaposlenici/', zaposlenici_view, name='zaposlenici'),
    path('zaposlenik/<int:pk>/obrisi/', zaposlenik_delete, name='zaposlenik_delete'),
    path('glavna-knjiga/<int:partner_id>/place/', obracuni_placa_view, name='obracuni_placa'),
    path('glavna-knjiga/<int:partner_id>/place/novi/', novi_obracun_place, name='novi_obracun_place'),
    path('place/<int:obracun_id>/uredi/', uredi_obracun_place, name='uredi_obracun_place'),
    path('place/<int:obracun_id>/obrisi/', obrisi_obracun_place, name='obrisi_obracun_place'),
    path('place/<int:obracun_id>/print/', print_obracun_place, name='print_obracun_place'),
    path('place/<int:obracun_id>/xlsx/', export_obracun_place_xlsx, name='export_obracun_place_xlsx'),
    path('glavna-knjiga/<int:partner_id>/vrste-isplate/', vrste_isplate_view, name='vrste_isplate'),
    path('vrsta-isplate/<int:pk>/obrisi/', vrsta_isplate_delete, name='vrsta_isplate_delete'),
    path('place/<int:obracun_id>/stavka/<int:stavka_id>/platna-lista/', print_platna_lista, name='platna_lista'),

    #mip obrazac
    path('place/<int:obracun_id>/mip/', mip_view, name='mip_obracun'),
    path('place/<int:obracun_id>/mip/xml/', mip_xml, name='mip_xml'),
    path('place/<int:obracun_id>/stavka/<int:stavka_id>/mip/', mip_zaposlenik, name='mip_zaposlenik'),
    path('place/<int:obracun_id>/stavka/<int:stavka_id>/mip/xml/', mip_xml_zaposlenik, name='mip_xml_zaposlenik'),
    path('place/<int:obracun_id>/mip/pdf/', mip_pdf, name='mip_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]