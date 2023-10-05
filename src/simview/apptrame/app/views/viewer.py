from __future__ import annotations

from typing import TYPE_CHECKING

# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
import vtkmodules.vtkRenderingOpenGL2  # noqa
from trame.widgets import vtk as vtk_widgets, vuetify
from trame_router.ui.router import RouterViewLayout

from simview.apptrame.app.representation import create_render_window
from simview.apptrame.app.views.graphs import plotter_window

if TYPE_CHECKING:
    from simview.apptrame.app.main import App


def content_routers(app: App):
    render_window = create_render_window(app.model)
    with RouterViewLayout(app.server, "/"):
        # view = vtk_widgets.VtkRemoteView(render_window)
        with vtk_widgets.VtkLocalView(render_window) as view:
            app.ctrl.view_update = view.update
            # app.ctrl.view_reset_camera = view.reset_camera
            # app.ctrl.on_server_ready.add(view.update)

    with RouterViewLayout(app.server, "/eigen"):
        plotter_window(app.ctrl)
