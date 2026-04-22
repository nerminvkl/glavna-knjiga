import os
from django.conf import settings as django_settings


def project_title(request):
    from .models import PoslovnaGodina, KorisnickePostavke

    godina_id = request.session.get('selected_year')
    godina = None
    if godina_id:
        godina = PoslovnaGodina.objects.filter(godina=godina_id).first()

    pozadina = 'pozadina.png'
    if request.user.is_authenticated:
        try:
            pozadina = request.user.postavke.pozadina
        except:
            pass

    wallpapers = []
    try:
        putanje = []
        if hasattr(django_settings, 'STATICFILES_DIRS') and django_settings.STATICFILES_DIRS:
            putanje.append(os.path.join(django_settings.STATICFILES_DIRS[0], 'images', 'wallpapers'))
        putanje.append(os.path.join(django_settings.BASE_DIR, 'static', 'images', 'wallpapers'))

        for putanja in putanje:
            if os.path.exists(putanja):
                wallpapers = sorted([
                    f for f in os.listdir(putanja)
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
                ])
                break
    except Exception as e:
        print(f"Wallpaper greška: {e}")

    return {
        'PROJECT_TITLE': django_settings.PROJECT_TITLE,  # ← ovo
        'selected_godina': godina,
        'bg_pozadina': pozadina,
        'wallpapers': wallpapers,
    }