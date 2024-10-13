import awsgi
from datetime import datetime
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS, cross_origin
from functools import wraps
import json
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
import uuid


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = 'lkjgbae;j35h60#!s/.v,'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if cookie exists
        if request.cookies.get('session_hash') == None:
            response = make_response(jsonify({
                'body': 'Login required'
            }), 403)
            return response
        
        # Check db for session / session timeout
        result = get_session(hash=request.cookies.get('session_hash'))
        if result == [] or (datetime.now() - result[0][2]).total_seconds() > 600:
            response = make_response(jsonify({
                'body': 'Login required'
            }), 403)
            return response
        
        # Refresh timestamp on session
        refresh_session(result[0][1])
        
        return f(*args, **kwargs)
    return decorated_function


def db(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Create db connection and close afterwards
        cnx =  mysql.connector.connect(**credentials())
        cursor = cnx.cursor()
        result = f(cnx, cursor, *args, **kwargs)
        cursor.close()
        cnx.close()
        return result
    return decorated_function


@app.route('/', methods=['GET'])
@cross_origin()
@login_required
def index():
    # Get session data
    sess = get_session(hash=request.cookies.get('session_hash'))

    # Get forecast for subscriptions
    result = get_subscriptions(sess[0][0])

    # Create list of dicts for json
    data = []

    if result != []:
        for row in result:
            data.append({
                'city': row[0],
                'country': row[1],
                'historical': row[2],
                'forecast': row[3],
                'discrepancy': row[4]
            })

    # Return data
    response = make_response(jsonify({
        'body': data
    }), 200)
    return response


@app.route('/all', methods=['GET'])
@login_required
def all():
    # Get forecast data from db
    result = get_forecasts()

    # Create list of dicts for json
    data = []
    for row in result:
        data.append({
            'city': row[0],
            'country': row[1],
            'historical': row[2],
            'forecast': row[3],
            'discrepancy': row[4]
        })
                        
    # Return data
    response = make_response(jsonify({
        'body': data
    }), 200)
    return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get username and password submitted
        username = request.json['username']
        password = generate_password_hash(request.json['password'])

        # Check db for username
        result = get_user(username)

        # Return error if username exists
        if result != []:
            response = make_response(jsonify({
                'body': 'Username already exists'
            }), 409)
            return response

        # Create new user in db
        sess = create_user(username, password)

        # Configure and return response
        response = make_response(jsonify({
            'body': 'user created successfully'
        }), 200)
        response.set_cookie('session_hash', sess)
        response.headers['Access-Control-Allow-Credentials'] = True
        return response
    
    elif request.method == 'GET':
        response = make_response(jsonify({
            'body': 'poo'
        }), 200)
        return response


@app.route('/login', methods=['GET', 'POST'])
@cross_origin()
def login():
    if request.method == 'POST':
        # Get username and password submitted
        username = request.json['username']
        password = request.json['password']

        # Check for user in db
        result = get_user(username)

        # Return error if user not found
        if result == []:
            response = make_response(jsonify({
                'body': 'User not found'
            }), 404)
            return response
        
        # Return error if wrong password used
        if not check_password_hash(result[0][2], password):
            response = make_response(jsonify({
                'body': 'Incorrect password provided'
            }), 401)
            return response

        # Delete any pre-existing session for user
        sess_result = get_session(user_id=result[0][0])
        if sess_result != []:
            delete_session(user_id=result[0][0])

        # Create new session for user
        sess = create_session(result[0][0])

        # Configure and return response
        response = make_response(jsonify({
            'body': 'Login successful'
        }), 200)
        response.set_cookie('session_hash', sess)
        response.headers.set('Access-Control-Allow-Origin', 'https://main.d2wguw3fssyxn2.amplifyapp.com/')
        return response

    elif request.method == 'GET':
        response = make_response(jsonify({
            'body': 'logpoo'
        }), 200)
        return response


@login_required
@app.route('/manage-user', methods=['GET', 'PATCH', 'DELETE'])
def manage_user():
    if request.method == 'DELETE':
        # Get session data
        result = get_session(hash=request.cookies.get('session_hash'))
        
        # Delete session and user
        delete_session(hash=result[0][1])
        delete_user(result[0][0])

        # Configure and send response
        response = make_response(jsonify({
            'body': 'user deletion successful'
        }), 200)
        response.set_cookie('session_hash', '', expires=0)
        return response
    
    elif request.method == 'PATCH':
        # Get session data
        result = get_session(hash=request.cookies.get('session_hash'))

        # Update user password
        passhash = generate_password_hash(request.json['password'])
        update_password(result[0][0], passhash)

        # Configure and send response
        response = make_response(jsonify({
            'body': 'password updated'
        }), 200)
        return response
    
    elif request.method == 'GET':
        # Configure and send response
        response = make_response(jsonify({
            'body': 'updatepoo'
        }), 200)
        return response
    

@login_required
@app.route('/manage-subscriptions', methods=['GET', 'POST', 'DELETE'])
def manage_subscriptions():
    if request.method == 'GET':
        # Get city data
        result = get_cities()

        # Create city dicts
        data = []
        for row in result:
            data.append({
                'id': row[0],
                'city': row[1],
                'country': row[2]
            })

        # Return reponse
        response = make_response(jsonify({
            'body': data
        }), 200)
        return response
    
    elif request.method == 'POST':
        # Get session data
        sess = get_session(hash=request.cookies.get('session_hash'))

        # Get city ID from request
        city_id = request.json['city_id']

        # Create subscription
        create_subscription(sess[0][0], city_id)

        # Return reponse
        response = make_response(jsonify({
            'body': 'Subscription created'
        }), 200)
        return response
    
    elif request.method == 'DELETE':
        # Get session data
        sess = get_session(hash=request.cookies.get('session_hash'))

        # Get city ID and  from request
        city_id = request.json['city_id']

        # Create subscription
        delete_subscription(sess[0][0], city_id)

        # Return reponse
        response = make_response(jsonify({
            'body': 'Subscription deleted'
        }), 200)
        return response
    

@login_required
@app.route('/logout', methods=['DELETE'])
def logout():
    # Delete user session from db
    delete_session(hash=request.cookies.get('session_hash'))

    # Configure and send response
    response = make_response(jsonify({
        'body': 'Logout successful'
    }), 200)
    response.set_cookie('session_hash', '', expires=0)
    return response


def credentials():
    with open('dbcreds.json') as file:
        return json.load(file)
    

@db
def get_user(cnx, cursor, username):
    sql = f"""
        SELECT * FROM USERS
        WHERE USERNAME = '{username}'
    """
    cursor.execute(sql)
    return cursor.fetchall()


@db
def create_user(cnx, cursor, username, passhash):
    sql = f"""
        INSERT INTO USERS (USERNAME, PASSHASH) VALUES ('{username}','{passhash}')
    """
    cursor.execute(sql)
    cnx.commit()
    sql = f"""
        SELECT ID FROM USERS WHERE USERNAME = '{username}'
    """
    cursor.execute(sql)
    result = cursor.fetchall()
    return create_session(result[0][0])


@db
def delete_user(cnx, cursor, user_id):
    sql = f"""
        DELETE FROM USERS WHERE ID = {user_id}
    """
    cursor.execute(sql)
    cnx.commit()
    return True


@db
def update_password(cnx, cursor, user_id, passhash):
    sql = f"""
        UPDATE USERS SET PASSHASH = '{passhash}' WHERE ID = {user_id}
    """
    cursor.execute(sql)
    cnx.commit()
    return True


@db
def get_session(cnx, cursor, hash=None, user_id=None):
    if hash != None:
        sql = f"""
            SELECT * FROM SESSIONS
            WHERE HASH = '{hash}'
        """
    else:
        sql = f"""
            SELECT * FROM SESSIONS
            WHERE USER_ID = {user_id}
        """
    cursor.execute(sql)
    return cursor.fetchall()


@db
def create_session(cnx, cursor, user_id):
    sess = uuid.uuid4().hex
    sql = f"""
        INSERT INTO SESSIONS (USER_ID, HASH, TIME) VALUES ({user_id},'{sess}','{str(datetime.now())}')
    """
    cursor.execute(sql)
    cnx.commit()
    return sess


@db
def delete_session(cnx, cursor, hash=None, user_id=None):
    if hash != None:
        sql = f"""
            DELETE FROM SESSIONS WHERE HASH = '{hash}'
        """
    else:
        sql = f"""
            DELETE FROM SESSIONS WHERE USER_ID = {user_id}
        """
    cursor.execute(sql)
    cnx.commit()
    return True


@db
def refresh_session(cnx, cursor, hash):
    sql = f"""
        UPDATE SESSIONS SET TIME = '{str(datetime.now())}' WHERE HASH = '{hash}'
    """
    cursor.execute(sql)
    cnx.commit()
    return True


@db
def get_forecasts(cnx, cursor):
    sql = f"""
        SELECT NAME, ISO, HIST_AVG, FORECAST, DISCREPANCY FROM FORECASTS F
        INNER JOIN CITIES C ON F.CITY_ID = C.ID
        ORDER BY ABS(DISCREPANCY) DESC
    """
    cursor.execute(sql)
    return cursor.fetchall()


@db
def get_subscriptions(cnx, cursor, user_id):
    sql = f"""
        SELECT NAME, ISO, HIST_AVG, FORECAST, DISCREPANCY FROM SUBSCRIPTIONS S
        INNER JOIN CITIES C ON S.CITY_ID = C.ID
        INNER JOIN FORECASTS F ON F.CITY_ID = C.ID
        WHERE S.USER_ID = {user_id}
        ORDER BY ABS(DISCREPANCY) DESC
    """
    cursor.execute(sql)
    return cursor.fetchall()


@db
def create_subscription(cnx, cursor, user_id, city_id):
    sql = f"""
        INSERT INTO SUBSCRIPTIONS (USER_ID, CITY_ID) VALUES ({user_id}, {city_id})
    """
    cursor.execute(sql)
    cnx.commit()
    return True


@db
def delete_subscription(cnx, cursor, user_id, city_id):
    sql = f"""
        DELETE FROM SUBSCRIPTIONS
        WHERE USER_ID = {user_id}
        AND CITY_ID = {city_id}
    """
    cursor.execute(sql)
    cnx.commit()
    return True


@db
def get_cities(cnx, cursor):
    sql = f"""
        SELECT ID, NAME, ISO FROM CITIES
    """
    cursor.execute(sql)
    return cursor.fetchall()
    

def lambda_handler(event, context):
    return awsgi.response(app, event, context, base64_content_types={"image/png"})