from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify

import pyvista as pv
from pyvista import examples
from pyvista.trame.ui import plotter_ui

from simview.helpers import DATA_DIR

# -----------------------------------------------------------------------------
# Trame initialization
# -----------------------------------------------------------------------------

pv.OFF_SCREEN = True

server = get_server()
state, ctrl = server.state, server.controller

state.trame__title = "Modify Scalar Range"
ctrl.on_server_ready.add(ctrl.view_update)

# -----------------------------------------------------------------------------
# Plotting
# -----------------------------------------------------------------------------

# mesh = pv.Wavelet()
mesh = pv.read(DATA_DIR / "Cantilever_CA_EIG_sh_modes.vtu")

pl = pv.Plotter()
actor = pl.add_mesh(mesh)


# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------


@state.change("scalar_range")
def set_scalar_range(scalar_range=mesh.get_data_range(), **kwargs):
    actor.mapper.scalar_range = scalar_range
    ctrl.view_update()


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------


with SinglePageLayout(server) as layout:
    layout.title.set_text("Scalar Selection")
    layout.icon.click = ctrl.view_reset_camera

    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VRangeSlider(
            thumb_size=16,
            thumb_label=True,
            label="Range",
            v_model=("scalar_range", [0, 300]),
            min=('0',),
            max=('500',),
            dense=True,
            hide_details=True,
            style="max-width: 400px",
        )

    with layout.content:
        with vuetify.VContainer(
                fluid=True,
                classes="pa-0 fill-height",
        ):
            # Use PyVista UI template for Plotters
            view = plotter_ui(pl, default_server_rendering=False)
            ctrl.view_update = view.update

if __name__ == '__main__':
    server.start(port=8000)
