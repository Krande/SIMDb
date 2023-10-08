from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from trame.decorators import trigger, change
from trame.widgets import vuetify

from simview.apptrame.app.base import AppExtend
from simview.apptrame.app.model_store import ModelDataStore
from simview.apptrame.app.representation import update_representation
from simview.apptrame.app.views.base_components import ui_card

if TYPE_CHECKING:
    from simview.apptrame.app.main import App


class EigenType(str, Enum):
    eigen = "Eigen"
    static = "Static"
    UNKNOWN = "Unknown"


class ModelUI(AppExtend):
    @change("active_model")
    def on_active_model_change(self, active_model, **kwargs):
        print("updated -> ", active_model)
        model_already_loaded = False
        if hasattr(self.app.server.state, "loaded_file") and self.app.server.state.loaded_file == active_model:
            model_already_loaded = True

        if model_already_loaded:
            return

        self.app.model = ModelDataStore(self.app.server)
        self.app.model.init()

        self.app.local_view.replace_view(self.app.model.render_window)
        self.app.ctrl.view_update = self.app.local_view.update
        update_representation(self.app.model.mesh_actor, self.app.server.state.mesh_representation)
        update_representation(self.app.model.filter_actor, self.app.server.state.filter_representation)
        self.app.model.mesh_actor.GetProperty().SetOpacity(self.app.server.state.mesh_opacity)
        self.app.model.filter_actor.GetProperty().SetOpacity(self.app.server.state.filter_opacity)
        self.app.ctrl.view_update()

    @trigger("download_binary")
    def download(self):
        return self.app.server.protocol.addAttachment(self.app.model.mesh_source.blob.blob.download_blob().readall())

    @change("active_model_type")
    def on_active_model_type_change(self, active_model_type: EigenType, **kwargs):
        if active_model_type == str(EigenType.eigen):
            print("This is an eigenvalue analysis")

        elif active_model_type == str(EigenType.static):
            print("This is a static analysis")
        else:
            print("updated -> ", active_model_type)
        self.app.ctrl.view_update()

    def toggle_model(self, *args):
        self.app.state.model_view = not self.app.state.model_view
        self.app.ctrl.view_update()


def file_reader_main(app: App):
    app.state.model_view = True
    eigen_keys = [str(x) for x in EigenType]
    mui = ModelUI(app)
    with ui_card("Model", mui.toggle_model):
        with vuetify.VCol(v_show=f"model_view == true", dense=True):
            vuetify.VSelect(
                label="FEA File",
                v_model=("active_model", None),
                items=("fea_files", []),
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-2",
            )

            vuetify.VSelect(
                label="FEA Type",
                v_model=("active_model_type", str(EigenType.UNKNOWN)),
                items=("fea_types", eigen_keys),
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-2",
            )
            vuetify.VSelect(
                label="EigenModes",
                v_show=f"active_model_type == '{str(EigenType.eigen)}'",
                v_model=("active_eigen", None),
                items=("eigen", []),
                hide_details=True,
                dense=True,
                outlined=True,
            )
