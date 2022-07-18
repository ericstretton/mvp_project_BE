import re
from flask import jsonify
from helpers.db_helpers import run_query

#For User Authorization

def get_authorization(token):
    token_valid = run_query("SELECT token FROM user_session WHERE token=?", [token])
    validity_response = token_valid[0][0]
    if validity_response == token:
        auth_level = run_query("SELECT authorization FROM user INNER JOIN user_session ON user.id = user_session.user_id WHERE token=?", [token])
        level_name = run_query('SELECT level FROM authorization INNER JOIN user ON authorization.id = user.authorization WHERE authorization.id=?', [auth_level[0][0]])
        return level_name[0][0]
    else:
        return "invalid authorization"
    
    
def populate_user_dict(data):
    user = {
        "userId" : data[0],
        "email" : data[1],
        "firstName" : data[2],
        "lastName" : data[3],
        "pictureURL" : data[4],
        "authorization" : data[5],
        "title" : data[6],
        "employee_start_date" : data[7]
    }
    return user
    
    
def populate_company_dict(data):
    company = {
        "companyId" : data[0],
        "name" : data[1],
        "org_owner" : data[2],
        "email" : data[3],
        "phoneNum" : data[4],
        "pictureURL" : data[5],
        "project_id" : data[6],
        "address" : data[7]
    }
    return company
    
def populate_project_dict(data):
    project = {
        "projectId" : data[0],
        "name" : data[1],
        "start_date" : data[2],
        "estimated_completion_date" : data[3],
        "description" : data[4],
        "project_manager" : data[5],
        "statusId" : data[6]
    }
    return project




#Helper function, regex email - qualifies submitted emails 
def check_email(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$' 
    if(re.search(regex, email)):
        return True
    else:
        return False
    
def check_phoneNum(phoneNum):
    regex = '^\(?([0-9]{3})\)?[-.●]?([0-9]{3})[-.●]?([0-9]{4})$'
    if(re.search(regex, phoneNum)):
        return True
    else:
        return False

def check_date(date):
    regex = '^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$'
    if(re.search(regex, date)):
        return True
    else:
        return False


    
def check_length(input, min_len, max_len):
    if len(input) >= min_len and len(input) <= max_len:
        return True
    else:
        return False

#Helper function that removes leading and trailing whitespaces - created fro json reqest data
def new_dictionary_request(data):
    new_dict = {}
    for k,v in data.items():
        new_dict[k] = str(v).strip()
    return new_dict