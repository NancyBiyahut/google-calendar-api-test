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
from datetime import date, timedelta
from django.db.models import Sum 
from .models import *
from .forms import ActivityForm


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

    


def add_event(request):
    if request.method == 'POST':
        duration = request.POST.get('duration')
        activity_name = request.POST.get('activity')  # Get the selected activity name
        print(activity_name)
        creds = get_credentials()
        add_event_to_calendar(creds, duration, activity_name)

        return HttpResponse("Event added successfully!")
    
    activities = Activity.objects.all()
    return render(request, 'add_event.html', {'activities': activities})


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

    # Calculate duration in hours
    duration_hours = int(duration)

    # Calculate dates covered by the event
    date_range = [start.date() + datetime.timedelta(days=i) for i in range(duration_hours)]

    for date_covered in date_range:
        # Check if an Hour entry exists for this date and Activity
        try:
            hour_entry = Hour.objects.get(date=date_covered, activity__name=description)
            # If it exists, update the hours
            hour_entry.hours = duration_hours
            hour_entry.save()
        except Hour.DoesNotExist:
            # If it doesn't exist, create a new Hour entry
            Hour.objects.create(date=date_covered, hours=duration_hours, activity=Activity.objects.get(name=description))





from decimal import Decimal, ROUND_HALF_UP  # Import Decimal and ROUND_HALF_UP

# ...

def get_hours(request):
    today = datetime.date.today()
    seven_days_ago = today + datetime.timedelta(days=-int(7))
    
    # Group hours by date and activity, and calculate total hours for each combination
    hours = (
        Hour.objects.filter(date__range=(seven_days_ago, today))
        .values('date', 'activity__name')
        .annotate(total_hours=Sum('hours'))
        .order_by('date', 'activity__name')
    )

    # Calculate total hours and average hours per activity
    total_hours = sum(Decimal(str(hour['total_hours'])) for hour in hours)
    average_hours = total_hours / Decimal(str(7))

    # Round average_hours to 2 decimal places using ROUND_HALF_UP
    average_hours = average_hours.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

    return render(request, 'get_hours.html', {
        'hours': hours,
        'total_hours': total_hours,
        'average_hours': average_hours,
    })

def add_activity(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity_name = form.cleaned_data['name']
            if not Activity.objects.filter(name=activity_name).exists():
                form.save()
            return redirect('add_activity')  # Redirect to the index page after adding the activity
            
    else:
        form = ActivityForm()
    activities = Activity.objects.all()
    return render(request, 'add_activity.html', {'activities': activities}) 

def index(request):
    activities = Activity.objects.all()  # Retrieve all activities from the database
    return render(request, 'index.html', {'activities': activities})









if __name__ == '__main__':
    main()

