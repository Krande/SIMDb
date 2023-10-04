import os

from trame.app import get_server
from trame.decorators import TrameApp, trigger, controller, change, life_cycle
from trame.widgets import vuetify, router
from trame_vuetify.ui.vuetify import SinglePageWithDrawerLayout
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor

from simview.apptrame.app.filewatcher import start_monitoring
from simview.apptrame.app.model_store import ModelDataStore
from simview.apptrame.app.views.draw_models import file_reader_main
from simview.apptrame.app.views.draw_plotter import plotter_drawer
from simview.apptrame.app.views.draw_repr import representation_drawer
from simview.apptrame.app.views.plotter import PLOTS
from simview.apptrame.app.representation import update_representation, create_render_window
from simview.apptrame.app.views.toolbar import toolbar_main
from simview.apptrame.app.views.viewer import content_routers

os.environ["TRAME_DISABLE_V3_WARNING"] = "1"


@TrameApp()
class App:
    def __init__(self, name=None, monitor=False):
        self.server = get_server(name)

        self.server.state.setdefault("active_ui", "geometry")
        self.server.state.setdefault("active_content", "Table")

        model = ModelDataStore(self.server)
        model.init()

        self.model = model
        self.render_window = create_render_window(self.model)

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
        return self.server.protocol.addAttachment(self.model.mesh_source.blob.blob.download_blob().readall())

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
        print("Slider value:", resolution)

    @change("active_plot")
    def update_plot(self, active_plot, **kwargs):
        print("update_plot", active_plot)
        self.ctrl.figure_update(PLOTS[active_plot]())

    @change("mesh_representation")
    def update_mesh_representation(self, mesh_representation=3, **kwargs):
        update_representation(self.model.mesh_actor, mesh_representation)
        self.ctrl.view_update()
        print(f"{mesh_representation=}")

    @change("mesh_opacity")
    def update_mesh_opacity(self, mesh_opacity, **kwargs):
        self.model.mesh_actor.GetProperty().SetOpacity(mesh_opacity)
        self.ctrl.view_update()

    @life_cycle.server_ready
    def on_ready(self, *args, **kwargs):
        print("on_ready")
        self.ctrl.view_update()

    @life_cycle.client_connected
    def on_client_connected(self, *args, **kwargs):
        print("on_client_connected")

    @change("scalar_range")
    def set_scalar_range(self, scalar_range=(-1, 1), **kwargs):
        fields = self.model.mesh_source.fields
        if scalar_range is None:
            scalar_range = fields.default_min, fields.default_max

        print("set_scalar_range", scalar_range)

        self.model.filter_actor.GetMapper().SetScalarRange(scalar_range)
        fields.vtk_filter.SetLowerThreshold(scalar_range[0])
        fields.vtk_filter.SetUpperThreshold(scalar_range[1])

        self.ctrl.view_update()

    def ui(self):
        content_routers(self)

        with SinglePageWithDrawerLayout(self.server) as layout:
            layout.title.set_text(self.server.name)

            with layout.content:
                with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
                    router.RouterView(style="width: 100%; height: 100%")

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
    app = App("FEA Results")
    app.server.start(open_browser=False)
    # check_and_open_webpage("http://localhost:8080", "Trame")
