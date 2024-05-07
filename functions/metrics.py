import pandas as pd
import json
import logging
import os

def ensure_directory_exists(path):
    os.makedirs(path, exist_ok=True)

def get_metrics(user_id, file_path, bot, ssh_clients):
    ssh_client = ssh_clients.get(user_id)
    if not ssh_client:
        logging.error("SSH client not available for user_id {}".format(user_id))
        return  # Handle error or disconnected state
    sftp = ssh_client.open_sftp()
    attrs = sftp.stat(file_path)
    local_path = f"./tmp/{user_id}_temp.csv"
    ensure_directory_exists('./tmp/')
    sftp.get(file_path, local_path)
    extension = local_path.split('.')[-1].lower()
    if extension == 'csv':
        df = pd.read_csv(local_path)
        return df.columns.tolist()
    elif extension == 'json':
        with open(local_path, 'r') as file:
            data = json.load(file)
            if isinstance(data, list):
                return list(data[0].keys())
            else:
                return list(data.keys())
    elif extension in ['log', 'txt']:
        with open(local_path, 'r') as file:
            first_line = file.readline()
            return first_line.strip().split()[2:]
    else:
        raise ValueError("Неподдерживаемый формат файла")
