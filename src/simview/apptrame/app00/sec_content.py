from trame.widgets import vuetify, plotly
from trame.widgets import vuetify, vtk as vtk_widgets


def main_window(layout, ctrl, vtk_grid, use_actor, render_window):
    with layout.content:
        with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
            with vuetify.VRow(dense=True, style="height: 30%"):
                vuetify.VSpacer()
                figure = plotly.Figure(
                    display_logo=False,
                    display_mode_bar="true",
                )
                ctrl.figure_update = figure.update
                vuetify.VSpacer()

            with vuetify.VRow(dense=True, style="height: 70%"):
                with vtk_widgets.VtkView(ref="view"):
                    if use_actor:
                        view = vtk_widgets.VtkLocalView(render_window)
                        ctrl.view_update.add(view.update)
                        ctrl.on_server_ready.add(view.update)
                    else:
                        with vtk_widgets.VtkGeometryRepresentation():
                            mesh = vtk_widgets.VtkMesh("mesh", dataset=vtk_grid)
                            ctrl.mesh_update = mesh.update


