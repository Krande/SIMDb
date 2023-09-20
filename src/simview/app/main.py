# Required for interactor initialization
# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
import vtkmodules.vtkRenderingOpenGL2  # noqa
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa
from trame.app import get_server

from simview.app.callbacks import ViewCalls
from simview.app.ui import VtkGui
from simview.app.data import VtkData


def initialize():
    vtk_data = VtkData()
    vtk_data.initialize()

    server = get_server()
    server.client_type = "vue3"
    server.state.setdefault("active_ui", None)

    view_calls = ViewCalls(vtk_data)

    gui = VtkGui(server, vtk_data, view_calls)

    server.start()


if __name__ == "__main__":
    initialize()
