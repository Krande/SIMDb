from trame.app import get_server
from trame_vuetify.ui.vuetify import SinglePageWithDrawerLayout
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid

from simview.apptrame.app00.representation import update_representation, create_render_window
from simview.apptrame.app00.sec_content import main_window
from simview.apptrame.app00.sec_drawer import drawer_main
from simview.apptrame.app00.sec_file_reader import read_file
from simview.apptrame.app00.sec_toolbar import toolbar_main

vtk_grid = vtkUnstructuredGrid()
use_actor = False

curr_mesh = read_file(vtk_grid)

render_window = None
actor = None
if use_actor:
    actor, render_window = create_render_window(vtk_grid)

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller
server.hot_reload = True
# -----------------------------------------------------------------------------
# Web App setup
# -----------------------------------------------------------------------------

state.trame__title = "FEA Results"


@state.change("mesh_representation")
def update_mesh_representation(mesh_representation, **kwargs):
    if use_actor:
        update_representation(actor, mesh_representation)
        ctrl.view_update()
    else:

        ctrl.mesh_update()
    print(mesh_representation)


@state.change("resolution")
def update_source(resolution=6, **kwargs):
    print(resolution)
    # mesh.warp_by_vector(factor=resolution)
    print('copy')
    # vtk_grid.DeepCopy(mesh)
    # ctrl.mesh_update()


@ctrl.trigger("download_binary")
def download():
    return server.protocol.addAttachment(curr_mesh.filepath.read_bytes())


@ctrl.set("update_ui")
def update_ui():
    with SinglePageWithDrawerLayout(server) as layout:
        layout.title.set_text("FEA Results")

        main_window(layout, ctrl, vtk_grid, use_actor, render_window)
        toolbar_main(layout, curr_mesh)
        drawer_main(layout)


update_ui()
# start_monitoring()

if __name__ == "__main__":
    server.start(open_browser=False)
