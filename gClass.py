from __future__ import print_function
from datetime import date
from urllib.error import HTTPError
from time import strftime
from tkinter import Y
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import threading
import datetime
import timeit
import sys
import os.path

date=datetime.datetime.now()
datedict={"year":date.strftime("%Y"),
"month":date.strftime("%m"),
"day":date.strftime("%d")}
directory_path = os.getcwd()
if os.path.exists('lib/date.dll'):
    with open(os.path.join(sys.path[0], "lib/date.dll"), "r") as f:
        line1 = f.readline()
else:
    line1 = input("Enter the Creation date to search from (yyyy-mm-dd): ")
    with open(os.path.join(sys.path[0], "lib/date.dll"), "w") as f1:
        f1.write(line1)

SCOPES = ['https://www.googleapis.com/auth/classroom.courses',
          'https://www.googleapis.com/auth/classroom.announcements',
          'https://www.googleapis.com/auth/classroom.coursework.me']

creds = None

if os.path.exists('lib/token.json'):
    creds = Credentials.from_authorized_user_file('lib/token.json', SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'lib/credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('lib/token.json', 'w') as token:
        token.write(creds.to_json())


service = build('classroom', 'v1', credentials=creds)#creates the API Service

#fetches the classes from the Classroom using classroom API
def getClasses():
    try:
        fc=open(os.path.join(sys.path[0], "bin/classes.dll"), "w+")
        fcn=open(os.path.join(sys.path[0], "bin/classNames.dll"), "w+")
        results = service.courses().list(courseStates="ACTIVE").execute()
        courses = results.get('courses', [])
        if not courses:
            print('No courses found.\n')
            return
        for course in courses:
            if(course['creationTime'] > line1):
                print(course['id'],file=fc)
                print(course['name'],file=fcn)
        fc.close
        fcn.close
    except HttpError:
        print("An error Occured %s"%HttpError)

def getDetails():
    a=[]
    b=[]
    fr=open(os.path.join(sys.path[0], "bin/classes.dll"), "r+")
    fcr=open(os.path.join(sys.path[0], "bin/classNames.dll"), "r+")
    fcw=open(os.path.join(sys.path[0], "bin/coursework.dll"), "w+")
    x=fr.readlines()
    y=fcr.readlines()
    for i in x:
        a.append(i.strip())
    for i in y:   
        b.append(i.strip())
    print(a)
    for x in range (0,len(a)):
        
        try:
            results=service.courses().courseWork().list(courseId=a[x]).execute()
            courseWork = results.get('courseWork', [])
            if not courseWork:
                pass
            else:
                for coursew in courseWork:
                    print(a[x],",",b[x],",",end="",file=fcw)
                    print(coursew['id'],",",coursew['title'],",",end="",file=fcw)
                    try:
                        dt=coursew['dueDate']
                        print(dt['year'],",",dt['month'],",",dt['day'],file=fcw)
                        #print(coursew['dueDate'],file=fcw)
                    except KeyError:print("00,00,00",file=fcw)
        except HttpError: pass
    fcw.close
    fcr.close
    fr.close
def fetchMissing():
    fr=open(os.path.join(sys.path[0], "bin/coursework.dll"), "r+")
    x=fr.readlines()
    for i in x:
        y=i.strip()
        y=y.split(",")#agar thread ke bina test karna karna hai toh comment out line 109 to 112 (included)
        '''threading.Thread(target=useThread,args=(y,)).start()
        return

def useThread(y):'''
        try:
            results=service.courses().courseWork().studentSubmissions().list(courseId=y[0].strip(),courseWorkId=y[2].strip()).execute()
            studentSubmissions=results.get('studentSubmissions',[])
            for course in studentSubmissions:
                if(course['state']!="TURNED_IN" and course['state']!="RETURNED"):
                    if(int(y[4])<=int(datedict['year']) and int(y[5])<=int(datedict['month']) and int(y[6])<=int(datedict['day'])):
                        print("Subject: ",y[1],"\nPractical Name: ",y[3],"\n", course['state'],"Missing","\n")
                    else:print("Subject: ",y[1],"\nPractical Name: ",y[3],"\n", course['state'],"\n")
        except HttpError:pass

def engine():
    while(True):
        print("1. Refresh Classes\n2. Get Courseworks\n3. Fetch Missing Practicals\n4. Exit")
        ch=int(input("Choice: "))
        if ch==1:
            getClasses()
        elif ch==2:
            getDetails()
        elif ch==3:
            fetchMissing()
        elif ch==4:
            return
        else:
            print("Wrong Choice, Enter Again")


engine()