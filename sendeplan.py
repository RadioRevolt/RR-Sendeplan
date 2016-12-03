import datetime
import csv
import io

from flask import Flask, render_template, make_response, abort, redirect, url_for
from werkzeug.contrib.fixers import ProxyFix
import requests
from yaml import load

app = Flask(__name__)

class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the 
    front-end server to add these headers, to let you quietly bind 
    this to a URL other than / and to an HTTP scheme that is 
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme

        server = environ.get('HTTP_X_FORWARDED_SERVER', '')
        if server:
            environ['HTTP_HOST'] = server
        return self.app(environ, start_response)


app.wsgi_app = ReverseProxied(app.wsgi_app)

def load_configuration(configfile):
    with open(configfile, "rb") as fp:
        data = load(fp)
    return (data['url'], -data['weeks_back'], data['weeks_forward'])

API_URL, WEEKS_BACK, WEEKS_FORWARD = load_configuration("settings.yaml")

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
    rel_week = parse_rel_week(rel_week)
    desired_monday = get_monday(rel_week)
    hours = get_week_schedule(desired_monday)
    resp = make_response(render_template('show_programming.html', 
        hours=hours, 
        first_date=desired_monday, 
        rel_week=rel_week, 
        possible_weeks=list(range(WEEKS_BACK, WEEKS_FORWARD + 1)), 
        one_day=datetime.timedelta(days=1),
        now=datetime.datetime.now()
    ))
    return prepare_response(resp)

def parse_rel_week(rel_week):
    # Is the rel_week within bounds?
    try:
        rel_week = int(rel_week)
    except ValueError:
        abort(404)
    if not (WEEKS_BACK <= rel_week <= WEEKS_FORWARD):
        abort(404)
    return rel_week

def get_monday(rel_week):
    last_monday = get_last_monday()
    desired_monday = (datetime.timedelta(days=7) * rel_week) + last_monday
    return desired_monday

@app.route("/")
def programming_default():
    return redirect(url_for('programming_week', rel_week=0))

@app.route("/<rel_week>.csv")
def programming_week_csv(rel_week):
    rel_week = parse_rel_week(rel_week)
    desired_monday = get_monday(rel_week)
    hours = get_week_schedule(desired_monday)
    hours.insert(0, ['Tid', 'Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lørdag', 'Søndag'])
    # Insert hours into the first element of each list
    for i, hour in enumerate(hours[1:]):
        hour.insert(0, "%02d00-%02d00" % (i, i+1))
    # Write the csv file
    with io.StringIO(newline='') as fp:
        writer = csv.writer(fp)
        writer.writerows(hours)
        document = fp.getvalue()
    # Prepare the response
    resp = make_response(document)
    resp = prepare_response(resp)
    resp.headers['Content-Type'] = 'text/csv'
    return resp


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
