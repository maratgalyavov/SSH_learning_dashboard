import time

from aiogram.types import InputFile, BufferedInputFile
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import logging
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import asyncio
import os
from functions import plotting

def ensure_directory_exists(path):
    os.makedirs(path, exist_ok=True)

async def monitor_file(user_id, file_path, bot, ssh_clients, metrics):
    ssh_client = ssh_clients.get(user_id)
    if not ssh_client:
        logging.error("SSH client not available for user_id {}".format(user_id))
        return  # Handle error or disconnected state

    last_modified = None
    last_message_id = None
    while True:
        try:
            sftp = ssh_client.open_sftp()
            attrs = sftp.stat(file_path)
            if last_modified is None or attrs.st_mtime > last_modified:
            # if True:
                # File has changed, update last_modified and process file
                last_modified = attrs.st_mtime
                local_path = f"./tmp/{user_id}_temp.csv"
                ensure_directory_exists('./tmp/')
                sftp.get(file_path, local_path)

                # Plot and prepare to send the file
                buf = plotting.plot_and_send_file(local_path, metrics)
                photo = BufferedInputFile(buf.getvalue(), filename="plot.png")

                # Delete the last sent photo if it exists
                if last_message_id:
                    try:
                        await bot.delete_message(user_id, last_message_id)
                    except Exception as e:
                        logging.error("Failed to delete previous message: {}".format(e))

                # Send new plot and store message ID
                message = await bot.send_photo(user_id, photo=photo)
                last_message_id = message.message_id

                buf.close()
            sftp.close()
        except Exception as e:
            logging.error(f"Error monitoring file: {e}")
            # Handle error and consider a cooldown or stop

        await asyncio.sleep(30)  # Sleep for 1 minute before checking again
