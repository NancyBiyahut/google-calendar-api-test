# calendar_integration/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz
import datetime
import os.path
import sqlite3
from dateutil import parser

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    
def index(request):
    return render(request, 'index.html')

def add_event(request):
    if request.method == 'POST':
        duration = request.POST.get('duration')
        description = request.POST.get('description')

        creds = get_credentials()
        add_event_to_calendar(creds, duration, description)

        return HttpResponse("Event added successfully!")

    return render(request, 'add_event.html')

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
    return creds

def add_event_to_calendar(creds, duration, description):
    ist_timezone = pytz.timezone('Asia/Kolkata')
    start = datetime.datetime.now(ist_timezone)
    end = start + datetime.timedelta(hours=int(duration))
    start_formatted = start.isoformat()
    end_formatted = end.isoformat()

    service = build('calendar', 'v3', credentials=creds)
    event = {
        'summary': description,
        'start': {
            'dateTime': start_formatted,
            'timeZone': "Asia/Kolkata",
        },
        'end': {
            'dateTime': end_formatted,
            'timeZone': "Asia/Kolkata",
        },
    }
    event = service.events().insert(
        calendarId='1138f1bddfe6076b55d204ff5a9aa09dd3e71f23ca54e893a9d0f80147489098@group.calendar.google.com',
        body=event).execute()

def get_hours(request, number_of_days):
    today = datetime.date.today()
    seven_days_ago = today + datetime.timedelta(days=-int(number_of_days))
    conn = sqlite3.connect('hours.db')
    cur = conn.cursor()
    cur.execute(f"SELECT DATE, HOURS FROM hours WHERE DATE between ? AND ?", (seven_days_ago, today))
    hours = cur.fetchall()
    total_hours = 0
    for element in hours:
        total_hours += element[1]
    average_hours = total_hours / float(number_of_days)
    return render(request, 'get_hours.html', {
        'hours': hours,
        'total_hours': total_hours,
        'average_hours': average_hours,
    })

if __name__ == '__main__':
    main()

