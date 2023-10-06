import argparse
from ping3 import ping
from datetime import datetime
import requests #pip install requests
from datetime import datetime
import sqlite3

# The argparse module makeis it easy to write user-friendly command-line interfaces
parser = argparse.ArgumentParser()
parser.add_argument("-a","--add", help="Add a service", action="store_true")
parser.add_argument("-d","--delete", help="Delete a service", action="store_true")
parser.add_argument("--name", help="Name of service")
parser.add_argument("--address", help="Address IP")
parser.add_argument("--checktimes", help="Number of times the service is detected down before being notified")
parser.add_argument("--list", help="List", action="store_true")
parser.add_argument("--test", help="Test Gotify notification", action="store_true")
parser.add_argument("--gotify", help="Add Gotify URL")
args = parser.parse_args()


def get_db_connection():
    # SQLite3
    database = sqlite3.connect('tinyud.db')
    database.execute('CREATE TABLE IF NOT EXISTS tinyud (	id INTEGER PRIMARY KEY ,	nom VARCHAR(100),	addr VARCHAR(100),	state VARCHAR(10),	attempt_fail INT(5),	lasttime_down FLOAT(100),check_attempt INT(5));')
    database.execute('CREATE TABLE IF NOT EXISTS tinyud_config (id INTEGER PRIMARY KEY ,	name VARCHAR(100),	config VARCHAR(100))')
    
    return database


# Function to alert via Gotify
def alert_gotify(name,state,lasttime_down):
    database=get_db_connection()
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
    
    if ping(addresses) is None:
        return "Down"
    else:
        return "Up"
# Check principal function
def check():
    database=get_db_connection()
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

def main():

    if args.add and (args.name is None or args.address is None or args.checktimes is None):
        parser.error('--add requires --name, --address and --check')
    if args.delete and (args.name is None ):
        parser.error('--delete requires --name')

    #For Debug     
    #print("args=%s" % args)


    if args.list:
        #for data in db:
            #print(data)
        database=get_db_connection()
        for row in database.execute('SELECT * FROM tinyud'):
            print(row)
        database.close()

    if args.add:
       # db.insert({'nom': args.name,'addr':args.address,'state':'Up','attempt_fail':'0','lasttime_down':'0','check_attempt':args.check})
        database=get_db_connection()
        database.execute("""
                         INSERT INTO tinyud (nom ,addr ,state ,attempt_fail ,lasttime_down , check_attempt )
                         VALUES (?,?,"Up",0,0,?);""",
                         (args.name,args.address,args.checktimes))
        database.commit()
        database.close()
    if args.delete:
        database=get_db_connection()
        #db.remove(Element.nom == args.name)
        database.execute("""DELETE FROM tinyud WHERE nom=?""",(args.name,))
        database.commit()
        database.close()
    if args.test:
        database=get_db_connection()
        now = datetime.now()
        alert_gotify("Test","Up",now.timestamp())
        database.close()
    if args.gotify:
        database=get_db_connection()
        database.execute("""
                         INSERT INTO tinyud_config (name ,config)
                         VALUES ('GotifyURL',?);""",
                         (args.gotify,))
        database.commit()
        database.close()
    if not any(vars(args).values()):
        check()

    
if __name__ == "__main__":
    main()