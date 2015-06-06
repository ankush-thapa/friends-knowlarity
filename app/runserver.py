from flask import Flask, request, session, g, redirect, render_template, flash, abort
from flask.ext.session import Session
import random
import uuid

# internal imports
import db_configs
import settings
import utils

app = Flask(__name__)
app.config['SESSION_TYPE'] = settings.SESSION_TYPE
app.config['SECRET_KEY'] = settings.SESSION_SECRET_KEY
sess = Session()

@app.before_request
def csrf_protect():
    """
        verifies if the csrf token sent from the client is the same that 
        session has generated
    """
    if request.method == 'POST':
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)

@app.before_request
def generate_csrf_token():
    """
        generates csrf token for session
    """
    if '_csrf_token' not in session:
        session['_csrf_token'] = str(uuid.uuid4())

def get_db_client():
    """
    opens a new connection to db if there does not exist any
    """
    if not hasattr(g, 'client'):
        g.client = db_configs.get_db_client()
    return g.client

@app.teardown_appcontext
def close_client(exception):
    """
    closes a db connection if exists
    """
    db_configs.close_db_client(g)

@app.route('/')
def show_all_apis():
    """
    links to all apis
    """
    return render_template('show_all_apis.html')

@app.route('/create-random-graph')
def create_random_graph():
    """
        creates MAX_USER_COUNT number of random users in db.
        and creates random connections between them.
    """
    client = get_db_client()
    command = "INSERT INTO Users (email_id) values %s" % ((", ").join(\
        utils.get_random_insert_values()))
    response = utils.execute_query(client, command)
    for counter in range(0,settings.MAX_USER_COUNT):
        # for nth user lets create random friends_count number of friends
        friends_count = random.randint(0,5)
        # name of those random number of users chosen to be friends of nth user
        usernames=random.sample(range(0,settings.MAX_USER_COUNT),friends_count)
        for username in usernames:
            user_email = utils.get_user_email(username)
            current_user_email = utils.get_user_email(counter)
            if not utils.are_friends(client, user_email, current_user_email):
                command = "create edge Connections from (select from Users where\
                    email_id = '%s') to (select from Users where email_id = '%s')"\
                    % (current_user_email, user_email)
                utils.execute_query(client, command)
    message = "%s users created succesfully." %(settings.MAX_USER_COUNT)
    return render_template('message.html', message=message)

 
@app.route('/add-new-user', methods=['GET', 'POST'])
def add_new_user():
    """
        add a new user into Users table with given email id. CSRF considered
    """
    if request.method == 'GET':
        return render_template('add_new_user.html')
    elif request.method == 'POST':
        email_id = request.form.get('email_id', None)
        client = get_db_client()
        # check if already exist in command, unique email_ids 
        if utils.user_exists(client, email_id):
            message = "User already exists."
        else:
            command = "INSERT INTO Users (email_id) values %s" % ("('"+ email_id + "')")
            utils.execute_query(client, command)
            message = "user %s created successfully" %(email_id) 
        return render_template('message.html', message=message)

@app.route('/create-friends', methods=['GET', 'POST'])
def create_friends():
    """
        given two users, create friendship connection between them
    """
    message = ""
    if request.method == 'GET':
        return render_template('create_connection.html')
    if request.method == 'POST':
        client = get_db_client()
        user_1 = request.form.get('user_1', None)
        user_2 = request.form.get('user_2', None)
        if not (utils.user_exists(client, user_1) or utils.user_exists(client, user_2)):
            message = "Users Doesnot Exist. Please use our create users API for creating users first."
        elif user_1 == user_2:
            message = "Cannot create friends with self."
        else:
            if not utils.are_friends(client, user_1, user_2):
                command = "create edge Connections from (select from Users where email_id = '%s') to (select from Users where email_id = '%s')" % (user_1, user_2)
                utils.execute_query(client, command)
                message = "connection created successfully from %s to %s" % (user_1, user_2)
            else:
                message = "They are already good friends."
        return render_template('create_connection.html', message=message, user_1=user_1, user_2=user_2)

@app.route('/clear-db')
def clear_db():
    """
        flush all db
    """
    client = get_db_client()
    db_configs.flush_db(client)
    message = "db flushed"
    return render_template('message.html', message=message)
 
@app.route('/view_friendship', methods=['GET', 'POST'])
def view_friendship():
    """
        returns the degree of separation between two users
    """
    if request.method == 'GET':
        return render_template('view_friendship.html')
    elif request.method == 'POST': 
        client = get_db_client()
        user_1 = request.form.get('user_1', None)
        user_2 = request.form.get('user_2', None)
        if not (utils.user_exists(client, user_1) and utils.user_exists(client, user_2)):
            message = "Users Doesnot Exist. Please use our create users API for creating users first."
        elif user_1 == user_2:
            message = "Same users entered."
        else:
            command = "select @rid from Users where email_id = '%s'" % user_1
            rid_1 = utils.execute_query(client, command)[0].rid
            command = "select @rid from Users where email_id = '%s'" % user_2
            rid_2 = utils.execute_query(client, command)[0].rid
            command = "Select shortestPath(%s, %s)" % (rid_1, rid_2)
            results = utils.execute_query(client, command)
            path_len = len(results[0].shortestPath) - 1
            if path_len == -1:
                message = "%s, %s are not connected" % (user_1, user_2)
            else:
                message = "%s, %s are %s order connections." % (user_1, user_2, path_len)
    return render_template('view_friendship.html', message=message, user_1=user_1, user_2=user_2)

if __name__ == '__main__':
    app.debug = settings.DEBUG
    app.run('0.0.0.0')
