from django.shortcuts import redirect
from .models import PoslovnaGodina

class ActiveYearMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.godina = None

        if request.user.is_authenticated:
            year_id = request.session.get('selected_year')

            if year_id:
                request.godina = PoslovnaGodina.objects.filter(id=year_id).first()

            # fallback ako nema session
            if not request.godina:
                request.godina = PoslovnaGodina.objects.filter(aktivna=True).first()

        response = self.get_response(request)
        return response
