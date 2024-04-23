import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np

def plot_and_send_file(file_path, user_id, bot):
    df = pd.read_csv(file_path)

    df['train_pred_smooth'] = df['train_pred'].rolling(window=10).mean()
    df['test_pred_smooth'] = df['test_pred'].rolling(window=10).mean()

    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Train/Test Prediction', color=color)
    ax1.plot(df.index, df['train_pred_smooth'], color='red', label='Train Pred (Smoothed)')
    ax1.plot(df.index, df['test_pred_smooth'], color='blue', label='Test Pred (Smoothed)')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Gradient', color=color)
    ax2.plot(df.index, df['grad_list'], color='green', label='Gradient')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.legend(loc='upper right')

    fig.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    bot.send_photo(user_id, photo=buf)
    buf.close()
    plt.close()
