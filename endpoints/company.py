
from app import app
from flask import jsonify, request, Response
from helpers.data_functions import *
from helpers.db_helpers import run_query



@app.get('/api/company')

def company_get():
    # takes the parameters of a login session token - query for the company_id - the get request displays the company information for that user
    params = request.args
    token = request.headers.get('token')
    
    auth_level = get_authorization(token)
    
    if auth_level == 'invalid':
        return jsonify('ERROR, invalid token submitted'), 400
    if auth_level == 'org_owner' or auth_level == 'proj_man' or auth_level == 'employee':
        if len(params.keys()) == 0:
            user_id = run_query('SELECT user_id FROM user_session WHERE token=?', [token])
            company_id = run_query('SELECT company_id FROM user WHERE id=?', [user_id[0][0]])
            company = run_query('SELECT company.id, company.name, user.lastName, company.email, company.phoneNum, company.pictureURL, company.project_id, company.address FROM company RIGHT JOIN user ON company.id=user.company_id WHERE company.id=?', [company_id[0][0]])
            
            company_info = []
            info = populate_company_dict(company[0])
            company_info.append(info)
            return jsonify(company_info)
        else:
            return jsonify('ERROR to access company information only headers are necessary, no parameters'), 400
    
    else:
        return jsonify('ERROR, you have to be associated with a proper authorization level to access company information'), 400

@app.post('/api/company')

def company_post():
    
    #Only an org_owner can post a new company and a org_owner can only have one company 
    data = request.json
    params = request.args
    token = params.get('token')
    
    auth_level = get_authorization(token)
    
    if auth_level == 'invalid':
        return jsonify('ERROR, invalid token submitted'), 400
    
    if auth_level != 'org_owner':
        return jsonify('ERROR, not authorized to create a company'), 401
    
    if len(data.keys()) >= 3 and len(data.keys()) <= 4:
        new_company = new_dictionary_request(data)
    else:
        return jsonify('ERROR, invalid amount of submitted keys'), 400
    
    if 'name' in new_company:
        if not check_length(new_company['name'], 1, 125):
            return jsonify('ERROR, name submitted is an invalid length, must be between 1 and 125 characters'), 400
    else:
        return jsonify('ERROR, name is required to create a company'), 401
    
    auth_number = run_query('SELECT id FROM authorization WHERE level=?', [auth_level])
    sessions_user_id = run_query('SELECT user_id FROM user_session WHERE token=?', [token])
    verified_requesting_userId = run_query('SELECT id FROM user WHERE id=? and authorization=?', [sessions_user_id[0][0], auth_number[0][0]])
    
    if 'email' in new_company:
        if not check_length(new_company['name'], 1, 125):
            return jsonify('ERROR, name submitted is an invalid length, must be between 1 and 125 characters'), 400
    else:
        return jsonify('ERROR, email is required to create a company'), 401
    
    # Regex to check if the syntax submitted for phoneNum follows North American phone formatting
    if 'phoneNum' in new_company:
        if not check_phoneNum(new_company['phoneNum']):
            return jsonify('ERROR, phoneNum submitted is invalid'), 400
    else:
        return jsonify('ERROR, phoneNum is required to create a company'), 401  
    
    # create optional endpoints for address and pictureURL
    
    if 'address' in new_company:
        if not check_length(new_company['address'], 1, 100):
            return jsonify('ERROR address must be between 1 and 100 characters'), 400
        
    if 'pictureURL' in new_company:
        if not check_length(new_company['pictureURL'], 1, 300):
            return jsonify('ERROR pictureURL must be between 1 and 300 characters'), 400
    
    run_query('INSERT INTO company(name, org_owner, email, phoneNum) VALUES (?,?,?,?)', \
        [new_company['name'], verified_requesting_userId[0][0], new_company['email'], new_company['phoneNum'] ])
    
    request_new_company = run_query('SELECT * FROM company WHERE org_owner=?', [verified_requesting_userId[0][0]])
        
    list_new_company = []
    
    company = populate_company_dict(request_new_company[0])
    list_new_company.append(company)
    
    return jsonify('Congratulations org_owner, your company has been initialized', list_new_company), 201
        
@app.patch('/api/company')
def company_patch():
    #only a org_owner can update their companies information
    # can update the address, pictureURL and project_id
    # Takes information from login session token
    data = request.json
    token = request.headers.get('token')
    
    auth_level = get_authorization(token)
    if auth_level == 'invalid':
        return jsonify('ERROR, invalid token submitted'), 400
    if auth_level == 'org_owner':
        if len(data.keys()) >= 1 and len(data.keys()) <= 3:
            user_id = run_query('SELECT user_id FROM user_session WHERE token=?', [token])
            company_id = run_query('SELECT company_id FROM user WHERE id=?', [user_id[0][0]])
        
            update_company = new_dictionary_request(data)
            if 'address' in update_company:
                if not check_length(update_company['address'], 1, 100):
                    jsonify('ERROR, address invalid length, characters should be between 1 and 100'), 400
            run_query('UPDATE company SET address=? WHERE id=?', [update_company['address'], company_id[0][0]])
                
            if 'pictureURL' in update_company:
                if not check_length(update_company['pictureURL'], 1, 300):
                    jsonify('ERROR pictureURL must be between 1 and 300 characters')
            run_query('UPDATE company SET pictureURL=? WHERE id=? ', [update_company['pictureURL'], company_id[0][0]])
            
                    
            if 'project_id' in update_company:
                if str(update_company['project_id']).isdigit() == False:
                    return jsonify('ERROR, project_id must be submitted as a digit')
            run_query('UPDATE company SET project_id=? WHERE id=? ', [update_company['project_id'], company_id[0][0]])
            
            updated_company = run_query('SELECT company.id, company.name, user.lastName, company.email, company.phoneNum, company.pictureURL, company.project_id, company.address FROM company RIGHT JOIN user ON company.id=user.company_id WHERE company.id=?', [company_id[0][0]])
            company_info = []
            info = populate_company_dict(updated_company[0])
            company_info.append(info)
            return jsonify(company_info)
            
        else:
            jsonify('ERROR an invalid amount of keys where selected to be updated.')

        
    else:
        jsonify('ERROR, you need to be an organization owner to update company information')
    