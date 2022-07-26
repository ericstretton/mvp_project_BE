
from app import app
from flask import jsonify, request
from helpers.data_functions import *
from helpers.db_helpers import run_query
import bcrypt
from uuid import uuid4


@app.get('/api/user')

def user_get():
    # employees can view their information, project-managers and org_owners can view there info and authorizations below users
    
    token = request.headers.get('token')
    params = request.args
    
    auth_level = get_authorization(token)
    if auth_level == 'invalid':
        return jsonify('ERROR, invalid token submitted'), 400
    
    
    if auth_level == 'org_owner' or auth_level == 'proj_man':
        if len(params.keys()) == 0:
            accessing_users_id = run_query('SELECT user_id FROM user_session WHERE token=?', [token])
            company_reference = run_query('SELECT company_id FROM user WHERE id=?', [accessing_users_id[0][0]])
            all_staff = run_query('SELECT id, email, firstName, lastName, pictureURL, authorization, title, employee_start_date FROM user WHERE company_id=?', [company_reference[0][0]])
            all_staff_list = []
            for staff in all_staff:
                user = populate_user_dict(staff)
                all_staff_list.append(user)
            
            return jsonify(all_staff_list), 200
        
        elif len(params.keys()) == 1:
            user_id = params.get('user_id')
            user_id_int = int(user_id)
            
            if user_id != None:
                if str(user_id).isdigit() == False:
                    return jsonify('ERROR, submitted param must be a number for a user Id'), 400
            else:
                return jsonify('User Id must be sent for individual lookup'), 400
            
            user_id_check = run_query('SELECT id FROM user WHERE id=?', [user_id])
            
            if user_id_check[0][0] == user_id_int:
                user_checked = run_query('SELECT id, email, firstName, lastName, pictureURL, authorization, title, employee_start_date FROM user WHERE id=?', [user_id])
                user_info = []
                
                user = populate_user_dict(user_checked[0])
                user_info.append(user)
                
                return jsonify(user_info[0]), 200
            else:
                return jsonify('ERROR, requested user_id does not exist in the database'), 400
        else:
            return jsonify('ERROR, incorrect data was sent')
        
    elif auth_level == 'employee':
        accessing_users_id = run_query('SELECT user_id FROM user_session WHERE token=?', [token])
        user_information = run_query('SELECT id, email, firstName, lastName, pictureURL, authorization, title, employee_start_date FROM user WHERE id=?', [accessing_users_id[0][0]])
        
        user_info = []
        user = populate_user_dict(user_information[0])
        user_info.append(user)
        
        return jsonify(user_info), 200
    else:
        return jsonify('ERROR, invalid authorization level'), 400




@app.post('/api/user')

def user_post():
    
    #Only org_owners can create new proj_man users
    
    #only org_owners and proj_man can create new employee users
    data = request.json
    params = request.args
    token = params.get('token')
    
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
        
        #TODO: apply reference table to get the numeric id value for users authorization
        
        if new_user['authorization'] == 'proj_man' and auth_level != 'org_owner':
            return jsonify('ERROR, only organization owners are permitted to create new project managers'), 401
    else: 
        return jsonify('ERROR, authorization is required to create a new user'), 400
    
    if 'title' in new_user:
        if not check_length(new_user['title'], 1, 100):
            return jsonify('ERROR, title must be between 1 and 100 characters'), 400
    else:
        return jsonify('ERROR, title is required to create a new user')
    
    
    
    # use cross reference to convert the authorization level to its digit identifier
    
    auth_level_num = run_query('SELECT id FROM authorization WHERE level=?', [new_user['authorization']])
    run_query('INSERT INTO user(email, password, firstName, lastName, authorization, title) VALUES (?,?,?,?,?,?)', \
        [new_user['email'], hash_pass, new_user['firstName'], new_user['lastName'], auth_level_num[0][0], new_user['title']])
    
    new_user_id = run_query('SELECT id FROM user WHERE email=?', [new_user['email']])
    
    
    request_new_user = run_query("SELECT id, email, firstName, lastName, pictureURL, authorization, title, employee_start_date FROM user WHERE id=?", [new_user_id[0][0]])
    list_new_user = []
    
    user = populate_user_dict(request_new_user[0])
    list_new_user.append(user)
    
    return jsonify("new user created", list_new_user),201

@app.patch('/api/user')

def user_patch():
    #employees can update their password only
    # project_managers can update employee information, except the password and can update their own password
    # org_owners can update employee and project_managers info, except the passwords and can update any of their information
    
    data = request.json
    token = data.get('token')
    user_id = data.get('user_id')
    
    if user_id != None:
        if str(user_id).isdigit() == False:
            return jsonify('ERROR, submitted param must be a number for a user Id'), 400
    else:
        return jsonify('User Id must be sent for individual lookup'), 400
    
    auth_level = get_authorization(token)
    if auth_level == 'invalid':
        return jsonify('Invalid token submitted'), 400
    
    if auth_level == 'employee':
        check_user = run_query('SELECT user_id FROM user_session WHERE user_id=? and token=? ', [user_id, token])
        
        if check_user[0][0] != int(user_id):
            return jsonify('ERROR, user not authorized to update this profile'), 400
        
        if len(data.keys()) == 3 and {'token', 'user_id', 'password'} <= data.keys():
            
            user_update = new_dictionary_request(data)
            
            if 'password' in user_update:
                
                #TODO: apply check to see if new password matches old password - this is not allowed
                
                if not check_length(user_update['password'], 6, 75):
                    return jsonify('ERROR, password must be between 6 and 75 characters'), 400
        
                password = user_update['password']
                salt = bcrypt.gensalt()
                hash_pass = bcrypt.hashpw(str(password).encode(), salt)

                run_query('UPDATE user SET password=? WHERE id=?', [hash_pass, user_id])
                
                get_updated_user = run_query('SELECT id, email, firstName, lastName, pictureURL, authorization, title, employee_start_date FROM user WHERE id=?', [user_id])
                
                user_info = []
                info = populate_user_dict(get_updated_user[0])
                user_info.append(info)
                
                return jsonify(user_info[0]), 400
            else:
                return jsonify('ERROR, a new password must be sent for and a password update.')
        else:
            return jsonify('ERROR, invalid keys submitted')
        
    elif auth_level == 'proj_man':
        
        
        # a project_manager can update their password firstly
        
        
        if len(data.keys()) == 3 and {'token', 'user_id', 'password'} <= data.keys():
            
            check_user = run_query('SELECT user_id FROM user_session WHERE user_id=? and token=? ', [user_id, token])
            if check_user[0][0] != int(user_id):
                return jsonify('ERROR, user not authorized to update this profile'), 400
            
            user_update = new_dictionary_request(data)
            
            if 'password' in user_update:
                
                #TODO: apply check to see if new password matches old password - this is not allowed
                
                if not check_length(user_update['password'], 6, 75):
                    return jsonify('ERROR, password must be between 6 and 75 characters'), 400
        
                password = user_update['password']
                salt = bcrypt.gensalt()
                hash_pass = bcrypt.hashpw(str(password).encode(), salt)

                run_query('UPDATE user SET password=? WHERE id=?', [hash_pass, user_id])
                
                get_updated_user = run_query('SELECT id, email, firstName, lastName, pictureURL, authorization, title, employee_start_date FROM user WHERE id=?', [user_id])
                
                user_info = []
                info = populate_user_dict(get_updated_user[0])
                user_info.append(info)
                
                return jsonify(user_info[0]), 400
            else:
                return jsonify('ERROR, a new password must be sent for and a password update.')
        
        #otherwise a project manager can update a user in their company and they can update that users email, firstName, lastName, pictureURL and title
        elif len(data.keys()) >= 3 and len(data.keys()) <= 7:
            user_update = new_dictionary_request(data)

            if 'email' in user_update:
                if not check_email(user_update['email']):
                    return jsonify('ERROR, invalid email address submitted')
                if not check_length(user_update['email'], 1, 75):
                    return jsonify('ERROR, email must be between 1 and 75 characters'), 400
                
                email_exists = run_query('SELECT email FROM user WHERE email=?', [user_update['email']])
                if email_exists[0][0] == user_update['email']:
                    return jsonify('ERROR, email already exists in the system.'), 400
                
        else:
            return jsonify('ERROR, Invalid amount of keys submitted'), 400
            
    elif auth_level == 'org_owner':
    
        if len(data.keys()) == 3 and {'token', 'user_id', 'password'} <= data.keys():

            check_user = run_query('SELECT user_id FROM user_session WHERE user_id=? and token=? ', [user_id, token])
        
            if check_user[0][0] != int(user_id):
                return jsonify('ERROR, user not authorized to update this profile'), 400
            
            
            
            
            
            
@app.delete('/api/user')

def user_delete():
    #org_owners and project_managers cannot be deleted
    # employees and can be deleted - all other fields they are in must be deleted as well
    
    data = request.json
    token = data.get('token')
    user_id = data.get('user_id')
    
    if user_id != None:
        if str(user_id).isdigit() == False:
            return jsonify('ERROR, user_id has to be a valid identifying number in the database'), 400
    else:
        return jsonify('ERROR, a user_id is required for user deletion'), 400
    
    check_user_id = run_query('SELECT id FROM user WHERE id=?', [int(user_id)])
    if check_user_id[0][0] != int(user_id):
        return jsonify('ERROR, user_id not found'), 400
    
    auth_level = get_authorization(token)
    if auth_level == 'invalid':
        return jsonify('ERROR, token is invalid'), 400
    
    if auth_level == 'employee':
        return jsonify('ERROR, user is not authorized for user deletion'), 401
    
    user_id_auth = run_query('SELECT authorization FROM user WHERE id=?', [user_id])
    
    if (auth_level == 'org_owner' or auth_level == 'proj_man') and (user_id_auth[0][0] == 'org_man' or user_id_auth[0][0] == 'proj_man'):
        return jsonify('ERROR, org_owners and proj_managers cannot be deleted')
    
    
    # The user must then be logged out
    run_query('DELETE  FROM user_session WHERE user_id=?', [user_id])
    
    
    run_query('DELETE  FROM user WHERE id=?', [user_id])
    return jsonify('User deleted'), 204
    