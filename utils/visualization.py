import plotly.express as px


def plot_feature_importance(df, title="Feature Importance"):
    fig = px.bar(
        df,
        x="importance",
        y=df.columns[0],
        orientation="h",
        title=title
    )

    fig.update_layout(
        height=450,
        margin=dict(l=120, r=20, t=50, b=30),
        yaxis_title="",
        xaxis_title="Importance",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return fig
