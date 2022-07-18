from dbcreds import *
import mariadb

def connect_db():
    conn=None
    cursor=None

    try:
        conn = mariadb.connect(
                                host=host,
                                port=port,
                                database=database,
                                user=user,
                                password = password
                                )
        cursor = conn.cursor()
        return (conn, cursor)
    except mariadb.OperationalError as e:
        print("Got an operational Error")
        if("Access denied" in e.msg):
            print("Failed to log-in")
        disconnect_db()
        
    
    

def disconnect_db(conn, cursor):
    if(cursor != None):
        cursor.close()
    if(conn != None):
        conn.rollback()
        conn.close()
    
# main db query 
# Change to args=[]
def run_query(statement, args=[]):
    
    try:
        (conn, cursor) = connect_db()
        if statement.startswith("SELECT"):
            cursor.execute(statement, args)
            result = cursor.fetchall()
            print("Total of {} users".format(cursor.rowcount))
            return result
        else:
            cursor.execute(statement, args)
            if cursor.rowcount == 1:
                conn.commit()
                print("Query successful")
            else:
                print("Query to insert")


    except mariadb.OperationalError as e:
        print("Got an operational Error")
        if("Access denied" in e.msg):
            print("Failed to log-in")
        print(e.msg)
    
    except mariadb.IntegrityError as e:
        
        if("Duplicate entry" in e.msg):
            print("User already exists")
        else:
            print(e.msg)
    
    except mariadb.ProgrammingError as e:
        if("SQL syntax" in e.msg):
            print("SQL syntax error, check formating")
        else:
            print("Got a different programming error")
        print(e.msg)

    except RuntimeError as e:
        print("Caught a runtime error")
        e.__traceback__

    except Exception as e:
        print(e.with_traceback)

        print(e.msg)
    finally:
        disconnect_db(conn,cursor)