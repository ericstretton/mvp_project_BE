import json
from app import app
from flask import jsonify, request
from helpers.data_functions import *
from helpers.db_helpers import  run_query


@app.get('/api/task')

def task_get():
    #proj_man and org owners can view all tasks
    # users can view their tasks
    #If a user has no tasks a message for you have no tasks will come up 
    
    
    params = request.args
    token = request.headers.get('token')
    
    auth_level = get_authorization(token)
    
    if auth_level == 'invalid':
        return jsonify('ERROR, invalid token submitted'), 400
    if  auth_level == 'employee' or auth_level == 'proj_man':
        
        if len(params.keys()) == 0:
            user_id = run_query('SELECT user_id FROM user_session WHERE token=?', [token])
            user_tasks = run_query('SELECT * FROM task WHERE user_id=?', [user_id[0][0]])
            
            user_tasks_list = []
            for t in user_tasks:
                task = populate_task_dict(t)
                user_tasks_list.append(task)
            return jsonify(user_tasks_list)
        
        elif len(params.keys()) == 1:
            task_id = params.get('task_id')
            selected_task = run_query('SELECT * FROM task WHERE id=?', [task_id])
            
            task_info = []
            task = populate_task_dict(selected_task[0])
            task_info.append(task)
            return jsonify(task_info)
            
        else:
            return jsonify("ERROR, incorrect keys submitted"), 400
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
            if user_id != int(new_task['user_id']):
                
                return jsonify('ERROR, user selected does not match the database query'), 400
        else:
            return jsonify('ERROR, user_id not found in database'), 400
    else:
        return jsonify('ERROR, user_id is required to create a task'), 401
    
    if 'project_id' in new_task:
        check_project = run_query('SELECT id FROM project WHERE id=?', [new_task['project_id']])
        
        if check_project != []:
            if check_project[0][0] != int(new_task['project_id']):
                return jsonify('ERROR, project selected does not match the database query'), 400
        else:
            return jsonify('ERROR, project not found in the database'), 400
    else:
        return jsonify('ERROR, project_id is required to create a task')
    
    if not 'instructions' in new_task:
        run_query('INSERT INTO task (name, user_id, project_id) VALUES (?,?,?)', \
            [new_task['name'], new_task['user_id'], new_task['project_id']])
        request_new_task = run_query('SELECT * FROM task WHERE name=?', [new_task['name']])
        
        list_new_task = []
        
        task = populate_task_dict(request_new_task[-1])
        list_new_task.append(task)
        
        return jsonify('Task created, ', list_new_task), 201
    elif 'instructions' in new_task:
        if not check_length(new_task['instructions'], 1, 250):
            return jsonify('ERROR, instructions must be between 1 and 250 characters'), 400
        run_query('INSERT INTO task (name, user_id, project_id, instructions) VALUES (?,?,?,?)', \
            [new_task['name'], new_task['user_id'], new_task['project_id'], new_task['instructions']])
        
        request_new_task = run_query('SELECT * FROM task WHERE name=?', [new_task['name']])
        
        list_new_task = []
        
        task = populate_task_dict(request_new_task[-1])
        list_new_task.append(task)
        
        return jsonify('Task created, ', list_new_task), 201
        
        
    


@app.patch('/api/task')
def task_patch():
    # A proj_man or org_owner and the user with assigned userId can update select fields 
    
    return