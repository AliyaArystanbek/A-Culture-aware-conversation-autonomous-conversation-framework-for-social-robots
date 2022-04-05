
from flask import Flask, request, make_response
from flask_restful import Api
from topics import *
from topics_utils import *
from CAIR_utils import *
from google.cloud import language_v1
from nltk.tokenize import word_tokenize 
import argparse
import io
import json
import os
import numpy
import six
import itertools
import sys 
import openai
import requests
import json
import random
import zlib
import re

app = Flask(__name__)
api = Api(app)

# IP of where the service for regex match is running
regex_ip = "127.0.0.1"
# Port for the request to the regex match service
regex_port = 5001

print("Starting dialogue manager. Please wait some seconds...")

# ------ RETRIEVE BASIC STUFF FROM FILES GENERATED STARTING FROM THE ONTOLOGY ------
# Get topic names, likelinesses and keywords (from triggering_keyword.json) - CHECKED
id_reqs, req_par1, req_par2, tot_topic = get_topics_keywords_and_likelinesses()

# Get the relationships between topics - father, children, brothers, and likeliness - CHECKED
top_topics, topics_father, topics_children, topics_brothers, base_topics_likeliness = get_topics_relationships()

# Get the topics, the types of the sentences, the sentences (from sentences.enu files) - CHECKED
topics_sentences_types, topics_sentences = get_topics_sentences()

# Initialize the flags of all topics sentences to zero
base_topics_sentences_flags = initialize_topics_sentences_flags(topics_sentences)

# The dictionary contains as keys the types of the sentences (where they should be used), and as values the sentences
common_sent_dict = retrieve_common_sentences()

init_topics = get_starting_topics()

# Sentence that triggers the goal when the user answers 'yes' to a goal request
goal_trigger_sentence = ''


def call_regex_matcher(sentence, prev_topic_number):
    # ---------- Call the service for matching patterns ----------
    print("\n ---------- CALLING REGEX MATCH SERVICE ----------")
    try:
        response = requests.get("http://" + regex_ip + ":" + str(regex_port) + "/CAIR_regex/" + str(prev_topic_number)
                                + "/" + sentence, verify=False)
        print(response.json())
        intent_reply = response.json()['reply']
        kbplan = response.json()['kbplan']
        plan = response.json()['plan']
    except requests.exceptions.ConnectionError as e:
        print(e)
        intent_reply = ''
        kbplan = ''
        plan = ''
    return intent_reply, kbplan, plan


def procedure(client_state, sentence, intent_reply, topics_sentences_flags, topics_likeliness):
    # The flags and the likelinesses are already merged with the ones specific of the client
    sentence = sentence.lower()

    # Save all data related to the current client
    prev_topic_number = client_state["topic"]
    prev_topic_sentence_type = client_state["sentence_type"]
    prev_topic_pattern = client_state["pattern"]
    prev_topic_stop = client_state["bool"]

    # Merge client likelinesses with original likelinesses
    modified_topics_likeliness = client_state["likelinesses"]

    # TODO: maybe it's better to put these answers in a file and use a broader set - maybe with regex?
    pos_user_answers = ["yes", "ok", "fine", "sure", "of course", "correct"]
    neg_user_answers = ["no", "never"]

    perform_goal = 0
    show_interest = False

    # Check the type of the previous sentence:
    if prev_topic_sentence_type == 'q':
        print("Expecting answer to a question")
        sentiment = 0
        # If the answer contains yes, change the likeliness of the previous topic to 1
        if any(word in sentence for word in pos_user_answers):
            sentiment = 1
            topics_likeliness[prev_topic_number] = 1.0
            modified_topics_likeliness[str(prev_topic_number)] = 1.0
            print("Setting likeliness of topic ", prev_topic_number, " to 1.0")
        elif any(word in sentence for word in neg_user_answers):
            sentiment = -1
            topics_likeliness[prev_topic_number] = 0.0
            modified_topics_likeliness[str(prev_topic_number)] = 0.0
            print("Setting likeliness of topic ", prev_topic_number, " to 0.0")

        # Check if the sentence is related to a topic
        # Allow topics with likeliness zero
        topic_n = main(sentence, id_reqs, topics_likeliness, req_par1, req_par2, tot_topic)
        # If a topic associated to the sentence is found
        if topic_n != -1:
            # If the topic is the same as the previous one
            if topic_n == prev_topic_number:
                # If the answer is not negative, try to continue with the same topic
                if sentiment != -1:
                    # Insert a positive sentence as next element of the pattern
                    prev_topic_pattern.insert(0, 'p')
                    print("Added positive sentence type to answer to the positive answer")
                    negative = False
                # If the sentiment is negative
                else:
                    prev_topic_pattern = ['n']
                    print("Added negative sentence type to answer to the negative answer")
                    negative = True

                sentence_type, prev_topic_pattern, reply, topic_n, prev_topic_stop, topics_sentences_flags = \
                    explore_DT("", prev_topic_number, prev_topic_pattern, prev_topic_stop, topics_father,
                               topics_children, topics_brothers, topics_likeliness, topics_sentences,
                               topics_sentences_types, topics_sentences_flags, negative)
            # If the triggered topic is not the same as the previous one, jump to that
            else:
                # Choose a new pattern
                print("Jumping to topic: ", topic_n)
                print("Topic likeliness: ", topics_likeliness[topic_n])
                # Start a new pattern for the new topic
                sentence_type, prev_topic_pattern, reply, topic_n, prev_topic_stop, topics_sentences_flags = \
                    start_new_pattern(topic_n, prev_topic_stop, topics_father, topics_children, topics_brothers,
                                      topics_likeliness, topics_sentences, topics_sentences_types,
                                      topics_sentences_flags)
                # Check if the likeliness of the returned topic is zero -> ask confirmation!
                if float(topics_likeliness[topic_n]) == 0.0:
                    print("Chosen topic likeliness:", topics_likeliness[topic_n])
                    reply = "I thought you didn't like it..." + reply

        # If no topic associated to the sentence is found
        else:
            print("No topic associated to sentence found.")
            if sentiment != -1:
                print("Prev topic number: ", prev_topic_number)
                prev_topic_pattern.insert(0, 'p')
                print("Added positive sentence type to pattern to answer to user's sentence")
                negative = False
            # If no topic is found and the user said no, go to negative
            else:
                negative = True
                prev_topic_pattern = ['n']
                print("Added negative sentence type to pattern to answer to user's sentence")
            sentence_type, prev_topic_pattern, reply, topic_n, prev_topic_stop, topics_sentences_flags = \
                explore_DT("", prev_topic_number, prev_topic_pattern, prev_topic_stop, topics_father,
                           topics_children, topics_brothers, topics_likeliness, topics_sentences,
                           topics_sentences_types, topics_sentences_flags, negative)
    # If we are at the end
    elif prev_topic_sentence_type == 'e':
        print("---------- REACHED END STATE ----------")
        # Check if the user's sentence contains keywords
        # Allow also topics with likeliness zero, if no other topics are found
        topic_n = main(sentence, id_reqs, topics_likeliness, req_par1, req_par2, tot_topic)
        common_sent = ''
        # If no topic is triggered by the user's sentence, choose it from top concepts
        if topic_n == -1:  ######## If the topic -1 and now children and brother Call OPENAI API
            print("No topic triggered by the user: choose from top concepts")
            topic_n = choose_topic(top_topics, topics_likeliness, False)
            # The sentence to be added at the beginning will be one of those to be put before a top concept
            common_sent = random.choice(common_sent_dict['r'])
            # Start a new pattern for the new topic
            sentence_type, prev_topic_pattern, reply, topic_n, prev_topic_stop, topics_sentences_flags = \
            start_new_pattern(topic_n, prev_topic_stop, topics_father, topics_children, topics_brothers,
                              topics_likeliness, topics_sentences, topics_sentences_types, topics_sentences_flags)
            # If there is a topic associated with the sentence (hence the common sentence has not been assigned yet)
            if not common_sent:
                # Check if the likeliness of the topic is zero: add a "check" sentence before making the question:
                if float(topics_likeliness[topic_n]) == 0.0:
                    common_sent = "I thought you didn't like it..."
                # If the topic doesn't have likeliness 0 or 1, add a common sentence among those to be said before questions
                elif float(topics_likeliness[topic_n]) < 1.0:
                    common_sent = random.choice(common_sent_dict['q'])
                # If the topic has likeliness 1 it will say a positive or a wait depending on the pattern, without adding
                # nothing before.

                reply = common_sent + " " + reply

    # If sentence type w, c, g
    else:
        if prev_topic_sentence_type == 'g':
            if any(word in sentence for word in pos_user_answers):
                perform_goal = 1
            elif any(word in sentence for word in neg_user_answers):
                perform_goal = -1
        else:
            # Show interest only if it's the answer to a wait during the dialogue.
            # If it's a wait as a response to an intent that set the likeliness to 1 do not show too much interest!
            if not intent_reply:
                print("SHOW INTEREST AFTER A WAIT!")
                show_interest = True

        # Check if the user's sentence is related to a topic - allow also topics with likeliness 0
        topic_n = main(sentence, id_reqs, topics_likeliness, req_par1, req_par2, tot_topic)
        # If a topic associated to the sentence is found
        if topic_n != -1:
            # If the topic is the same as the previous one
            if topic_n == prev_topic_number:
                # Try to continue with the same topic or choose a son, or end.
                sentence_type, prev_topic_pattern, reply, topic_n, prev_topic_stop, topics_sentences_flags = \
                    explore_DT("", topic_n, prev_topic_pattern, prev_topic_stop, topics_father,
                               topics_children, topics_brothers, topics_likeliness, topics_sentences,
                               topics_sentences_types, topics_sentences_flags, False)

            # If the triggered topic is not the same as the previous one, jump to that
            else:
                # Start a new pattern for the new topic
                sentence_type, prev_topic_pattern, reply, topic_n, prev_topic_stop, topics_sentences_flags = \
                    start_new_pattern(topic_n, prev_topic_stop, topics_father, topics_children, topics_brothers,
                                      topics_likeliness, topics_sentences, topics_sentences_types,
                                      topics_sentences_flags)
                # If the likeliness of the topic is 0, add a "doubt" sentence before
                if float(topics_likeliness[topic_n]) == 0.0:
                    # TODO: put these sentences in the common_sent file and choose randomly every time
                    reply = "I thought you didn't like it..." + reply

        # If no topic associated to the user's sentence is found
        else:
            print("No topic associated to the sentence found: try to continue")
            sentence_type, prev_topic_pattern, reply, topic_n, prev_topic_stop, topics_sentences_flags = \
                explore_DT("", prev_topic_number, prev_topic_pattern, prev_topic_stop, topics_father,
                           topics_children, topics_brothers, topics_likeliness, topics_sentences,
                           topics_sentences_types, topics_sentences_flags, False)
        if perform_goal == 1:
			# Or choose between gp sentences in case the goal could be accomplished
            # Actually there is the intent reply -
            # Call again the regex match service (as the answer is yes there was no previous intent matched this time)
            reply = "#" + reply
        elif perform_goal == -1:
            reply = random.choice(common_sent_dict['gn']) + " " + reply
        elif show_interest:
            reply = random.choice(common_sent_dict['w']) + " " + reply

    return sentence_type, prev_topic_pattern, reply, topic_n, prev_topic_stop, modified_topics_likeliness

@app.route("/CAIR_server")
# If the client performs a GET request, it means that the ID already exists.
def get():
    global goal_trigger_sentence
    decompressed_data = zlib.decompress(request.data)
    data = json.loads(decompressed_data.decode('utf-8'))
    client_state = data['client_state']
    sentence = data['sentence']
    # print(client_state)

    # Save all data related to the current client
    prev_topic_number = client_state["topic"]
    prev_topic_sentence_type = client_state["sentence_type"]
    prev_topic_pattern = client_state["pattern"]
    prev_topic_stop = client_state["bool"]

    modified_topics_likeliness = client_state["likelinesses"]
    print("\n-----------------------------------------------")
    print("\nMODIFIED LIKELINESSES")
    print(modified_topics_likeliness)
    topics_likeliness = {}
    for key in base_topics_likeliness.keys():
        if str(key) in modified_topics_likeliness.keys():
            topics_likeliness[key] = modified_topics_likeliness[str(key)]
        else:
            topics_likeliness[key] = base_topics_likeliness[key]

    modified_topics_sentences_flags = client_state["flags"]
    print("\nMODIFIED FLAGS")
    print(modified_topics_sentences_flags)
    topics_sentences_flags = {}
    for key in base_topics_sentences_flags.keys():
        if str(key) in modified_topics_sentences_flags.keys():
            topics_sentences_flags[key] = modified_topics_sentences_flags[str(key)]
        else:
            topics_sentences_flags[key] = base_topics_sentences_flags[key]

    do_procedure = True
    topic_n = prev_topic_number
    sentence_type = prev_topic_sentence_type
    reply = ''

    intent_reply, kbplan, plan = call_regex_matcher(sentence, prev_topic_number)

    # If a topic is found in the regex it will be replaced, and it will be passed as parameter to the procedure
    topic = sentence
    if kbplan:
        kbplan_items = kbplan.split('#')[1:]
        print(kbplan_items)
        for item in kbplan_items:
            # The action is supposed to be made of 1 word
            action = re.findall("action=(\w+)", item)[0]
            # The topic extracted could be of more than a word
            topic = re.findall("topic=(.*) (?:startsentence|value)", item)[0]
            print(topic)
            if topic:
                # Add spaces before and after the topic to have keyword match when it's just one word
                topic = " " + topic + " "
                # Setting the last parameter to true allows to return topics with zero likeliness (if no others)
                topic_n = main(topic, id_reqs, topics_likeliness, req_par1, req_par2, tot_topic)
            else:
                topic_n = -1
            if action == 'setlikeliness':
                print("---- SETLIKELINESS action ----")
                if topic_n != -1:
                    likeliness = re.findall("value=(\d+.\d+)", item)[0]
                    likeliness = float(likeliness)
                    if 0.0 < likeliness < 1.0:
                        likeliness = max(float(topics_likeliness[topic_n]), likeliness)
                    print("Setting likeliness of topic", topic_n, "to", str(likeliness))
                    topics_likeliness[topic_n] = likeliness
                    client_state["likelinesses"][str(topic_n)] = likeliness
            if action == 'jump':
                print("---- JUMP action ----")
                startsentence = re.findall("startsentence=(\w+)", item)[0]
                if startsentence == 'n':
                    do_procedure = False
                    # Set prev topic stop to false as it is not considered as saying "no" for the second time to a
                    # question. In this way it jumps to a brother if you say "I hate/I don't want to talk about"
                    prev_topic_stop = False
                    prev_topic_pattern = []
                    sentence_type, prev_topic_pattern, reply, topic_n, prev_topic_stop, topics_sentences_flags = \
                        explore_DT("", topic_n, prev_topic_pattern, prev_topic_stop, topics_father,
                                   topics_children, topics_brothers, topics_likeliness,
                                   topics_sentences, topics_sentences_types, topics_sentences_flags, True)

    if do_procedure:
        # NB: the procedure is called passing the topic extracted as parameter and not the full sentence
        sentence_type, prev_topic_pattern, reply, topic_n, prev_topic_stop, modified_topics_likeliness = \
            procedure(client_state, topic, intent_reply, topics_sentences_flags, topics_likeliness)

    # Check if there is a goal to execute before replying
    if '#' in reply:
        reply = reply.replace('#', '')
        intent_reply, kbplan, plan = call_regex_matcher(goal_trigger_sentence, prev_topic_number)

    print("Update sentence type to: ", sentence_type)
    print("Update next sentences types to: ", prev_topic_pattern)
    print("Updating topic counter with topic: ", topic_n)
    if topic_n >= 0:
        modified_topics_sentences_flags[str(topic_n)] = topics_sentences_flags[topic_n]
        print(topics_sentences_flags[topic_n])
    client_state = {"topic": topic_n,
                    "sentence_type": sentence_type,
                    "pattern": prev_topic_pattern,
                    "bool": prev_topic_stop,
                    "likelinesses": modified_topics_likeliness,
                    "flags": modified_topics_sentences_flags}

    # Delete eventual spaces at the beginning and at the end of the reply
    reply = reply.strip()
    print("The plan is", plan)
    # When the last sentence is a goal, save the second part of the sentence somewhere, in case the user says yes.
    if sentence_type == 'g':
        goal_trigger_sentence = reply.split('&')[1].strip()
        reply = reply.split('&')[0]

    data = {"client_state": client_state, "intent_reply": intent_reply, "plan": plan, "reply": reply}
    encoded_data = json.dumps(data).encode('utf-8')
    content = zlib.compress(encoded_data)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding']='deflate'
    return response


@app.route("/CAIR_server", methods=["PUT"])
# This function manages the put request which is the request made by the client the first time it connects to the
# dialogue management service.
def put():
    global init_topics
    absolute_start_topic = init_topics[0]

    sentence_type, prev_topic_pattern = choose_pattern(absolute_start_topic, base_topics_likeliness)
    # time = datetime.datetime.now()

    reply, topic_sentences_flags = choose_sentence(sentence_type, topics_sentences[absolute_start_topic],
                                                   topics_sentences_types[absolute_start_topic],
                                                   base_topics_sentences_flags[absolute_start_topic],
                                                   base_topics_likeliness[absolute_start_topic])

    client_state = {"topic": init_topics[0],
                    "sentence_type": sentence_type,
                    "pattern": prev_topic_pattern,
                    "bool": False,
                    "likelinesses": {},
                    "flags": {absolute_start_topic: topic_sentences_flags}}

    return {"client_state": client_state, "reply": reply}


if __name__ == "__main__":
    # https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
    # & openssl req - x509 - newkey rsa: 4096 - nodes - out cert.pem - keyout key.pem - days 365
    app.run(host="0.0.0.0", debug=False)
    # Default running on port 5000
    # ssl_context=('cert.pem', 'key.pem')
    # debug=True to make it restart when errors occur or changes are made
