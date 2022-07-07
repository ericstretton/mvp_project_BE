import json
from app import app
from flask import jsonify, request, Response
from helpers.data_functions import *
from helpers.db_helpers import run_query
import bcrypt
from uuid import uuid4


@app.get('/api/user')

def user_get():
    
    return




@app.post('/api/user')

def user_post():
    
    #Only org_owners can create new proj_man users
    
    #only org_owners and proj_man can create new employee users
    data = request.json
    token = data.get('token')
    
    auth_level = get_authorization(token)
    
    if auth_level == 'invalid':
        return jsonify('ERROR, invalid token submitted'), 400
    
    if auth_level != 'proj_man' and auth_level != 'org_owner':
        return jsonify('ERROR, not authorized to create a new user'), 401
    
    
    #What is needed for a new user creation? authorization, firstName, lastName, email, password, title
    #What are the optional fields? employee_start_date, pictureURL
    if len(data.keys()) >= 6 and len(data.keys()) <= 8:
        new_user = new_dictionary_request(data)
    else:
        return jsonify('ERROR, invalid amount of submitted keys'), 400
    
    
    if 'email' in new_user:
        if not check_email(new_user['email']):
            return jsonify('ERROR, invalid email address submitted'), 400
        if not check_length(new_user['email'], 5, 75):
            return jsonify('ERROR, email submitted is an invalid length, must be between 5 and 75 characters'), 400
        
        email_exists = run_query('SELECT email FROM user WHERE email=?', [new_user['email']])
        if email_exists == new_user['email']:
            return jsonify('ERROR, email already exists in the system.'), 400
    else:
        return jsonify('ERROR, email is required to create a new user')
    
    
    if 'password' in new_user:
        if not check_length(new_user['password'], 6, 75):
            return jsonify('ERROR, password must be between 6 and 75 characters'), 400
        
        password = new_user['password']
        salt = bcrypt.gensalt()
        hash_pass = bcrypt.hashpw(str(password).encode(), salt)
    else:
        return jsonify('ERROR, password is required to create a new user')
    

    if 'firstName' in new_user:
        if not check_length(new_user['firstName'], 1, 50):
            return jsonify('ERROR, firstName must be between 1 and 50 characters'), 400
    else:
        return jsonify('ERROR, firstName is required to create and new user')
    
    
    if 'lastName' in new_user:
        if not check_length(new_user['lastName'], 1, 75):
            return jsonify('ERROR, lastName must be between 1 and 75 characters'), 400
    else:
        return jsonify('ERROR, lastName is required to create a new user'), 400
    
    if 'authorization' in new_user:
        
        if  new_user['authorization'] != 'proj_man' and new_user['authorization'] != 'employee':
            return jsonify('Invalid authorization level. Acceptable inputs are: proj_man or employee')
        
        if new_user['authorization'] == 'proj_man' and auth_level != 'org_owner':
            return jsonify('ERROR, only organization owners are permitted to create new project managers'), 401
    else: 
        return jsonify('ERROR, authorization is required to create a new user'), 400
    
    if 'title' in new_user:
        if not check_length(new_user['title'], 1, 100):
            return jsonify('ERROR, title must be between 1 and 100 characters'), 400
    else:
        return jsonify('ERROR, title is required to create a new user')
    
    

@app.patch('/api/user')

def user_patch():
    
    return



@app.delete('/api/user')

def user_delete():
    
    return