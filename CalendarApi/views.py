from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
import requests

class GoogleCalendarInitView(View):
    def get(self, request):
        SCOPE = 'https://www.googleapis.com/auth/calendar'
        AUTHORIZATION_ENDPOINT = 'https://accounts.google.com/o/oauth2/auth?client_id={}&redirect_uri={}&scope={}&response_type=code'

        # redirect the user to the Google authorization endpoint
        auth_url = AUTHORIZATION_ENDPOINT.format(settings.CLIENT_ID, settings.REDIRECT_URI, SCOPE)

        return redirect(auth_url)

class GoogleCalendarRedirectView(View):
    def get(self, request):
        # make post request to the Google account endpoint to to get access token
        response = requests.post(
            'https://accounts.google.com/o/oauth2/token',
            data={
                'client_id': settings.CLIENT_ID,
                'client_secret': settings.CLIENT_SECRET,
                'redirect_uri': settings.REDIRECT_URI,
                'code': request.GET.get('code'),
                'grant_type': 'authorization_code',
            }
        )
        
        # extract token
        access_token = response.json().get('access_token')
        
        calendar_id = 'primary'
        
        # make get request google-calendar API with token
        response = requests.get(
            f'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events',
            headers={
                'Authorization': f'Bearer {access_token}',
            }
        )
        events = response.json().get('items', [])
        event_list = []
        for event in events:
            event_list.append({
                'summary': event.get('summary'),
                'start': event.get('start', {}).get('dateTime'),
                'end': event.get('end', {}).get('dateTime'),
            })
        
        return JsonResponse(event_list, safe=False)
