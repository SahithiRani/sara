from flask import Flask, flash, redirect, render_template, request, session, abort
import random
import pandas as pd
from datetime import datetime
from datetime import timedelta
import GetOldTweets3 as got
from datetime import datetime
from datetime import timedelta
import nltk
from nltk import TweetTokenizer 
import pandas as pd
import nltk.classify.util
from nltk.corpus import wordnet
import schedule 
import time 
import threading
import math
import json
import requests
import os.path
from os import path
from threading import Thread

data = pd.read_csv('state_wise_daily.csv', error_bad_lines=False)

data.fillna(0, inplace = True) 

visits = 0

updating = 1
running = 0
update_loop_count = 0

cur = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def reloader():

    global updating
    global running
    
    sentiment_nat = {}
    sentiment_data = {}


    x = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # start = list(sentiment_nat.keys())[0]
    start = "2020-03-01"


    start_date = datetime.strptime(start, "%Y-%m-%d")
    latest = datetime.strptime(x, "%Y-%m-%d")

    delta = latest-start_date

    date_list_keys = []
    total_maps = 0

    print(sentiment_nat)



    for ii in range(1,delta.days+1):
        # print(ii)
        from_date = (start_date+timedelta(days=ii)).strftime("%Y-%m-%d")
        # print(from_date)
        try:
            data=pd.read_csv('data/data_'+from_date + '.csv', error_bad_lines=False)
            
            if from_date not in sentiment_data.keys():
                print(from_date)
                sentiment_data[from_date] = {}
           

            if from_date not in sentiment_nat.keys():
                print(from_date)
                sentiment_nat[from_date] = [0,0,0,0,0,0,0]

        except:
            print(from_date)
            print("couldnt read")
            break
        for i,j in data.iterrows():

            # if j['Tweet Posted Time (UTC)'] not in sentiment_data.keys():
            #     print(from_date)
            #     sentiment_data[j['Tweet Posted Time (UTC)']] = {}
            
            
            
            # if j['Tweet Posted Time (UTC)'] not in sentiment_nat.keys():
            #     print(from_date)
            #     sentiment_nat[j['Tweet Posted Time (UTC)']] = [0,0,0,0,0,0,0]


            sentiment_nat[j['Tweet Posted Time (UTC)']][emotion_one(j['Emotion'])] += 1

            flag = 0
        
            areLoc = j['Tweet Location'].strip()


            if areLoc == "Visakhapatnam" or areLoc == "Tirupati":
                flag = 1
                areLoc = "Andhra Pradesh"

            if areLoc == "Jaipur":
                flag = 1
                areLoc = "Rajasthan"
            
            if areLoc == "Indore":
                flag = 1
                areLoc = "Madhya Pradesh"

            if areLoc == "Bhubaneswar":
                flag = 1
                areLoc = "Orissa"
            
            if areLoc == "Dehradun":
                flag = 1
                areLoc = "Uttarakhand"
            
            if areLoc == "Kochi":
                flag = 1
                areLoc = "Kerala"
            
            if areLoc == "Ahmedabad":
                flag = 1
                areLoc = "Gujarat"
            
            if areLoc == "Bangalore":
                flag = 1
                areLoc = "Karnataka"

            if areLoc == "Kolkata":
                flag = 1
                areLoc = "West Bengal"

            if areLoc == "Hyderabad":
                flag = 1
                areLoc = "Telangana"

            if areLoc == "Mumbai":
                flag = 1
                areLoc = "Maharashtra"
            
            

            if areLoc not in sentiment_data[j['Tweet Posted Time (UTC)']]:
                sentiment_data[j['Tweet Posted Time (UTC)']][areLoc] = [0,0,0,0,0,0,0]
            else:
                sentiment_data[j['Tweet Posted Time (UTC)']][areLoc][emotion_one(j['Emotion'])] += 1

            if flag == 1:
                if j['Tweet Location'] not in sentiment_data[j['Tweet Posted Time (UTC)']]:
                    sentiment_data[j['Tweet Posted Time (UTC)']][j['Tweet Location']] = [0,0,0,0,0,0,0]
                else:
                    sentiment_data[j['Tweet Posted Time (UTC)']][j['Tweet Location']][emotion_one(j['Emotion'])] += 1
            else:
                sentiment_nat[j['Tweet Posted Time (UTC)']][emotion_one(j['Emotion'])] += 1
    


        
    print(sentiment_nat)  

    with open('data/jsondata.txt', 'w') as outfile:
        json.dump(sentiment_data, outfile)

    with open('data/nat_jsondata.txt', 'w') as outfile:
        json.dump(sentiment_nat, outfile)

    updating = 1
    running = 0
    
    





cases_dict = {}
states = data.keys()[3:]
total_counts = {}

for i,j in data.iterrows():
    x = str(datetime.strptime(j['Date'], "%d-%b-%y").date())

    if x not in cases_dict.keys():
        cases_dict[x] = {}
        total_counts[x] = {}
        cases_dict[x][j['Status']] = {}
        total_counts[x][j['Status']] = 0

        for k in states:
            cases_dict[x][j['Status']][k] = j[k]
            total_counts[x][j['Status']] += j[k]
        
    else:
        confirm = 0
        recovered = 0
        death = 0

        cases_dict[x][j['Status']] = {}
        total_counts[x][j['Status']] = 0
        for k in states:
            cases_dict[x][j['Status']][k] = j[k]
            total_counts[x][j['Status']] += j[k]

datetime_str = '09 Feb 2020 23:35:08'

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
def emotion_one(lis):
    emo_dict = {'anger': 0, 'disgust': 1, 'joy': 2, 'surprise': 3, 'fear': 4, 'sadness': 5,'neutral':6}
    # print("++++++++++++++++++++++++++++++++")
    # print(lis)
    # print("++++++++++++++++++++++++++++++++")
    return emo_dict[lis]

def emotion(lis):
    new_list = []
    emo_dict = {'anger': 0, 'disgust': 1, 'joy': 2, 'surprise': 3, 'fear': 4, 'sadness': 5,'neutral':6}

    for k in lis:
        
        new_list.append(emo_dict[k])
    return new_list

def get_url(s):
    temp = ""
    if s == 0:
        temp = '../static/anger.png'
    elif s == 1:
        temp = '../static/disgust.png'
    elif s == 2:
        temp = '../static/happy.png'
    elif s == 3:
        temp = '../static/surprise.png'
    elif s == 4:
        temp = '../static/fear.png'
    elif s == 5:
        temp = '../static/sad.png'
    elif s == 6:
        temp = '../static/neutral.png'
        
    return temp



# f = [x.split(' ') for x in f]



# print(fdict)


# print(data.head())



@app.route("/")
def home2():

    global updating
    global cur
    global update_loop_count
    global running

    # thi = datetime.now().strftime("%Y-%m-%d")
    # print(thi,cur)
    # if thi != cur:
    #     print("Gone Wrong")
    #     updating = 0
    #     cur = thi
    # print(updating)

    # # thi = str(datetime.now())

    # if updating == 0:
    #     print("Gone into this")
    #     if running == 0:
    #         print("Gone into this too")
    #         thr = Thread(target=ultimate)
    #         thr.start()
    #         running = 1
    #         # ultimate()
    #     return render_template("Updating.html",count=update_loop_count, time=thi)



    global visits
    f = open('data/visits.txt').readlines()[0]
    visits = int(f)
    
    visits = visits + 1

    filea = open('data/visits.txt', 'w')
    filea.write(str(visits))
    filea.close()

    nowd = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    
    yesd = (datetime(2020, 3, 14)).strftime("%Y-%m-%d")

    with open('data/jsondata.txt') as json_file:
        sentiment_date = json.load(json_file)

    dates = list(sentiment_date.keys())

    nowd = dates[-1]
    
    # yesd = dates[0]


    return home(yesd+' '+nowd)

# 2020-4-3 2020-4-9
@app.route("/<string:dates>")
def home(dates):
    if(dates.split('|')[0] == 'report'):
        return report(dates)
    # dates = '2020-3-3 2020-4-29'
    print(dates)
    try:
        new_date_list = dates.split(' ')
        print("asdasd")
    except:
        print("asdasd2")
        new_date_list = ["123123","123123"]



    
    lvar = 1
    minDate = ["2020-03-14"]
    maxDate = [new_date_list[1]]
    
    # maxDate = [(datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")]
    f = open('coordinates2', encoding='utf-8').readlines()
    fdict = {}

    try:
        new_date = new_date_list[0].split('-')
        print("asdasd")
    except:
        print("asdasd2")
        new_date = minDate[0].split('-')

    try:
        print("asdasd")
        new_date1 = new_date_list[1].split('-')
    except:
        print("asdasd2")
        new_date1 = maxDate[0].split('-')

    city_state = {}

    for i in f:
        k = " "
        l = i.split(',')
        # print(l)
        first = l[0].strip().split()
        second = l[1].strip()
        fdict[k.join(first[:-2])] = [first[-2].strip(), first[-1].strip()]
        if k.join(first[:-2]) not in city_state.keys():
            city_state[k.join(first[:-2])] = second

    # print(city_state)

    # content = []
    time = []
    lats = []
    longs = []
    place = []
    emot = []



    # x = datetime.now()-timedelta(days=30*lvar)
    x = datetime(int(new_date[0]), int(new_date[1]), int(new_date[2]))
    n = datetime(int(new_date[0]), int(new_date1[1]), int(new_date1[2]))
    # n = datetime.now()-timedelta(days=30*(lvar-1))
    # n = datetime.now()-timedelta(days=1)
    n2 = datetime(2020, 3, 1)

    delta = n-x
    delta2 = datetime.now()-n2

    date_list_keys = []
    total_maps = 0
    for ii in range(delta.days+1):

        from_date = (x+timedelta(days=ii)).strftime("%Y-%m-%d")
        if x+timedelta(days=ii) >= n2:
            try:
                data=pd.read_csv('data/data_'+from_date + '.csv', error_bad_lines=False)
            except:
                print("Holy ")
            date_list_keys.append(from_date)
            total_maps += 1
            for i,j in data.iterrows():
                # print(i)
                if i > 1:
                    break
                # content.append(j['Tweet Content'])
                time.append(j['Tweet Posted Time (UTC)'])
                datetime_object = datetime.strptime(j['Tweet Posted Time (UTC)'], "%Y-%m-%d")
                # print(type(datetime_object))
                # print(datetime_object)  # printed in default format
                
                lats.append(fdict[j['Tweet Location']][0])
                longs.append(fdict[j['Tweet Location']][1])
                place.append(city_state[j['Tweet Location']])
                emot.append(j['Emotion'])

    sentiment = emotion(emot)

    f = open('state_codes', encoding='utf-8').readlines()

    state_codes = {}
    opp_state_codes = {}
    for i in f:
        l = i.strip().split(' ')
        fi = i[:-4]
        se = l[-1]
        state_codes[se] = fi
        opp_state_codes[fi] = se

    date_list = {}
    ranged_date_list = []
    emo_date_count = {}
    emo_only = {}
    sentiment_date = {}
    
    # print(place)

    # reloader()
    
    with open('data/jsondata.txt') as json_file:
        sentiment_data = json.load(json_file)

    states = ["Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat","Haryana","Himachal Pradesh","Jammu and Kashmir","Jharkhand","Karnataka","Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Orissa","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Andaman and Nicobar Islands","Chandigarh","Dadra and Nagar Haveli","Daman and Diu","Lakshadweep","Delhi","Puducherry"]
    cities = ['Mumbai', 'Chennai', 'Pune', 'Hyderabad', 'Bangalore','Tirupati']

    total_range = [0,0,0,0,0,0,0]

    nat_dict = {}

    for kk in range(delta.days+1):
        seg_date = (x+timedelta(days=kk)).strftime("%Y-%m-%d")
        datted = [0,0,0,0,0,0,0]
        for sss in states:
            if x+timedelta(days=kk) >= n2:
                try:
                    fool = sentiment_data[seg_date]
                    sd = fool[sss]
                except:
                    sd = [0,0,0,0,0,0,0]
            for n,em in enumerate(sd):
                datted[n] += em

        for ki in range(7):
            if ki in nat_dict.keys():
                nat_dict[ki].append(datted[ki])
            else:
                nat_dict[ki]= [datted[ki]]
                    

        
        # print(nat_dict)


    for sss in states:
        emolis = [0,0,0,0,0,0,0]
        for kk in range(delta.days):
            seg_date = (x+timedelta(days=kk)).strftime("%Y-%m-%d")
            if x+timedelta(days=kk) >= n2:
                fool = sentiment_data[seg_date]
                try:
                    sd = fool[sss]
                except:
                    sd = [0,0,0,0,0,0,0]
                for num,i in enumerate(sd):
                    emolis[num] += i
                    total_range[num] += i
        

        top_vals = sorted(range(len(emolis)), key=lambda i: emolis[i])[-3:]
        
        for t in top_vals:

            if emolis[t]!=0:
                dictu = {
                    "latitude": float(fdict[str(sss)][0]) + random.uniform(-0.2, 0.2),
                    "longitude": float(fdict[str(sss)][1]) + random.uniform(-0.2, 0.2),
                    "imageURL": get_url(t),
                    "value": 100,
                    "title": str(sss)
                }

            
                ranged_date_list.append(dictu)     

                



    for j in sentiment_data.keys():

        fool = sentiment_data[j]
        for k in fool.keys():
            if k in states:
                sd = fool[k]
                # print(sd)
                m = -1
                di = 0
                for num,i in enumerate(sd):
                    if i > m:
                        m = i
                        di = num

                top_vals = sorted(range(len(sd)), key=lambda i: sd[i])[-3:]
                
                for ilu in top_vals:

                    if sd[ilu] != 0:
                        dictu = {
                            "latitude": float(fdict[str(k)][0]) + random.uniform(-0.4, 0.4),
                            "longitude": float(fdict[str(k)][1]) + random.uniform(-0.4, 0.4),
                            "imageURL": get_url(ilu),
                            "value": 100,
                            "title": str(k)
                        }

                        if j not in date_list.keys():
                            date_list[j] = [dictu]
                        else:
                            date_list[j].append(dictu)

    # for num in range(len(sentiment)):

    #     datetime_object = datetime.strptime(time[num], '%Y-%m-%d').date()
    #     date = str(datetime_object)



    #     dictu = {

    #                 "latitude": float(lats[num]) + random.uniform(-0.5, 0.5),
    #                 "longitude": float(longs[num]) + random.uniform(-1, 1),
    #                 "imageURL": get_url(int(sentiment[num])),
    #                 "value": 100,
    #                 "title": place[num]
    #                 }

    #     if date not in date_list.keys():
    #         date_list[date] = [dictu]
    #     else:
    #         date_list[date].append(dictu)
        
    #     if date not in sentiment_date.keys():
    #         sentiment_date[date] = {}
        
    #     if place[num] not in sentiment_date[date].keys():
    #         sentiment_date[date][place[num]] = [0,0,0,0,0,0,0]
    #         sentiment_date[date][place[num]][int(sentiment[num])] = 1
    #     else:
    #         sentiment_date[date][place[num]][int(sentiment[num])] += 1


    #     if date not in emo_date_count.keys():
    #         emo_date_count[date] = [0,0,0,0,0,0,0]
    #         emo_date_count[date][int(sentiment[num])] = 1
    #     else:
    #         emo_date_count[date][int(sentiment[num])] += 1

    #     if str(sentiment[num]) not in emo_only.keys():
    #         emo_only[str(sentiment[num])] = [dictu]
    #     else:
    #         emo_only[str(sentiment[num])].append(dictu)
        
    # print(date_list)

    # with open('data/dates_jsondata.txt', 'w') as outfile:
    #     json.dump(date_list, outfile)
    # # print(sentiment_date)

    # with open('data/jsondata.txt', 'w') as json_file:
    #     json.dump(sentiment_date, json_file)
    emo_only = []

    # print(cases_dict)
    # print(cities)
    # Have to update everyday.

    state_cases = {}

    for i in cases_dict.keys():
        la = cases_dict[i]
        for k in la.keys():
            li = la[k]
            for sat in li.keys():
                if sat not in state_cases.keys():
                    state_cases[sat] = {"Confirmed":0,"Recovered":0,"Deceased":0}
                    state_cases[sat][k] += li[sat]
                else:
                    state_cases[sat][k] += li[sat]
    
    print(state_cases)


    
    # reloader()

    with open('data/nat_jsondata.txt') as outfile:
        emo_date_count = json.load(outfile)

    
    # print(sentiment_date)
        # print(emo_date_count)

        
    # Have to update everyday.

    
    # reloader()


    with open('data/jsondata.txt') as json_file:
        sentiment_date = json.load(json_file)
        
    emo_keys = ['2', '5', '0', '3', '6', '1', '4']

    max_lvar = math.ceil((delta2.days)/30)

    file_dates = open('data/imp_dates').readlines()
    imp_dates = []
    imp_refs = {}

    for r in file_dates:
        one = r.split('|')
        imp_dates.append(one[0])
        imp_refs[one[0]] = one[1] 

    # imp_dates = ['2020-03-02','2020-03-08','2020-03-10','2020-03-16','2020-03-19','2020-03-27','2020-03-30','2020-04-07','2020-04-12','2020-04-16']
    # imp_ref = ['02/3/2020: Uneasiness of COVID-19 being declared a global pandemic','08/3/2020: Telecom operators start warning people of COVID','10/3/2020: Large scale spread of fake news and fake cures of COVID flood social media','16/3/2020: India govt announces 14 compulsory quarantine for travellers from gulf countries','19/3/2020: Citizens asked to observe janata curfew','27/3/2020: LockdownWithoutPlan starts trending on twitter as score of labourers try walking home','30/3/2020: Police start beating people violating lockdown','07/4/2020: India lifts ban on export of hydroxychloroquine after trump threatens retaliation','12/4/2020: PM considers extension of lockdown','16/4/2020: Corona virus cases cross 3200 in Maharashtra']
    
    # for num,i in enumerate(imp_dates):
    #     imp_refs[i] = imp_ref[num]

    return render_template('index.html',state_cases=state_cases,visits = visits,minDate = minDate, maxDate=maxDate,nat_dict=nat_dict,total_range=total_range,ranged_date_list=ranged_date_list,imp_dates = imp_dates,total_maps = total_maps,max_lvar = max_lvar,lvar=lvar,len=len,sentiment_date = sentiment_date,opp_state_codes=opp_state_codes,state_codes = state_codes ,emots = emo_keys,emo_only = emo_only, emo_date_count = emo_date_count,dates = date_list_keys, kklist = date_list, enumerate=enumerate,\
             time = time, total_counts = total_counts, imp_refs=imp_refs,cases_dict = cases_dict, cities=cities,states = states, dates2 = total_counts.keys())
# Removed sentiment = sentiment, lats = lats, longs = longs, parameter


@app.route("/<string:report>")
def report(report):
    f = open('coordinates2', encoding='utf-8').readlines()
    fdict = {}

    city_state = {}

    for i in f:
        k = " "
        l = i.split(',')
        # print(l)
        first = l[0].strip().split()
        second = l[1].strip()
        fdict[k.join(first[:-2])] = [first[-2].strip(), first[-1].strip()]
        if k.join(first[:-2]) not in city_state.keys():
            city_state[k.join(first[:-2])] = second

    time = []
    lats = []
    longs = []
    place = []
    emot = []


    datekun = report.split('|')

    date = datekun[1].split('-')
    date1 = datekun[2].split('-')



    # x = datetime.now()-timedelta(days=15*lvar)
    x = datetime(2020, 3, 14)
    # n = datetime.now()-timedelta(days=15*(lvar-1))
    n = datetime.now()-timedelta(days=1)
    # n = datetime(2020,4,29)

    x = datetime(int(date[0]), int(date[1]), int(date[2]))
    n = datetime(int(date1[0]), int(date1[1]), int(date1[2]))

    n2 = datetime(2020, 3, 1)

    delta = n-x
    delta2 = datetime.now()-n2

    date_list_keys = []

    for ii in range(delta.days):

        from_date = (x+timedelta(days=ii)).strftime("%Y-%m-%d")
        date_list_keys.append(from_date)
        if x+timedelta(days=ii) >= n2:
            print('data/data_'+from_date + '.csv')
            try:
                data=pd.read_csv('data/data_'+from_date + '.csv', error_bad_lines=False)
            except:
                print("Hi")
            for i,j in data.iterrows():
                print(i)
                if i > 1:
                    break

                time.append(j['Tweet Posted Time (UTC)'])
                datetime_object = datetime.strptime(j['Tweet Posted Time (UTC)'], "%Y-%m-%d")
  
                lats.append(fdict[j['Tweet Location']][0])
                longs.append(fdict[j['Tweet Location']][1])
                place.append(city_state[j['Tweet Location']])
                emot.append(j['Emotion'])

    sentiment = emotion(emot)

    f = open('state_codes', encoding='utf-8').readlines()

    state_codes = {}
    opp_state_codes = {}
    for i in f:
        l = i.strip().split(' ')
        fi = i[:-4]
        se = l[-1]
        state_codes[se] = fi
        opp_state_codes[fi] = se

    date_list = {}
    emo_date_count = {}
    emo_only = {}
    sentiment_date = {}

    # reloader()

    with open('data/jsondata.txt') as json_file:
        sentiment_data = json.load(json_file)

    states = ["Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat","Haryana","Himachal Pradesh","Jammu and Kashmir","Jharkhand","Karnataka","Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Orissa","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Andaman and Nicobar Islands","Chandigarh","Dadra and Nagar Haveli","Daman and Diu","Lakshadweep","Delhi","Puducherry"]

    # for j in sentiment_data.keys():

    #     fool = sentiment_data[j]
    #     for k in fool.keys():
    #         if k in states:
    #             sd = fool[k]
    #             print(sd)
    #             m = -1
    #             di = 0
    #             for num,i in enumerate(sd):
    #                 if i > m:
    #                     m = i
    #                     di = num
                
    #             dictu = {
    #                 "latitude": float(fdict[str(k)][0]),
    #                 "longitude": float(fdict[str(k)][1]),
    #                 "imageURL": get_url(di),
    #                 "value": 100,
    #                 "title": str(k)
    #             }

    #             if j not in date_list.keys():
    #                 date_list[j] = [dictu]
    #             else:
    #                 date_list[j].append(dictu)

    emo_only = []

    print(fdict)

    # reloader()
    
    with open('data/nat_jsondata.txt') as outfile:
        emo_date_count = json.load(outfile)

    with open('data/jsondata.txt') as json_file:
        sentiment_date = json.load(json_file)
        
    emo_keys = ['2', '5', '0', '3', '6', '1', '4']

    max_lvar = math.ceil((delta2.days)/15)

    return render_template('report.html',int=int,len=len,sentiment_date = sentiment_date,opp_state_codes=opp_state_codes,state_codes = state_codes ,emots = emo_keys,emo_only = emo_only, emo_date_count = emo_date_count,dates = date_list_keys, kklist = date_list, enumerate=enumerate,\
             time = time, total_counts = total_counts, cases_dict = cases_dict, states = states, dates2 = total_counts.keys())



@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

def get_emo_words(sent):
        score = {}
        # tokens = remove_stop_words(sent.split(' '))
        tk = TweetTokenizer() 
        tokens = tk.tokenize(sent)
        tagged = nltk.pos_tag(tokens)
        # print(tagged)
        emo_dict = {}
        data=pd.read_csv("emotions.csv", error_bad_lines=False)
        for i,j in data.iterrows():
            emo = j['emotion']
            if emo not in emo_dict.keys():
                emo_dict[emo] = [j['word']]
            else:
                emo_dict[emo].append(j['word'])

        is_neg = False
        negation = ['no',"dont",'do not', 'not', 'never']
        for neg in negation:
            if sent.find(neg)!=-1:
                is_neg = True
                # print("Is Neg")

        for key in emo_dict.keys():
            score[key] = 0
            compare = emo_dict[key]
            # print(compare)
            for num,i in enumerate(tokens):
                #Creating a list 
                if tagged[num][1] not in ['IN','NN','NNP']:
                    synonyms = [i]
                    for syn in wordnet.synsets(i):
                        for lm in syn.lemmas():
                                synonyms.append(lm.name())#adding into synonyms
                    # print (set(synonyms))
                    synonyms = set(synonyms)
                    for k in synonyms:
                        if k in compare:
                            score[key] = score[key] + 1
                            # print(i,k,key)

        # print(score)
        feeling = ""
        maxi = -1

        was_zero = False
        for key in score.keys():
            if score[key] > maxi:
                if score[key] == 0:
                    was_zero = True
                    maxi = score[key]
                    feeling = key
                else:
                    was_zero = False
                    maxi = score[key]
                    feeling = key
            
        
        opposites = {'anger': 'neutral', 'joy':'sadness', 'surprise':'neutral','fear':'neutral','sadness':'joy','disgust':'disgust'}
        if is_neg:
            # print(opposites[feeling])
            return opposites[feeling]
            
        # print(feeling)
        if was_zero == True:
            return 'neutral'

        return feeling

def ultimate():

    global updating
    global update_loop_count

    url = 'https://api.covid19india.org/csv/latest/state_wise_daily.csv'
    r = requests.get(url, allow_redirects=True)

    open('state_wise_daily.csv', 'wb').write(r.content)

    # with open('data/jsondata.txt') as json_file:
    #     sentiment_date = json.load(json_file)

    # start = list(sentiment_date.keys())[-1]

    start = datetime(2020,5,6)

    # start = datetime.strptime(start, "%Y-%m-%d")

    x = datetime.now()-timedelta(days=1)

    dele = x - start
    # print((x+timedelta(days=60)).strftime("%Y-%m-%d"))
    states = open("state_codes", encoding='utf-8').readlines()
    states = [i[:-3] for i in states]
    # print(states)
    count = []

    Target = "This is not good."

    log = open('data/logs','w',encoding='utf-8')
    for ii in range(1,dele.days+1):
        min_count = 0
        from_date = (start+timedelta(days=ii)).strftime("%Y-%m-%d")
        to_date = (start+timedelta(days=ii+1)).strftime("%Y-%m-%d")
                
        if path.exists('data/data_'+from_date + '.csv'):
            print("Path exists: Append mode!")
            f = open('data/data_'+from_date + '.csv', 'a', encoding='utf-8')
        else:
            f = open('data/data_'+from_date + '.csv', 'a', encoding='utf-8')
            f.write('Tweet Posted Time (UTC),Tweet Content,Tweet Location,Emotion\n')
        
        print('Started for all states for the date of ' + from_date)
        log.write('Started for all states for the date of ' + from_date + '\n')
        for s in states:
            log.write("Started for State: " + s + "Date: " + from_date+"\n")
            print("Started for State: " + s + "Date: " + from_date+"\n")

            tweetCriteria4 = got.manager.TweetCriteria().setQuerySearch("Covid-19")\
                                                    .setLang('en')\
                                                    .setMaxTweets(100)\
                                                    .setNear(s)\
                                                    .setSince(from_date)\
                                                    .setUntil(to_date)

            tweetCriteria5 = got.manager.TweetCriteria().setQuerySearch("FightCorona")\
                                                    .setLang('en')\
                                                    .setMaxTweets(100)\
                                                    .setNear(s)\
                                                    .setSince(from_date)\
                                                    .setUntil(to_date)

            tweetCriteria = got.manager.TweetCriteria().setQuerySearch("coronavirus")\
                                                    .setLang('en')\
                                                    .setMaxTweets(100)\
                                                    .setNear(s)\
                                                    .setSince(from_date)\
                                                    .setUntil(to_date)

            tweetCriteria2 = got.manager.TweetCriteria().setQuerySearch("Covid")\
                                                    .setLang('en')\
                                                    .setMaxTweets(100)\
                                                    .setNear(s)\
                                                    .setSince(from_date)\
                                                    .setUntil(to_date)
            
            tweetCriteria3 = got.manager.TweetCriteria().setQuerySearch("Lockdown")\
                                                    .setLang('en')\
                                                    .setMaxTweets(100)\
                                                    .setNear(s)\
                                                    .setSince(from_date)\
                                                    .setUntil(to_date)

            tweet = got.manager.TweetManager.getTweets(tweetCriteria)
            for i in tweet:
                print(i)
                update_loop_count += 1
                min_count += 1
                f.write(from_date +","+ i.text.replace(',', ' ') +","+ s.strip() +"," + get_emo_words(i.text.replace(',', ' ')) + '\n' )

            tweet2 = got.manager.TweetManager.getTweets(tweetCriteria2)
            for i in tweet2:
                print(i)
                update_loop_count += 1
                min_count += 1
                f.write(from_date +","+ i.text.replace(',', ' ') +","+ s.strip() +"," + get_emo_words(i.text.replace(',', ' ')) + '\n' )

            tweet3 = got.manager.TweetManager.getTweets(tweetCriteria3)
            for i in tweet3:
                print(i)
                update_loop_count += 1
                min_count += 1
                f.write(from_date +","+ i.text.replace(',', ' ') +","+ s.strip() +"," + get_emo_words(i.text.replace(',', ' ')) + '\n' )

            tweet4 = got.manager.TweetManager.getTweets(tweetCriteria4)
            for i in tweet4:
                print(i)
                update_loop_count += 1
                min_count += 1
                f.write(from_date +","+ i.text.replace(',', ' ') +","+ s.strip() +"," + get_emo_words(i.text.replace(',', ' ')) + '\n' )

            tweet5 = got.manager.TweetManager.getTweets(tweetCriteria5)
            for i in tweet5:
                print(i)
                update_loop_count += 1
                min_count += 1
                f.write(from_date +","+ i.text.replace(',', ' ') +","+ s.strip() +"," + get_emo_words(i.text.replace(',', ' ')) + '\n' )
                
            
            print(s,from_date)
            log.write("State: " + s + "Date: " + from_date+ " --done\n")
        log.write('Completed all states for the date of ' + from_date + '\n')
        print('Completed all states for the date of ' + from_date)

        log.write('Count min: ' +from_date + " " + str(min_count) + '\n')     
        count.append(min_count)
        f.close()
    sumi = 0
    for i in count:
        sumi = sumi + i
    log.write('Count Total: ' + str(sumi) + '\n')
    print(count)

    reloader()

# def test():
#     for i in range(5):
#         print("yes ho")

# def run_task():
#     schedule.every().day.at("23:40").do(ultimate) 
#     while True:
#         schedule.run_pending() 
#         time.sleep(1)

if __name__ == "__main__":
    
    # try:
    #     threading.Thread(target = run_task).start()
    # except:
    #     print("Caught an exception")

    # threading.Thread(target = run_task).start()
    app.run(port=5000, debug=True)