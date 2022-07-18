from flask import Flask

app = Flask(__name__)

from endpoints import company,  project, task_comment, user_session, user, task