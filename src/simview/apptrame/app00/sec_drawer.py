from trame.app import get_server
from trame.widgets import vuetify

from simview.apptrame.app00.plotter import PLOTS
from simview.apptrame.app00.representation import Representation

server = get_server()
state, ctrl = server.state, server.controller


@state.change("active_plot")
def update_plot(active_plot, **kwargs):
    ctrl.figure_update(PLOTS[active_plot]())


def drawer_main(layout):
    with layout.drawer as drawer:
        drawer.width = 325

        with vuetify.VRow(classes="pt-2", dense=True):
            vuetify.VSelect(
                # Representation
                v_model=("mesh_representation", Representation.Surface),
                items=(
                    "representations",
                    [
                        {"text": "Points", "value": 0},
                        {"text": "Wireframe", "value": 1},
                        {"text": "Surface", "value": 2},
                        {"text": "Surface With Edges", "value": 3},
                    ],
                ),
                label="Representation",
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-1",
            )

        with vuetify.VRow(classes="pt-2", dense=True):
            vuetify.VSelect(
                label="Plot",
                v_model=("active_plot", "Contour"),
                items=("plots", list(PLOTS.keys())),
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-1",
            )
