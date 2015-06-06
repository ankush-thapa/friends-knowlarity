import settings

def get_user_email(name):
    """
        returns email if given username
        e.g - for ankush, it will return ankush@gmail.com
    """
    return str(name)+'@gmail.com'

def random_email_ids(start=0, end=settings.MAX_USER_COUNT):
    email_list = [get_user_email(counter) for counter in range(start, end)]
    return email_list

def get_random_insert_values():
    random_list = random_email_ids()
    insert_values = ["('" + email + "')" for email in random_list]
    return insert_values

def execute_query(client, query):
    """
        executes the passed string using give client and returns responses
    """
    response = client.command(str(query))
    return response

def are_friends(client, user_1, user_2):
    """
        checks if there exists friendship between two given users
    """
    command = "select both().email_id Connections from Users where email_id='%s'" % (user_1)
    results = execute_query(client, command)
    friends = results[0].both
    if user_2 in friends:
        return True
    return False

def user_exists(client, user):
    """
        checks if a user exists in our system or not
    """
    command = "select count(*) from Users where email_id = '%s'" % (user)
    results = execute_query(client, command)
    if bool(results[0].count):
        return True
    return False
