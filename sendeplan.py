import datetime

from flask import Flask, render_template, make_response, abort, redirect, url_for
import requests
from yaml import load

app = Flask(__name__)

def load_configuration(configfile):
    with open(configfile, "rb") as fp:
        data = load(fp)
    return data['url']

API_URL = load_configuration("settings.yaml")

def get_week_schedule(monday):
    datas = fetch_data_from_api(monday)
    days = []
    for data in datas:
        program_start_hours = dict()
        
        for j, entry in enumerate(data):
            hour_string = entry['starttime'][11:13]
            hour = int(hour_string)
            program_start_hours[hour] = entry['title']
            
        # Make sure we have one entry per hour
        # The first entry is set to be "Not available", in case the first
        # hour is not present.
        all_hours = ["Ikke tilgjengelig"]
        for hour in range(24):
            if (hour in program_start_hours):
                # Entry for this hour, use it
                all_hours.append(program_start_hours[hour])
            else:
                # No entry for this hour, use last hour's entry
                all_hours.append(all_hours[-1])
        # Cut off the first "Not available"-message
        all_hours = all_hours[1:]
        
        days.append(all_hours)
    
    # Go from list of days to list of hours
    new_times = []
    for hour in range(24):
        programs = []
        for day in range(7):
            programs.append(days[day][hour])
        new_times.append(programs)
    return new_times

def prepare_response(resp):
    # Store for 5 minutes
    resp.cache_control.max_age = int(datetime.timedelta(minutes=5).total_seconds())
    # Everyone can cache it
    resp.cache_control.public = True
    return resp

@app.route("/<rel_week>")
def programming_week(rel_week):
    # Is the rel_week within bounds?
    try:
        rel_week = int(rel_week)
    except ValueError:
        abort(404)
    if not (-3 <= rel_week <= 2):
        abort(404)
    last_monday = get_last_monday()
    desired_monday = (datetime.timedelta(days=7) * rel_week) + last_monday
    hours = get_week_schedule(desired_monday)
    resp = make_response(render_template('show_programming.html', hours=hours, first_date=desired_monday))
    return prepare_response(resp)

@app.route("/")
def programming_default():
    return redirect(url_for('programming_week', rel_week=0))

def fetch_data_from_api(first_date):
    datas = []
    date = first_date
    one_day = datetime.timedelta(days=1)
    for i in range(0, 7):
        
        r = requests.get("{api_url}/sendinger/dato/{year}/{month}/{day}/autoavvikler".format(
            api_url=API_URL,
            year=date.year,
            month=date.month,
            day=date.day
            )
        )
        r.raise_for_status()
        datas.append(r.json())
        date+= one_day
    return datas

def get_last_monday():
    today = datetime.date.today()
    days_since_monday = datetime.timedelta(days=1) * today.weekday()
    monday = today - days_since_monday
    return monday

if __name__ == "__main__":
    app.run()
