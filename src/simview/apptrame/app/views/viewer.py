from __future__ import annotations

from typing import TYPE_CHECKING

# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
import vtkmodules.vtkRenderingOpenGL2  # noqa
from trame.widgets import vtk as vtk_widgets, vuetify
from trame_router.ui.router import RouterViewLayout

from simview.apptrame.app.views.plotter import plotter_window

if TYPE_CHECKING:
    from simview.apptrame.app.main import App


def content_routers(app: App):
    with RouterViewLayout(app.server, "/"):
        with vtk_widgets.VtkLocalView(app.render_window) as view:
            app.ctrl.view_update.add(view.update)
            app.ctrl.on_server_ready.add(view.update)

    with RouterViewLayout(app.server, "/eigen"):
        with vuetify.VCardText():
            vuetify.VBtn("Take me back", click="$router.back()")
        with vuetify.VRow(dense=True, style="height: 30%"):
            plotter_window(app.ctrl)
        with vuetify.VRow(dense=True, style="height: 70%"):
            with vtk_widgets.VtkLocalView(app.render_window) as view:
                app.ctrl.view_update.add(view.update)
                app.ctrl.on_server_ready.add(view.update)
