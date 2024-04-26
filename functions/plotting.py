import pandas as pd
import plotly.graph_objects as go
from plotly.io import to_image
from io import BytesIO


def plot_and_send_file(file_path):
    df = pd.read_csv(file_path)

    # Assuming your dataframe has pairs of 'train_X' and 'test_X' columns for each prediction type X
    fig = go.Figure()
    prediction_types = set(col.split('_')[1] for col in df.columns if col.startswith(('train_', 'test_')))

    for ptype in prediction_types:
        train_col = f'train_{ptype}'
        test_col = f'test_{ptype}'
        if train_col in df.columns and test_col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[train_col], mode='lines', name=f'Train {ptype}'))
            fig.add_trace(go.Scatter(x=df.index, y=df[test_col], mode='lines', name=f'Test {ptype}'))

    # Update layout with the latest test/train values for the last epoch
    latest_train = df.iloc[-1][[f'train_{ptype}' for ptype in prediction_types]].to_dict()
    latest_test = df.iloc[-1][[f'test_{ptype}' for ptype in prediction_types]].to_dict()
    latest_values_text = "<br>".join(
        [f"Latest {ptype} - Train: {latest_train[f'train_{ptype}']}, Test: {latest_test[f'test_{ptype}']}" for ptype in
         prediction_types])

    fig.update_layout(
        title='Predictions Over Time',
        xaxis_title='Epoch',
        yaxis_title='Value',
        yaxis_type='log',  # Set to 'linear' if log scale is not desired
        legend_title='Legend',
        annotations=[{
            'text': latest_values_text,
            'align': 'left',
            'showarrow': False,
            'xref': 'paper',
            'yref': 'paper',
            'x': 1.0,
            'y': -0.3,
            'bordercolor': 'black',
            'borderwidth': 1,
            'bgcolor': 'white',
            'xanchor': 'right',
            'yanchor': 'bottom',
            'font': {'size': 12}
        }]
    )

    buf = BytesIO()
    buf.write(to_image(fig, format='png', scale=1))  # You can adjust 'scale' for higher resolution
    buf.seek(0)

    return buf
