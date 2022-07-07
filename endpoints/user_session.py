import json
from app import app
from flask import jsonify, request
from helpers.db_helpers import run_query
from helpers.data_functions import *
import bcrypt
from uuid import uuid4


@app.post('/api/user_session')

def user_session_post():
    data = request.json
    
    if len(data.keys()) == 2 and {'email', 'password'} <= data.keys():
        email = data.get('email')
        password = data.get('password')
        
        if not check_email(email):
            return jsonify('ERROR, not a valid email'), 400
        
        valid_email = run_query('SELECT email FROM user WHERE email=?', [email])
        
        if valid_email == email:
            
            user_password = run_query('SELECT password FROM user WHERE email=?', [email])
            
            if bcrypt.checkpw(str(password).encode(), str(user_password.encode())):
                user_id = run_query('SELECT id FROM user WHERE email=?', [email])
                token = uuid4()
                
                resp = []
                for id in user_id:
                    userId = {}
                    userId = id[0]
                    resp.append(userId)
                    resp.append(token)
                    
                run_query('INSERT INTO user_session(user_id, token) VALUES(?,?)', [user_id[0], token])
                
                return jsonify(resp), 201
            else:
                return jsonify('ERROR invalid login credentials'), 400
        else:
            return jsonify('ERROR, email does not exist in the database'), 404
    else:
        return jsonify('ERROR, incorrect keys submitted'), 400
      

@app.delete('/api/user_session')

def user_session_delete():
    data = request.json
    
    if len(data.keys()) == 1 and {'token'} <=data.keys():
        token = data.get('token')
    
        token_valid = run_query('SELECT token FROM user_session WHERE token=?', [token])
        
        if token_valid == token:
            run_query('DELETE FROM user_session WHERE token=?', [token])
            return jsonify('Log-out Successful'), 201
        else:
            return jsonify('ERORR, Invalid token submitted'), 400
    else:
        return jsonify('ERROR, incorrect keys submitted'), 400
    