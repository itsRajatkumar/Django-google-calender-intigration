from django.shortcuts import redirect

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import os

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/calendar']
REDIRECT_URL = 'http://127.0.0.1:8080/rest/v1/calendar/redirect'
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'


class InitAuth(APIView):

    def get(self, request):

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URL
        authorization_url, state = flow.authorization_url(
            access_type='offline', include_granted_scopes='true')
        request.session['state'] = state
        return redirect(authorization_url)
