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
    # Godine
    path('godine/',                godine,        name='godine'),
    path('godine/edit/<int:edit_id>/', godine,    name='godina_edit'),
    path('godine/delete/<int:pk>/',    godina_delete, name='godina_delete'),

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
    path('api/partneri/search/', partneri_search_api, name='partneri_search_api'),
    path('api/artikli/search/', artikli_search_api, name='artikli_search_api'),
    path('kalkulacija/<int:pk>/obrisi/', obrisi_kalkulaciju, name='obrisi_kalkulaciju'),
    path('kalkulacija/<int:kalk_id>/zakljuci/', zakljuci_kalkulaciju, name='zakljuci_kalkulaciju'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]