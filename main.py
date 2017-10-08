from multiprocessing import Process
from sseclient import SSEClient
import json
import time
import pyrebase

config = {
  "apiKey": "AIzaSyCL5LSuFsKtcvjy7SitOoQd4iMnVbWLFkQ ",
  "authDomain": "muckrake-e5854.firebaseapp.com",
  "databaseURL": "https://muckrake-e5854.firebaseio.com/",
  "storageBucket": "gs://muckrake-e5854.appspot.com",
  "serviceAccount": "/Users/edwardgao/projects/Muckrake/muckrake-e5854-firebase-adminsdk-xo5s5-d7d01d4f59.json"
}

firebase = pyrebase.initialize_app(config)


def respond_to_query(info):
    if 'a' == "search":
        dummy = 0
    elif 'a' == "analyze_bill":
        dummy = 0
    else:
        dummy = 0

if __name__ == '__main__':

    # Start a thread to monitor changes to firebase
    t = Process(target=respond_to_query)
    t.start()

    time.sleep(1)
    # Get a reference to the auth service
    auth = firebase.auth()

    # Log the user in
    user = auth.sign_in_with_email_and_password("eddiegao98@gmail.com", "muckrake")

    # Get a reference to the database service
    db = firebase.database()

    acknowledged_tasks = set()

    while (True):
        all_agents = db.child("users").get(user['idToken']).val()
        tasks_to_complete = {}
        for agent in all_agents:
            if agent not in acknowledged_tasks:
                tasks_to_complete[agent] = all_agents[agent]
                acknowledged_tasks.add(agent)
        for agent in tasks_to_complete:
            data = respond_to_query(tasks_to_complete[agent])
            db.child("users").child(agent).set(data, user['idToken'])