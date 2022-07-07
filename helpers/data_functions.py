import re
from helpers.db_helpers import run_query

#For User Authorization

def get_authorization(token):
    token_valid = run_query("SELECT user_id FRO user_session WHERE token=?", [token])
    if token_valid == token:
        auth_level = ("SELECT authorization FROM user INNER JOIN user_session ON user.id = user_session.user_id WHERE token=?", [token])
        
        return auth_level[0]
    else:
        return "invalid authorization"
    
    
    
    
    


#Helper function, regex email - qualifies submitted emails 
def check_email(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$' 
    if(re.search(regex, email)):
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