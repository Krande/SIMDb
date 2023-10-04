import os

from trame.app import get_server
from trame.decorators import TrameApp, trigger, controller, change, life_cycle
from trame.widgets import vuetify, trame as trame_widget
from trame_vuetify.ui.vuetify import SinglePageWithDrawerLayout

from simview.apptrame.app.filewatcher import start_monitoring
from simview.apptrame.app.views.file_reader import ModelDataStore, file_reader_main
from simview.apptrame.app.views.plotter import plotter_window, PLOTS, plotter_drawer
from simview.apptrame.app.views.representation import update_representation, create_render_window, representation_drawer
from simview.apptrame.app.views.toolbar import toolbar_main
from simview.apptrame.app.views.viewer import view3d_window

os.environ["TRAME_DISABLE_V3_WARNING"] = "1"


@TrameApp()
class App:
    def __init__(self, name=None, use_actor=False, monitor=False):
        self.server = get_server(name)
        self.server.state.setdefault("active_ui", "geometry")
        self.server.state.setdefault("active_content", "Table")
        self.use_actor = use_actor

        model = ModelDataStore(self.server)
        model.load_files_from_storage_blob()
        model.download_file()

        self.model = model
        self.actor = None
        self.render_window = None

        if use_actor:
            self.actor, self.render_window = create_render_window(self.model)

        if monitor:
            start_monitoring(self.server)

        self.ui()

    @property
    def state(self):
        return self.server.state

    @property
    def ctrl(self):
        return self.server.controller

    @trigger("download_binary")
    def download(self):
        return self.server.protocol.addAttachment(self.model.current_mesh.blob.blob.download_blob().readall())

    @trigger("exec")
    def method_call(self, msg):
        print("method_called", msg)

    @controller.set("hello")
    def method_on_ctrl(self, *args):
        print("method_on_ctrl", args)

    @trigger("click_me")
    def click_me(self, *args):
        print("method_on_ctrl", args)

    @change("active_ui")
    def active_ui_change(self, active_ui, **kwargs):
        print(active_ui)

    @change("resolution")
    def one_slider(self, resolution, **kwargs):
        print("Slider value 1", resolution)

    @change("active_model")
    def load_current_file(self, **kwargs):
        self.model.download_file()

    @change("active_plot")
    def update_plot(self, active_plot, **kwargs):
        print("update_plot", active_plot)
        self.ctrl.figure_update(PLOTS[active_plot]())

    @change("mesh_representation")
    def update_mesh_representation(self, mesh_representation=3, **kwargs):
        if self.use_actor:
            update_representation(self.actor, mesh_representation)
            self.ctrl.view_update()
        else:
            self.ctrl.mesh_update()
        print(f"{mesh_representation=}")

    @change("mesh_opacity")
    def update_mesh_opacity(self, mesh_opacity, **kwargs):
        self.actor.GetProperty().SetOpacity(mesh_opacity)
        self.ctrl.view_update()

    @life_cycle.server_ready
    def on_ready(self, *args, **kwargs):
        print("on_ready")

    @life_cycle.client_connected
    def on_client_connected(self, *args, **kwargs):
        print("on_client_connected")

    @change("contour_representation")
    def update_contour_representation(self, contour_representation, **kwargs):
        if self.actor is None:
            return
        update_representation(self.model.contour_actor, contour_representation)
        self.ctrl.view_update()

    def ui(self):
        with SinglePageWithDrawerLayout(self.server) as layout:
            layout.title.set_text(self.server.name)

            # Let the server know the browser pixel ratio
            trame_widget.ClientTriggers(mounted="pixel_ratio = window.devicePixelRatio")

            with layout.content:
                with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
                    with vuetify.VRow(dense=True, style="height: 30%"):
                        plotter_window(self.ctrl)
                    # vuetify.VDivider(vertical=False, classes="mx-2")
                    with vuetify.VRow(dense=True, style="height: 70%"):
                        view3d_window(self.ctrl, self.model.vtk_grid, self.use_actor, self.render_window)

            with layout.toolbar as toolbar:
                toolbar.dense = True
                toolbar_main(self)

            with layout.drawer as drawer:
                drawer.width = 325
                file_reader_main(self.model)
                representation_drawer()
                plotter_drawer()
                # contour_card(self.model)


if __name__ == "__main__":
    app = App("FEA Results", use_actor=True)
    app.server.start(open_browser=False)
    # check_and_open_webpage("http://localhost:8080", "Trame")
