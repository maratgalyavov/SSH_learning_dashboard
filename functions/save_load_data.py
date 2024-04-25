import json


def save_connection_details(user_id, host, username, port=2222):
    connection_details = {user_id: {'host': host, 'username': username, 'port': port}}
    try:
        with open('ssh_connections.json', 'r') as file:
            existing_details = json.load(file)
    except FileNotFoundError:
        existing_details = {}

    existing_details.update(connection_details)

    with open('ssh_connections.json', 'w') as file:
        json.dump(existing_details, file, indent=4)

def load_connection_details():
    try:
        with open('ssh_connections.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
