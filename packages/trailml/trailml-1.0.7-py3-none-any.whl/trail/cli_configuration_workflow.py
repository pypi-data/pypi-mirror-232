import os
import yaml

import pyrebase
import requests
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError

from .libconfig import libconfig

GET_ALL_PROJECTS = """
    query{
    allProjects {
      id
      title
    }
  }
  """


def create_config(username, password, project_id, parent_experiment_id):
    config = {
        'username': username,
        'password': password,
        'projects': {
            'id': project_id,
            'parentExperimentId': parent_experiment_id
        },
    }
    path = os.path.join(os.getcwd(), 'trail_config.yml')
    with open(path, 'w') as f:
        yaml.dump(config, f, sort_keys=False)
    print(
        f"Configuration with given information was "
        f"created at '{path}' \n"
    )


def get_user_credentials(message):
    print(message)
    username = input("Username: ")
    password = input("Password: ")

    print("Validating credentials... \n")
    return [username, password]


def login_user(useremail, userpassword, invalid=False, first=False):
    email = useremail
    password = userpassword
    firebase = pyrebase.initialize_app(
        {
            'apiKey': libconfig.FIREBASE_API_KEY,
            'authDomain': libconfig.FIREBASE_AUTH_DOMAIN,
            'databaseURL': 'THIS_IS_NOT_USED',
            'storageBucket': 'THIS_IS_NOT_USED',
        }
    )
    auth = firebase.auth()
    if invalid:
        selection = input("If you want to retry input r, or to abort input c: ")
        if selection.lower() == 'c':
            exit()
        elif selection.lower() == 'r':
            [new_email, new_password] = get_user_credentials(
                "Please input credentials. \n"
            )
            email = new_email
            password = new_password
        else:
            return login_user(email, password, invalid=True, first=False)
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        token = user['idToken']
        try:
            transport = AIOHTTPTransport(
                libconfig.GQL_ENDPOINT_URL, headers={'authorization': f'Bearer {token}'}
            )
            client = Client(transport=transport)
            result = client.execute(document=gql(GET_ALL_PROJECTS))
            print("Your projects are listed below:\n")
            print("Project ID | Project Title")
            for project in result["allProjects"]:

                print(project['id'] + "     | " + project['title'])

        except TransportQueryError as e:
            print(e)
        project_id = input("Please type in project id: ")
        parent_experiment = input("Please input parent experiment id: ")
        create_config(email, password, project_id, parent_experiment)

    except requests.exceptions.HTTPError as e:
        if first:
            TRAIL_LINK = "https://www.trail-ml.com/sign-up"
            print(f"Dont' have an account yet?" f" You can sign up here: {TRAIL_LINK}")
        if e.errno.response.status_code == 400:  # type: ignore
            user = login_user(email, password, invalid=True, first=False)
            return user
        else:
            raise e

    return user['idToken']
