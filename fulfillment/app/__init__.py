from flask import Flask
from app.dialogflow import DialogFlow
from .refer_mock import ReferMock

app = Flask(__name__)
dialogflow = DialogFlow(app, '/webhook', 'handson', 'hocoChatBot');
refer_mock = ReferMock('db.sqlite')

from app import actions
