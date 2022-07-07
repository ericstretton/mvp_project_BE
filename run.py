from app import app
from flask import Flask
from flask_cors import CORS
import sys

if len(sys.argv) > 1:
    mode = sys.argv[1]
else:
    print("Missing required mode argument")
    exit()
if mode == 'testing':
    CORS(app)
    app.run(debug=True)
elif mode == 'production':
    import bjoern
    bjoern.run(app, "0.0.0.0", 5500)
else:
    print("Mode must be in testing|production")
    exit()