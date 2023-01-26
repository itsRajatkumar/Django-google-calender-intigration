from django.shortcuts import redirect

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/calendar']
REDIRECT_URL = 'http://127.0.0.1:8000/rest/v1/calendar/redirect'
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'


class InitAuth(APIView):

    def get(self, request):
        try:
            # handlig initialization of google auth for calender access
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, scopes=SCOPES,redirect_uri = REDIRECT_URL)
            
            authorization_url, state = flow.authorization_url(
                access_type='offline', include_granted_scopes='true')
            request.session['state'] = state
            return redirect(authorization_url)
        except Exception:
            return Response({"status":False,"message": "Internal Server Error"})
    
class GetCalendarEvents(APIView):

    def get(self, request):
        try:
            # handlig redirect from google
            state = request.session['state']

            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
            flow.redirect_uri = REDIRECT_URL
            authorization_response = request.get_full_path()
            flow.fetch_token(authorization_response=authorization_response)

            credentials = flow.credentials
            
            request.session['credentials'] = {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

            if 'credentials' not in request.session:
                return redirect('v1/calendar/init')

            credentials = google.oauth2.credentials.Credentials(
                **request.session['credentials'])

            service = googleapiclient.discovery.build(
                API_SERVICE_NAME, API_VERSION, credentials=credentials)

            calendar_list = service.calendarList().list().execute()

            calendar_id = calendar_list['items'][0]['id']

            events  = service.events().list(calendarId=calendar_id).execute()

            if not events['items']:
                return Response({"status":False,"message": "User does not have Events"})
            else:
                return Response({"status":True,"message": "Success","data":events['items']})
        except Exception as error:
            return Response({"status":False,"message": "Internal Server Error"})
