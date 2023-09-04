import argparse
from tinydb import TinyDB, Query
from ping3 import ping
from datetime import datetime
import requests #pip install requests

# The argparse module makeis it easy to write user-friendly command-line interfaces
parser = argparse.ArgumentParser()
parser.add_argument("-a","--add", help="Add a service", action="store_true")
parser.add_argument("-d","--delete", help="Delete a service", action="store_true")
parser.add_argument("--name", help="Name of service")
parser.add_argument("--address", help="Address IP")
parser.add_argument("--list", help="List", action="store_true")
parser.add_argument("--test", help="Test Gotify notification", action="store_true")
args = parser.parse_args()

# Initialize TinyDB
db = TinyDB('tinydb.json')
Element = Query()

# Variable
gotify_url=db.search(Element.nom =="GotifyURL")
now = datetime.now() # current date and time
date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

# Function to alert via Gotify
def alert_gotify(name,state):
    requests.post(gotify_url[0]["addr"], json={
    "message": date_time + " : The " + name + " service is "+state,
    "priority": 2,
    "title": "Service : "+name+" : "+state
    })

# Function to check ping3
def check_ping(addresses):
    
    if ping(addresses) is None:
        return "Down"
    else:
        return "Up"
# Check principal function
def check():
    for data in db:
        if data["nom"] == "GotifyURL":
            continue
        oldstate = data["state"]
        newstate = check_ping(data["addr"])
        # print(data["nom"])
        if oldstate == "Down" and newstate == "Up" :
            db.update({'state':'Up'},Element.nom == data["nom"])
            if int(data["attempt_fail"]) >= 5 :
                print("Notifier de nouveau Up")
                alert_gotify(data["nom"],"Up")
            db.update({'attempt_fail':'0'},Element.nom == data["nom"])
        elif oldstate == "Up" and newstate == "Down":
            db.update({'state':'Down'},Element.nom == data["nom"])
            db.update({'attempt_fail':'1'},Element.nom == data["nom"])
        elif oldstate == "Down" and newstate == "Down":
            nb_fail=int(data["attempt_fail"])
            nb_fail +=1
            db.update({'attempt_fail':nb_fail},Element.nom == data["nom"])
            if nb_fail == 5:
                print("Notifier Down")
                alert_gotify(data["nom"],"Down")

def main():

    if args.add and (args.name is None or args.address is None):
        parser.error('--add requires --name and --address')
    if args.delete and (args.name is None ):
        parser.error('--delete requires --name')

    #For Debug     
    print("args=%s" % args)


    if args.list:
        for data in db:
            print(data)

    if args.add:
        db.insert({'nom': args.name,'addr':args.address,'state':'Up','attempt_fail':'0','lasttime_down':'0'})

    if args.delete:
        db.remove(Element.nom == args.name)

    if args.test:
        alert_gotify("Test","Test")

    if not any(vars(args).values()):
        check()

if __name__ == "__main__":
    main()