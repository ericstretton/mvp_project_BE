from flask import Flask

app = Flask(__name__)

from endpoints import company, post_comment, post, project, user_session, user