from dataclasses import dataclass

from trame.widgets import vuetify
from trame_server import Server

from simview.apptrame.app.views.graphs import PLOTS


@dataclass
class PlotterUI:
    server: Server

    def on_active_plot_change(self, active_plot, **kwargs):
        print("updated -> ", active_plot)
        self.server.controller.figure_update(PLOTS[active_plot]())


def plotter_drawer(server: Server):
    pui = PlotterUI(server)
    active_plot = "active_plot"
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
        server.state.change(active_plot)(pui.on_active_plot_change)
