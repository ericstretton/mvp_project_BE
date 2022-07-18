from app import app
from flask import jsonify, request, Response
from helpers.data_functions import *
from helpers.db_helpers import run_query


@app.get('/api/task')

def task_get():
    #proj_man and org owners can view all tasks
    # users can view their tasks
    return


@app.post('/api/task')
def task_post():
    # Only a proj_man or org_owner can create and assign tasks to users
    params = request.args
    data = request.json
    
    token = params.get('token')
    auth_level = get_authorization(token)
    
    if auth_level == 'invalid':
        return jsonify('ERROR, invalid token submitted'), 400
    if auth_level != 'org_owner' and auth_level != 'proj_man':
        return jsonify('ERROR, your user credentials are not authorized to create a task'), 401
    
    if len(data.keys()) >= 3 and len(data.keys()) <= 4:
        new_task = new_dictionary_request(data)
    else:
        return jsonify('ERROR, invalid amount of submitted keys'), 400
    
    if 'name' in new_task:
        if not check_length(new_task['name'], 1, 125):
            return jsonify('ERROR, task name is an invalid length, must be between 1 and 125 characters')
        
    if 'user_id' in new_task:
        check_is_user = run_query('SELECT id FROM user WHERE id=?', [new_task['user_id']])
        
        if check_is_user != []:
            user_id = check_is_user[0][0]
            if user_id == new_task['user_id']:
                return
        else:
            return jsonify('ERROR, user_id not found in database'), 400
    else:
        return jsonify('ERROR, user_id is required to create a task'), 401
    return


@app.patch('/api/task')
def task_patch():
    # A proj_man or org_owner and the user with assigned userId can update select fields 
    
    return