import time
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import logging
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import asyncio


from main import user_ssh_clients
async def monitor_file(user_id, file_path):
    ssh_client = user_ssh_clients.get(user_id)
    if not ssh_client:
        return  # Handle error or disconnected state

    last_modified = None
    while True:
        try:
            sftp = ssh_client.open_sftp()
            attrs = sftp.stat(file_path)
            if last_modified is None or attrs.st_mtime > last_modified:
                # File has changed, update last_modified and process file
                last_modified = attrs.st_mtime
                local_path = f"./temp/{user_id}_temp.csv"  # Temp path for downloaded file
                sftp.get(file_path, local_path)
                plot_and_send_file(local_path, user_id)
            sftp.close()
        except Exception as e:
            logging.error(f"Error monitoring file: {e}")
            # Handle error

        await asyncio.sleep(10)  # Check every 10 seconds for changes


def plot_and_send_file(file_path, user_id):
    df = pd.read_csv(file_path)
    # Example: plotting the first two columns
    plt.figure()
    plt.plot(df[df.columns[0]], df[df.columns[1]], marker='o', linestyle='-')
    plt.title("File Update Plot")
    plt.xlabel(df.columns[0])
    plt.ylabel(df.columns[1])

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Send plot
    bot.send_photo(user_id, photo=buf)
    buf.close()
    plt.close()
