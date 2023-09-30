from __future__ import annotations

from dataclasses import dataclass

# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
import vtkmodules.vtkRenderingOpenGL2  # noqa
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vtk, vuetify, trame

# Required for interactor initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa

from simview.apptrame.callbacks import ViewCalls, Representation, LookupTable, actives_change
from simview.apptrame.data import VtkData
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from trame.app import Server as TrameServer


# -----------------------------------------------------------------------------
# GUI elements
# -----------------------------------------------------------------------------
@dataclass
class VtkGui:
    server: TrameServer
    vtk_data: VtkData
    view_calls: ViewCalls

    def standard_buttons(self):
        vuetify.VCheckbox(
            v_model=("cube_axes_visibility", True),
            on_icon="mdi-cube-outline",
            off_icon="mdi-cube-off-outline",
            classes="mx-1",
            hide_details=True,
            dense=True,
        )
        vuetify.VCheckbox(
            v_model="$vuetify.theme.dark",
            on_icon="mdi-lightbulb-off-outline",
            off_icon="mdi-lightbulb-outline",
            classes="mx-1",
            hide_details=True,
            dense=True,
        )
        vuetify.VCheckbox(
            v_model=("viewMode", "local"),
            on_icon="mdi-lan-disconnect",
            off_icon="mdi-lan-connect",
            true_value="local",
            false_value="remote",
            classes="mx-1",
            hide_details=True,
            dense=True,
        )
        with vuetify.VBtn(icon=True, click="$refs.view.resetCamera()"):
            vuetify.VIcon("mdi-crop-free")

    def pipeline_widget(self):
        trame.GitTree(
            sources=(
                "pipeline",
                [
                    {"id": "1", "parent": "0", "visible": 1, "name": "Mesh"},
                    {"id": "2", "parent": "1", "visible": 1, "name": "Contour"},
                ],
            ),
            actives_change=(actives_change, "[$event]"),
            visibility_change=(self.view_calls.visibility_change, "[$event]"),
        )

    def ui_card(self, title, ui_name):
        with vuetify.VCard(v_show=f"active_ui == '{ui_name}'"):
            vuetify.VCardTitle(
                title,
                classes="grey lighten-1 py-1 grey--text text--darken-3",
                style="user-select: none; cursor: pointer",
                hide_details=True,
                dense=True,
            )
            content = vuetify.VCardText(classes="py-2")
        return content

    def mesh_card(self):
        with self.ui_card(title="Mesh", ui_name="mesh"):
            vuetify.VSelect(
                # Representation
                v_model=("mesh_representation", Representation.Surface),
                items=(
                    "representations",
                    [
                        {"text": "Points", "value": 0},
                        {"text": "Wireframe", "value": 1},
                        {"text": "Surface", "value": 2},
                        {"text": "SurfaceWithEdges", "value": 3},
                    ],
                ),
                label="Representation",
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-1",
            )
            with vuetify.VRow(classes="pt-2", dense=True):
                with vuetify.VCol(cols="6"):
                    vuetify.VSelect(
                        # Color By
                        label="Color by",
                        v_model=("mesh_color_array_idx", 0),
                        items=("array_list", self.vtk_data.dataset_arrays),
                        hide_details=True,
                        dense=True,
                        outlined=True,
                        classes="pt-1",
                    )
                with vuetify.VCol(cols="6"):
                    vuetify.VSelect(
                        # Color Map
                        label="Colormap",
                        v_model=("mesh_color_preset", LookupTable.Rainbow),
                        items=(
                            "colormaps",
                            [
                                {"text": "Rainbow", "value": 0},
                                {"text": "Inv Rainbow", "value": 1},
                                {"text": "Greyscale", "value": 2},
                                {"text": "Inv Greyscale", "value": 3},
                            ],
                        ),
                        hide_details=True,
                        dense=True,
                        outlined=True,
                        classes="pt-1",
                    )
            vuetify.VSlider(
                # Opacity
                v_model=("mesh_opacity", 1.0),
                min=0,
                max=1,
                step=0.1,
                label="Opacity",
                classes="mt-1",
                hide_details=True,
                dense=True,
            )

    def contour_card(self):
        with self.ui_card(title="Contour", ui_name="contour"):
            vuetify.VSelect(
                # Contour By
                label="Contour by",
                v_model=("contour_by_array_idx", 0),
                items=("array_list", self.vtk_data.dataset_arrays),
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-1",
            )
            vuetify.VSlider(
                # Contour Value
                v_model=("contour_value", self.vtk_data.contour_value),
                min=("contour_min", self.vtk_data.default_min),
                max=("contour_max", self.vtk_data.default_max),
                step=("contour_step", 0.01 * (self.vtk_data.default_max - self.vtk_data.default_min)),
                label="Value",
                classes="my-1",
                hide_details=True,
                dense=True,
            )
            vuetify.VSelect(
                # Representation
                v_model=("contour_representation", Representation.Surface),
                items=(
                    "representations",
                    [
                        {"text": "Points", "value": 0},
                        {"text": "Wireframe", "value": 1},
                        {"text": "Surface", "value": 2},
                        {"text": "SurfaceWithEdges", "value": 3},
                    ],
                ),
                label="Representation",
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-1",
            )
            with vuetify.VRow(classes="pt-2", dense=True):
                with vuetify.VCol(cols="6"):
                    vuetify.VSelect(
                        # Color By
                        label="Color by",
                        v_model=("contour_color_array_idx", 0),
                        items=("array_list", self.vtk_data.dataset_arrays),
                        hide_details=True,
                        dense=True,
                        outlined=True,
                        classes="pt-1",
                    )
                with vuetify.VCol(cols="6"):
                    vuetify.VSelect(
                        # Color Map
                        label="Colormap",
                        v_model=("contour_color_preset", LookupTable.Rainbow),
                        items=(
                            "colormaps",
                            [
                                {"text": "Rainbow", "value": 0},
                                {"text": "Inv Rainbow", "value": 1},
                                {"text": "Greyscale", "value": 2},
                                {"text": "Inv Greyscale", "value": 3},
                            ],
                        ),
                        hide_details=True,
                        dense=True,
                        outlined=True,
                        classes="pt-1",
                    )
            vuetify.VSlider(
                # Opacity
                v_model=("contour_opacity", 1.0),
                min=0,
                max=1,
                step=0.1,
                label="Opacity",
                classes="mt-1",
                hide_details=True,
                dense=True,
            )

    def create_gui(self):
        with SinglePageWithDrawerLayout(self.server) as layout:
            layout.title.set_text("Viewer")

            with layout.toolbar:
                # toolbar components
                vuetify.VSpacer()
                vuetify.VDivider(vertical=True, classes="mx-2")
                self.standard_buttons()

            with layout.drawer as drawer:
                # drawer components
                drawer.width = 325
                self.pipeline_widget()
                vuetify.VDivider(classes="mb-2")
                self.mesh_card()
                self.contour_card()

            with layout.content:
                # content components
                with vuetify.VContainer(
                        fluid=True,
                        classes="pa-0 fill-height",
                ):
                    # view = vtk.VtkRemoteView(renderWindow, interactive_ratio=1)
                    view = vtk.VtkLocalView(self.vtk_data.renderWindow)
                    # view = vtk.VtkRemoteLocalView(
                    #     renderWindow, namespace="view", mode="local", interactive_ratio=1
                    # )
                    self.server.controller.view_update = view.update
                    self.server.controller.view_reset_camera = view.reset_camera
