import json
import psycopg2
from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.shortcuts import render
from wallhaven.api import Wallhaven
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ast
import smtplib
from kafka import KafkaProducer
from json import dumps

# Create your views here.
wallhaven_obj = Wallhaven(api_key="X9XQ93BFRXZKPB7KzwxgQbNv59FLStTt")


# wallhaven_obj = Wallhaven(api_key="sKFDEhAGIqJL3iILEtmh808HLWHyG5ra")


def index(request):
    print('index')
    return render(request, 'index.html')


def login_page(request):
    print('login_page')
    return render(request, 'login.html')


def login(request):
    print('login page')
    username = request.GET.get('username')
    password = request.GET.get('password')
    db_cursor, db_conn = getDBConnection()
    if db_cursor is not None:
        pwd = getUserNameFromDB(db_cursor, username)
        if pwd == password and pwd is not None:
            query = "select * from get_user_preferences(%s)"
            db_cursor.callproc('get_user_preferences', [username])
            data_from_db = db_cursor.fetchone()
            html_page = render(request, 'userpref.html')
            html_page_dom = BeautifulSoup(html_page.content, features="html.parser")
            updated_html_dom = update_html_dom_with_user_inputs(data_from_db, html_page_dom)
            updated_html_dom = update_html_dom_with_username(updated_html_dom, username)
            return HttpResponse(updated_html_dom.prettify())
    return HttpResponse('Hi ' + username + ': Login Failed, Try Again!')


def advertise(request):
    print('advertise')
    username = request.GET.get('username')
    password = request.GET.get('password')
    print(username, password)
    db_cursor, db_conn = getDBConnection()
    if db_cursor is not None:
        pwd = getUserNameFromDB(db_cursor, username)
        if pwd == password and pwd is not None:
            query = "select * from get_user_preferences(%s)"
            db_cursor.callproc('get_user_preferences', [username])
            userPreference = db_cursor.fetchall()
            userPrefObj = formatUserPreference(userPreference[0])
            userEmail = fetchUserEmail(db_cursor, username)
            notify(userEmail, userPrefObj)
    return HttpResponse('Hi ' + username)


def formatUserPreference(prefObj):
    # value_if_true if condition else value_if_false
    userPref = []
    prefObj = ast.literal_eval(str(prefObj[0]))
    for x in prefObj.keys():
        if prefObj[x] is False:
            userPref.append(x)
    print(userPref)
    return userPref


def fetchUserEmail(db_cursor, user_name):
    if db_cursor is not None and user_name is not None:
        s = ""
        s = s + "SELECT email FROM public.m_user WHERE"
        s = s + " user_name ='" + user_name + "'"
        db_cursor.execute(s)
        pwd_from_db = db_cursor.fetchone()[0]
        print(pwd_from_db)
        return pwd_from_db
    return None


def notify(userEmail, userPrefObj):
    try:
        print('Notifying User')

        TO = [userEmail]
        print('Sending Email To:', TO)
        SUBJECT = "Advertise ! Waldo Papers for You!"

        urls = ""
        for items in userPrefObj:
            urls = urls + items + "\n "

        message = "Thank you for being a loyal user, We have more options for you, Please check and subscribe for these categories also ! \n" + urls

        password = "helloworld123"

        # Create a secure SSL context
        msg = MIMEMultipart()

        msg['From'] = "hw2400727@gmail.com"
        msg['To'] = ', '.join(TO)
        msg['Subject'] = SUBJECT

        msg.attach(MIMEText(message, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
        server.login(msg['From'], password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()

    except Exception as e:
        print('Error:', e)
    print('email sent')

    return True


def register(request):
    username = request.GET.get('username')
    password = request.GET.get('password')
    email = request.GET.get('email')
    mobile = request.GET.get('mobile')
    fullname = request.GET.get('fullname')
    print(username, password, email, mobile, fullname)

    anime = True if request.GET.get('anime') == "true" else False
    abstract = True if request.GET.get('abstract') == "true" else False
    animals = True if request.GET.get('animals') == "true" else False
    cars = True if request.GET.get('cars') == "true" else False
    digitalArt = True if request.GET.get('digitalArt') == "true" else False
    minimalism = True if request.GET.get('minimalism') == "true" else False
    mountains = True if request.GET.get('mountains') == "true" else False
    nature = True if request.GET.get('nature') == "true" else False
    photography = True if request.GET.get('photography') == "true" else False
    sports = True if request.GET.get('sports') == "true" else False
    tattoo = True if request.GET.get('tattoo') == "true" else False
    games = True if request.GET.get('games') == "true" else False

    userPreference = {"anime": anime,
                      "abstract": abstract,
                      "animals": animals,
                      "cars": cars,
                      "digitalArt": digitalArt,
                      "minimalism": minimalism,
                      "mountains": mountains,
                      "nature": nature,
                      "photography": photography,
                      "sports": sports,
                      "tattoo": tattoo,
                      "games": games}

    query = "select * from register_user(%s,%s,%s,%s,%s,%s)"
    db_cursor, db_conn = getDBConnection()
    db_cursor.callproc('register_user', [fullname, email, password, mobile, username, json.dumps(userPreference)])
    pwd_from_db = db_cursor.fetchall()
    db_conn.commit()
    print(pwd_from_db)
    return HttpResponse(
        'Hi ' + username + " " + str(pwd_from_db))


def fetchWallHavenData():
    url_list = {}
    wallhaven_obj.params["sorting"] = "toplist"
    categories = ['anime', 'abstract', 'animals', 'cars', 'sports', 'minimalism']
    # 'photography', 'mountains','nature', 'digital art', 'tattoo', 'games']

    for category in categories:
        wallhaven_obj.params["q"] = category
        results = json.loads(wallhaven_obj.search().as_json())
        urls = []
        data_array = results['data']
        for data in data_array:
            urls.append(data['url'])
        url_list[category] = urls
    return json.loads(json.dumps(url_list))


def notifyUser(request):
    print('Notifying User')
    apiData = fetchWallHavenData()
    print('Wallhaven data Fetched')
    query = "select * from save_or_update_catagory(%s)"
    db_cursor, db_conn = getDBConnection()
    db_cursor.callproc('save_or_update_catagory', [json.dumps(apiData)])
    pwd_from_db = db_cursor.fetchall()
    db_conn.commit()
    print('Initializing kafka producer')
    producer = KafkaProducer(value_serializer=lambda m: dumps(m).encode('utf-8'), bootstrap_servers=['kafka1:19091', 'kafka2:19092', 'kafka3:19093'])
    producerData = apiData
    print('Producer sending data !')
    for data in producerData:
        value = producerData[data]
        print("The key and value are ({}) = ({})".format(data, value))
        producer.send(data, value=json.dumps(value))
    return HttpResponse("Hi Waldo!!, DB updated")


def getUserNameFromDB(db_cursor=None, user_name=None):
    if db_cursor is not None and user_name is not None:
        s = ""
        s = s + "SELECT hash_password FROM public.m_user WHERE"
        s = s + " user_name ='" + user_name + "'"
        db_cursor.execute(s)
        pwd_from_db = db_cursor.fetchone()[0]
        print(pwd_from_db)
        return pwd_from_db
    return None


def getDBConnection():
    # Database Credentials
    hostname = "postgres"
    port = "5432"
    dbname = "postgres"
    db_user = "postgres"
    db_pwd = "admin"
    db_conn = psycopg2.connect(host=hostname, port=port, dbname=dbname, user=db_user, password=db_pwd)
    db_cursor = db_conn.cursor()
    return db_cursor, db_conn


def update_html_dom_with_user_inputs(user_inputs, html_dom):
    user_inputs = user_inputs[0]
    for key in user_inputs.keys():
        if user_inputs[key] is True:
            checkbox = html_dom.find('input', attrs={"name": key})
            if checkbox is not None:
                checkbox['checked'] = "checked"
    return html_dom


def update_html_dom_with_username(html_dom, username):
    html_dom.find('h1', attrs={"class": "username"}).string = "Welcome " + username + "!!"
    return html_dom


def updatePreference(request):
    print(request.GET.get('advertise'))
    if request.GET.get('advertise') == 'advertise':
        response = advertise(request)
        return response
    elif request.GET.get('update') == 'update':
        username = request.GET.get('username')
        print(username)
        anime = True if request.GET.get('anime') == "true" else False
        abstract = True if request.GET.get('abstract') == "true" else False
        animals = True if request.GET.get('animals') == "true" else False
        cars = True if request.GET.get('cars') == "true" else False
        digitalArt = True if request.GET.get('digitalArt') == "true" else False
        minimalism = True if request.GET.get('minimalism') == "true" else False
        mountains = True if request.GET.get('mountains') == "true" else False
        nature = True if request.GET.get('nature') == "true" else False
        photography = True if request.GET.get('photography') == "true" else False
        sports = True if request.GET.get('sports') == "true" else False
        tattoo = True if request.GET.get('tattoo') == "true" else False
        games = True if request.GET.get('games') == "true" else False

        userPreference = {"anime": anime,
                          "abstract": abstract,
                          "animals": animals,
                          "cars": cars,
                          "digitalArt": digitalArt,
                          "minimalism": minimalism,
                          "mountains": mountains,
                          "nature": nature,
                          "photography": photography,
                          "sports": sports,
                          "tattoo": tattoo,
                          "games": games}

        query = "select * from update_or_save_preference(%s,%s)"
        db_cursor, db_conn = getDBConnection()
        db_cursor.callproc('update_or_save_preference', [username, json.dumps(userPreference)])
        pwd_from_db = db_cursor.fetchall()
        db_conn.commit()
        return HttpResponse(
            'Hi ' + username + " , your preference has been updated")
