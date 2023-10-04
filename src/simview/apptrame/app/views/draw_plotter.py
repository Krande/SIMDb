from trame.widgets import vuetify

from simview.apptrame.app.views.plotter import PLOTS


def plotter_drawer():
    with vuetify.VRow(classes="pt-2", dense=True):
        vuetify.VSelect(
            label="Plot",
            v_model=("active_plot", "Table"),
            items=("plots", list(PLOTS.keys())),
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
        )
