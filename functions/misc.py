from config import user_ssh_clients

async def is_connected(user_id):
    if user_id in user_ssh_clients and user_ssh_clients[user_id].get_transport() is not None and user_ssh_clients[user_id].get_transport().is_active():
        return True
    return False