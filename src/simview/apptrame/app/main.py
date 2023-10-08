import os

# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
import vtkmodules.vtkRenderingOpenGL2  # noqa
from trame.app import get_server
from trame.decorators import TrameApp, trigger, life_cycle
from trame.widgets import vuetify, router
from trame_vuetify.ui.vuetify import SinglePageWithDrawerLayout
# Required for interactor initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa

from simview.apptrame.app.filewatcher import start_monitoring
from simview.apptrame.app.model_store import ModelDataStore
from simview.apptrame.app.views.draw_model import file_reader_main
from simview.apptrame.app.views.draw_plotter import plotter_drawer
from simview.apptrame.app.views.draw_repr import representation_drawer
from simview.apptrame.app.views.toolbar import toolbar_main
from simview.apptrame.app.views.view_model import content_routers

os.environ["TRAME_DISABLE_V3_WARNING"] = "1"


@TrameApp()
class App:
    def __init__(self, name=None, monitor=False):
        self.server = get_server(name)
        self.server.state.trame__title = name
        self.local_view = None

        self.model = ModelDataStore(self.server)
        self.model.init()

        self.ui()

        if monitor:
            start_monitoring(self.server)

    @property
    def state(self):
        return self.server.state

    @property
    def ctrl(self):
        return self.server.controller

    @trigger("click_me")
    def click_me(self, *args):
        print("method_on_ctrl", args)

    @life_cycle.server_ready
    def on_ready(self, *args, **kwargs):
        print("on_ready")

    @life_cycle.client_connected
    def on_client_connected(self, *args, **kwargs):
        print("on_client_connected")

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
                file_reader_main(self)
                representation_drawer(self)
                plotter_drawer(self)


if __name__ == "__main__":
    app = App("FEA Results", monitor=False)
    app.server.start(open_browser=False)
