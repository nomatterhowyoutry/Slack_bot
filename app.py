# -*- coding: utf-8 -*-

import json
import bot
import re
from flask import Flask, request, make_response, render_template

pyBot = bot.Bot()
slack = pyBot.client

app = Flask(__name__)


def _event_handler(event_type, slack_event):
    
    if event_type == "message":
        message = slack_event['event']['text']
        message = re.sub(r'(\!)+|(\?)+|(\.)+|(\,)+|(\;)+|(\")+|(\')+', '', message)
        grettings = ['hello', 'hi', 'hey', 'grettings', 'good morning', 'good evening']
        if message.lower() in  grettings and not 'bot_id' in slack_event['event']:
            print('messaging')
            channel = slack_event["event"]["channel"]
            message = 'hello'
            slack.api_call(
                 "chat.postMessage",
                 channel=channel,
                 text=message
            )
        return make_response("Welcome message updates with pin", 200,)

    message = "You have not added an event handler for the %s" % event_type

    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/install", methods=["GET"])
def pre_install():
    client_id = pyBot.oauth["client_id"]
    return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    code_arg = request.args.get('code')
    pyBot.auth(code_arg)
    return render_template("thanks.html")


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                             })

    if pyBot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], pyBot.verification)

        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]

        return _event_handler(event_type, slack_event)

    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


if __name__ == '__main__':
    app.run(debug=True)
