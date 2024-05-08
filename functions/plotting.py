import json
import os
import math

import pandas as pd
import plotly.graph_objects as go
from plotly.io import to_image
from io import BytesIO

from plotly.subplots import make_subplots


def ensure_directory_exists(path):
    os.makedirs(path, exist_ok=True)


def read_data(file_path):
    file_ext = os.path.splitext(file_path)[-1].lower()
    if file_ext == ".csv":
        return pd.read_csv(file_path)
    elif file_ext == ".json":
        with open(file_path, 'r') as file:
            data = json.load(file)
            return pd.DataFrame(data)
    elif file_ext in [".log", ".txt"]:
        data = []
        with open(file_path, 'r') as file:
            for line in file:
                elements = line.strip().split()
                epoch = int(elements[1])  # Assuming 'Epoch' is always the first word and followed by the epoch number
                values = elements[2:]  # Rest are values
                # Process pairs of values
                row = {'Epoch': epoch}
                for i in range(0, len(values), 2):
                    key = values[i]
                    value = float(values[i + 1])
                    row[key] = value
                data.append(row)
        df = pd.DataFrame(data)
        if not df.empty:
            df.set_index('Epoch', inplace=True)
        return df
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")


def plot_data(df, metrics):
    num_plots = len(metrics)
    num_cols = math.ceil(math.sqrt(num_plots))
    num_rows = math.ceil(num_plots / num_cols)

    fig = make_subplots(
        rows=num_rows,
        cols=num_cols,
        subplot_titles=[f"Metrics Group {i + 1}" for i in range(num_plots)],
        vertical_spacing=0.1,
    )

    for i, metrics in enumerate(metrics):
        row = i // num_cols + 1
        col = i % num_cols + 1

        for metric in metrics:
            if metric in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df[metric], mode='lines', name=metric),
                    row=row, col=col
                )
        fig.update_xaxes(title_text="Epoch", row=row, col=col)
        fig.update_yaxes(title_text="Value", type='log', row=row, col=col)


    for i in range(num_plots, num_rows * num_cols):
        row = i // num_cols + 1
        col = i % num_cols + 1
        fig.update_layout({f'xaxis{i + 1}': {'visible': False}, f'yaxis{i + 1}': {'visible': False}})

    fig.update_layout(
        title="Data Over Time",
        xaxis_title="Epoch",
        yaxis_title="Value",
        height=num_rows * 400,  # Adjust the height based on the number of rows
    )

    return fig


def plot_and_send_file(file_path, metrics):
    df = read_data(file_path)
    fig = plot_data(df, metrics)
    buf = BytesIO()
    buf.write(to_image(fig, format='png', scale=1))
    buf.seek(0)
    return buf
