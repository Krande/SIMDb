from typing import TYPE_CHECKING

from trame.decorators import TrameApp
from trame.widgets import vtk as vtk_widgets

# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
import vtkmodules.vtkRenderingOpenGL2  # noqa

if TYPE_CHECKING:
    from simview.apptrame.app00.main import App


@TrameApp()
class Viewer:
    ...


def view3d_window(ctrl, vtk_grid, use_actor, render_window):
    if use_actor:
        with vtk_widgets.VtkLocalView(render_window) as view:
            ctrl.view_update.add(view.update)
            ctrl.on_server_ready.add(view.update)
    else:
        with vtk_widgets.VtkView(ref="view"):
            with vtk_widgets.VtkGeometryRepresentation():
                mesh = vtk_widgets.VtkMesh("mesh", dataset=vtk_grid)
                ctrl.mesh_update = mesh.update
                ctrl.mesh_reset_camera = mesh.reset_camera
                # ctrl.on_server_ready.add(mesh.update)
