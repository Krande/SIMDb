import plotly.express as px
import plotly.graph_objects as go
from trame.widgets import vuetify, plotly as plotly_widget


def contour_plot():
    """https://plotly.com/python/contour-plots/"""
    return go.Figure(
        data=go.Contour(
            z=[
                [10, 10.625, 12.5, 15.625, 20],
                [5.625, 6.25, 8.125, 11.25, 15.625],
                [2.5, 3.125, 5.0, 8.125, 12.5],
                [0.625, 1.25, 3.125, 6.25, 10.625],
                [0, 0.625, 2.5, 5.625, 10],
            ]
        )
    )


def bar_plot(color="Gold"):
    return go.Figure(data=go.Bar(y=[2, 3, 1], marker_color=color))


def scatter():
    df = px.data.iris()

    fig = px.scatter(
        df,
        x="sepal_width",
        y="sepal_length",
        color="species",
        title="Using The add_trace() method With A Plotly Express Figure",
    )

    fig.add_trace(
        go.Scatter(
            x=[2, 4],
            y=[4, 8],
            mode="lines",
            line=go.scatter.Line(color="gray"),
            showlegend=False,
        )
    )

    return fig


def table():
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(values=["Mode #", "Eigenvalue [Hz]"]),
                cells=dict(values=[[100, 90, 80, 90], [95, 85, 75, 95]]),
            )
        ]
    )
    return fig


PLOTS = {
    "Contour": contour_plot,
    "Bar": bar_plot,
    "Scatter": scatter,
    "Table": table,
}


def plotter_window(ctrl):
    vuetify.VSpacer()
    figure = plotly_widget.Figure(
        display_logo=False,
        display_mode_bar="true",
        v_show="table_view == true",
    )
    ctrl.figure_update = figure.update
    vuetify.VSpacer()
