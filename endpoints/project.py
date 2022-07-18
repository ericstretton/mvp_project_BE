from app import app
from flask import jsonify, request, Response
from helpers.data_functions import *
from helpers.db_helpers import run_query



@app.get('/api/project')
def project_get():
    # org owners can view all projects within their company
    #proj_managers and employees can view all projects they are associated to 
    token = request.headers.get('token')
    params = request.args
    auth_level = get_authorization(token)
    if auth_level == 'invalid':
        return jsonify('ERROR, invalid token submitted'), 400
    
    if auth_level == 'org_owner' or auth_level == 'proj_man' or auth_level == 'employee':
        if len(params.keys()) == 0:
        
            user_id = run_query('SELECT user_id FROM user_session WHERE token=? ', [token])
            #get all company projects
            company_id = run_query('SELECT company_id FROM user WHERE id=? ', [user_id[0][0]])
            project = run_query('SELECT project_id FROM company WHERE id =?', [company_id[0][0]])
            project_info = run_query('SELECT * FROM project WHERE id=?', [project[0][0]])
            
            get_project_info = []
            info = populate_project_dict(project_info[0])
            get_project_info.append(info)
            
            return jsonify(get_project_info)
        if len(params.keys()) ==1:
            project_id = params.get('project_id')
            project_info = run_query('SELECT * FROM project WHERE id=?', [project_id])
            
            get_single_project = []
            info = populate_project_dict(project_info[0])
            get_single_project.append(info)
            return jsonify(get_single_project)
            
    return 


@app.post('/api/project')
def project_post():
    # only org_owners can create new projects and assign proj_managers
    data = request.json
    params = request.args
    token = params.get('token')
    
    auth_level = get_authorization(token)
    if auth_level == 'invalid':
        return jsonify('ERROR, invalid token submitted'), 400
    
    if auth_level != 'org_owner':
        return jsonify('ERROR, not authorized to create a project'), 401
    
    if len(data.keys()) >= 3 and len(data.keys()) <= 7:
        new_project = new_dictionary_request(data)
    else:
        return jsonify('ERROR, invalid amount of submitted keys'), 400
    
    # Required keys to have are: name, estimated_completion_date, project_manager
    # Additional accepted keys are: description, initial_budget, current_budget
    
    if 'name' in new_project:
        if not check_length(new_project['name'], 1, 75):
            return jsonify('ERROR, project name submitted is an invalid length, must be between 1 and 75 characters')
    else:
        return jsonify('ERROR, name is required to create a project'), 401
    
    if 'estimated_completion_date' in new_project:
        # Regex to check if the syntax submitted for the estimated project completion date is correctly formatted
        if not check_date(new_project['estimated_completion_date']):
            return jsonify('ERROR, date syntax is incorrectly formatted. Try XXXX-XX-XX'), 400
    else:
        return jsonify('ERROR, estimated_completion_date is required to complete a project'), 401
    
    if 'project_manager' in new_project:
        # check that the user id selected is of level 2 authorization
        # use reference table to compare the id with authorization
        auth_level = run_query('SELECT authorization FROM user WHERE id=?', [new_project['project_manager']])
        level_name = run_query('SELECT level FROM authorization INNER JOIN user ON authorization.id = user.authorization WHERE authorization.id=?', [auth_level[0][0]])
        if level_name[0][0] != 'proj_man':
            return jsonify('ERROR, project managers must be appropriate authorization level "2"')

    
    if not 'description' in new_project:
        run_query('INSERT INTO project (name, estimated_completion_date, project_manager) VALUES (?,?,?) ', \
        [new_project['name'], new_project['estimated_completion_date'], new_project['project_manager']])
    
        request_new_project = run_query('SELECT id, name, start_date, estimated_completion_date, description, project_manager, status_id FROM project WHERE name=?', [new_project['name']])
        
        list_new_project = []
        project = populate_project_dict(request_new_project[0])
        list_new_project.append(project)
        
        return jsonify('New Project Created,', list_new_project[0]), 201
    else:
        if 'description' in new_project:
            if not check_length(new_project['description'], 1, 200):
                return jsonify('ERROR, description must be between 1 and 200 characters')
        run_query('INSERT INTO project (name, estimated_completion_date, project_manager, description) VALUES (?,?,?,?) ', \
            [new_project['name'], new_project['estimated_completion_date'], new_project['project_manager'], new_project['description']])
        request_new_project = run_query('SELECT id, name, start_date, estimated_completion_date, description, project_manager, status_id FROM project WHERE name=?', [new_project['name']])

        list_new_project = []
        project = populate_project_dict(request_new_project[0])
        list_new_project.append(project)

        return jsonify('New Project Created,', list_new_project[0]), 201
        
    

@app.patch('/api/project')
def project_patch():
    #only org_owners and proj managers can update projects
    #proj_managers have a select amount of updates they can run compared to org_owners
    #TODO: ADD updates for project information on both accounts
    
    token = request.headers.get('token')
    params = request.args
    data = request.json
    project_id = params.get('project_id')
    
    auth_level = get_authorization(token)
    if auth_level == 'invalid':
        return jsonify('ERROR, invalid token submitted'), 400
    if auth_level == 'org_owner':
        if len(data.keys()) >= 1 and len(data.keys()) <=2:
            update_project = new_dictionary_request(data)
            if 'status_id' in update_project:
                if str(update_project['status_id']).isdigit() == False:
                    return jsonify('ERROR, status_id must be a digit between 1 and 3')
                
            if not 'project_manager' in update_project:
                run_query('UPDATE project SET status_id=? WHERE id=?', [update_project['status_id'], project_id])
            
            elif 'project_manager' in update_project:
                auth_level = run_query('SELECT authorization FROM user WHERE id=?', [update_project['project_manager']])
                level_name = run_query('SELECT level FROM authorization INNER JOIN user ON authorization.id = user.authorization WHERE authorization.id=?', [auth_level[0][0]])
                if level_name[0][0] != 'proj_man':
                    return jsonify('ERROR, project managers must be appropriate authorization level "2"')
                run_query('UPDATE project SET status_id=?, project_manager=? WHERE id=?', [update_project['status_id'], update_project['project_manager'], project_id])
                
    elif auth_level == 'proj_man':
        
        update_project = new_dictionary_request(data)
        if 'status_id' in update_project:
            if str(update_project['status_id']).isdigit() == False:
                return jsonify('ERROR, status_id must be a digit between 1 and 3')
        run_query('UPDATE project SET status_id=? WHERE id=?', [update_project['status_id'], project_id])
            
            
    request_updated_project = run_query('SELECT id, name, start_date, estimated_completion_date, description, project_manager, status_id FROM project WHERE id=?', [project_id])
    
    list_updated_project = []
    project = populate_project_dict(request_updated_project[0])
    list_updated_project.append(project)

    return jsonify('New Project Created,', list_updated_project[0]), 201


