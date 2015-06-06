# friends-knowlarity

there are 3 main folders in this project.
1. app
2. orientdb
3. venv

app - contains the mail code base
orientdb - package files of orientdb
venv - python virtualenv for this project

Getting started:
1. we need to start flask server using python app/runserver.py file
2. flask server needs connection to orientdb, so orientdb server should be available running and listening to local on port 2424. 
3. Configurational settings for the orientdb is mentioned in the app/settings.py file itsef. 
4. Also, database "friends_db" is accessible via HTTP on orientdb client at http://52.74.39.117:2480/ with credentials as username - root, password - root.
