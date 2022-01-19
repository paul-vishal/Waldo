import psycopg2
import smtplib

import requests
from flask import Response
from flask import Flask
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from kafka import KafkaConsumer
from json import loads

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


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


@app.route('/notify')
def notifyUser():
    try:
        print('Notifying User')
        apiData = fetchAPIData()
        userList = fetchUserList()
        print('UserList', userList)
        emailData = constructDataForNotification(userList, apiData)
        print('EmailData')
        print(emailData)
        for i in range(0, len(emailData)):
            TO = [emailData[i][0]]
            print('Sending Email To:', TO)
            SUBJECT = "Waldo Papers for You!"
            # apiData_json = json.loads(apiData)
            # data = apiData_json['data']

            # print(data)
            urls = ""
            for items in emailData[i][1]:
                urls = urls + items + "\n "

            # print(urls)
            message = "Thank You. Here is some images you might like. Please Login to Waldo App for more!! \n" + urls

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
    #requests.get("http://b2-broker:9001/notify")
    return Response("Hi Waldo!!, Email sent")


def fetchUserList():
    query = "select * from m_user"
    db_cursor, db_conn = getDBConnection()
    db_cursor.execute(query)
    userList = db_cursor.fetchall()
    userPreference = []
    for i in userList:
        userPreference.append(fetchUserPreference(i[5], i[2]))
    return userPreference


def fetchUserPreference(userName, email):
    print('Fetching user preferences')
    query = "select * from get_user_preferences('%s')"
    db_cursor, db_conn = getDBConnection()
    db_cursor.callproc('get_user_preferences', [userName])
    userPreference = db_cursor.fetchall()
    userPrefObj = formatUserPreference(userPreference[0])
    userResult = [email, userPrefObj]
    return userResult


# anime , abstract , animals , cars
def formatUserPreference(prefObj):
    for x in prefObj:
        userDataObj = [x['digitalArt'], x['minimalism'], x['mountains'], x['nature']]
    return userDataObj


def fetchAPIData():
    print('Fetching Saved API Data from DB')
    query = "select * from category_results"
    db_cursor, db_conn = getDBConnection()
    db_cursor.execute(query)
    apiData = db_cursor.fetchall()
    return apiData[0][0]


def constructDataForNotification(user, apiData):
    userDataObj = []
    for i in range(0, len(user)):
        for j in range(0, 4):
            if user[i][1][j]:
                if j == 0:
                    userDataObj.append([user[i][0], apiData['digitalArt']])
                elif j == 1:
                    userDataObj.append([user[i][0], apiData['minimalism']])
                elif j == 2:
                    userDataObj.append([user[i][0], apiData['mountains']])
                elif j == 3:
                    userDataObj.append([user[i][0], apiData['nature']])
    return userDataObj


consumer = KafkaConsumer(
    'abstract', 'animals', 'mountains', 'nature', 'photography', 'sports',
    value_deserializer=lambda m: loads(m.decode('utf-8')),
    bootstrap_servers='kafka2:19092')

for m in consumer:
    print(m.value)
    notifyUser()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9092)
