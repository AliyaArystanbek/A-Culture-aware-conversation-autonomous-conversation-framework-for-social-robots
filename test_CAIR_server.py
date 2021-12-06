"""
Author:      Lucrezia Grassi
Email:       lucrezia.grassi@edu.unige.it
Affiliation: Laboratorium, DIBRIS, University of Genoa, Italy
Project:     CAIR

This file contains an example of client for the CAIR server
"""

import requests
import os
import pickle
import json

# Location of the API (the server it is running on)
localhost = "127.0.0.1"
azure_server = "13.95.222.73"
cineca = "131.175.198.134"
BASE = "http://" + localhost + ":5000/"

path = "state"

# If the client is not new
if os.path.exists("state.txt"):
    print("S: Welcome back!")
    print("S: I missed you. What would you like to talk about?")
else:
    resp = requests.put(BASE + "CAIR_server", verify=False)
    state = resp.json()['client_state']
    # Save the client state in the file
    with open("state.txt", 'wb') as f:
        pickle.dump(state, f)
    print("S: Hey, you're new!")
    print("S:", resp.json()['reply'])


def main():
    while True:
        sentence = input("U: ")
        # Load the array containing all information about the state of the client
        with open("state.txt", 'rb') as cl_state:
            client_state = pickle.load(cl_state)
        response = requests.get(BASE + "CAIR_server/" + sentence, data=json.dumps(client_state), verify=False)
        client_state = response.json()['client_state']
        # print(client_state)
        with open("state.txt", 'wb') as cl_state:
            pickle.dump(client_state, cl_state)
        intent_reply = response.json()['intent_reply']
        plan = response.json()['plan']
        reply = response.json()['reply']

        if intent_reply:
            if plan:
                reply = intent_reply + " " + plan + " " + reply
            else:
                reply = intent_reply + " " + reply

        print("S:", reply)


if __name__ == '__main__':
    main()
