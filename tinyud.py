import argparse
from ping3 import ping
from datetime import datetime
import requests #pip install requests
from datetime import datetime
import sqlite3




def get_db():
    # SQLite3
    database = sqlite3.connect('/app/db/tinyud.db')
    return database


# Function to alert via Gotify
def alert_gotify(name,state,lasttime_down):
    database=get_db()
    cursor=database.cursor()
    cursor.execute("SELECT config FROM tinyud_config WHERE name='GotifyURL'")
    gotify_url=cursor.fetchone()[0]
    date_time = datetime.fromtimestamp(lasttime_down)
    if state == "Down":
        requests.post(gotify_url, json={
        "message": "The " + name + " service is "+state + " since : " + date_time.strftime("%d-%m-%Y, %H:%M:%S"),
        "priority": 2,
        "title": "Service : "+name+" : "+state
        })
    elif state == "Up":
        now = datetime.now() # current date and time
        then =datetime.fromtimestamp(lasttime_down)
        duration = now - then
        requests.post(gotify_url, json={
        "message": "The " + name + " service is "+state + ". Duration : " + str(duration.total_seconds() / 60) + " minutes",
        "priority": 2,
        "title": "Service : "+name+" : "+state
        })   
    database.close()     

# Function to check ping3
def check_ping(addresses):
    result=ping(addresses)
    if result is None or result is False:
        return "Down"
    else:
        return "Up"
# Check principal function
def check():
    database=get_db()
    cursor=database.cursor()
    cursor.execute("SELECT * FROM tinyud")
    result=cursor.fetchall()
    for data in result:
        print(data)
        oldstate = data[3]
        newstate = check_ping(data[2])
        # print(data["nom"])
        if oldstate == "Down" and newstate == "Up" :
            database.execute("""UPDATE tinyud SET state = 'Up' WHERE nom = ?""",(data[1],))
            #db.update({'state':'Up'},Element.nom == data["nom"])
            if int(data[4]) >= int(data[6]) :
                print("Notifier de nouveau Up")
                alert_gotify(data[1],"Up",data[5])
            #db.update({'attempt_fail':'0'},Element.nom == data["nom"])
            database.execute("""UPDATE tinyud SET attempt_fail = 0 WHERE nom = ?""",(data[1],))
        elif oldstate == "Up" and newstate == "Down":
            #db.update({'state':'Down'},Element.nom == data["nom"])
            database.execute("""UPDATE tinyud SET state = 'Down' WHERE nom = ?""",(data[1],))
            #db.update({'attempt_fail':'1'},Element.nom == data["nom"])
            database.execute("""UPDATE tinyud SET attempt_fail = 1 WHERE nom = ?""",(data[1],))
            now = datetime.now() # current date and time
            #db.update({'lasttime_down':now.timestamp()},Element.nom == data["nom"])
            database.execute("""UPDATE tinyud SET lasttime_down = ? WHERE nom = ?""",(now.timestamp(),data[1]))
        elif oldstate == "Down" and newstate == "Down":
            nb_fail=int(data[4])
            nb_fail +=1
            #db.update({'attempt_fail':nb_fail},Element.nom == data["nom"])
            database.execute("""UPDATE tinyud SET attempt_fail = ? WHERE nom = ?""",(nb_fail,data[1]))
            if nb_fail == int(data[6]):
                print("Notifier Down")
                alert_gotify(data[1],"Down",data[5])
    database.commit()
    database.close()
