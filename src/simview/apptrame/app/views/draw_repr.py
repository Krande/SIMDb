from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from trame.app import asynchronous
from trame.decorators import change, trigger
from trame.widgets import vuetify

from simview.apptrame.app.base import AppExtend
from simview.apptrame.app.representation import Representation, update_representation
from simview.apptrame.app.views.base_components import ui_card

if TYPE_CHECKING:
    from simview.apptrame.app.main import App


class DrawUI(AppExtend):
    @change("warp_scale")
    def update_warp(self, warp_scale, **kwargs):
        if not self.app.model.fields:
            return

        self.app.model.fields.warp_vector.SetScaleFactor(warp_scale)  # Set the scale factor as needed
        self.app.ctrl.view_update()
        # print(f"{warp_scale=}")

    @change("mesh_representation")
    def update_mesh_representation(self, mesh_representation=3, **kwargs):
        update_representation(self.app.model.mesh_actor, mesh_representation)
        self.app.ctrl.view_update()
        # print(f"{mesh_representation=}")

    @change("filter_representation")
    def update_filter_representation(self, filter_representation=3, **kwargs):
        update_representation(self.app.model.filter_actor, filter_representation)
        self.app.ctrl.view_update()
        # print(f"{filter_representation=}")

    @change("mesh_opacity")
    def update_mesh_opacity(self, mesh_opacity, **kwargs):
        self.app.model.mesh_actor.GetProperty().SetOpacity(mesh_opacity)
        self.app.ctrl.view_update()
        # print(f"{mesh_opacity=}")

    @change("filter_opacity")
    def update_filter_opacity(self, filter_opacity, **kwargs):
        self.app.model.filter_actor.GetProperty().SetOpacity(filter_opacity)
        self.app.ctrl.view_update()
        # print(f"{filter_opacity=}")

    @change("scalar_range")
    def set_scalar_range(self, scalar_range=(-1, 1), **kwargs):
        fields = self.app.model.fields

        if scalar_range is None:
            scalar_range = fields.default_min, fields.default_max

        filter_mapper = self.app.model.filter_actor.GetMapper()
        vtk_filter = self.app.model.fields.vtk_filter

        # print("set_scalar_range", scalar_range)
        filter_mapper.SetScalarRange(*scalar_range)  # Comment if you want to have a fix color range

        vtk_filter.SetLowerThreshold(scalar_range[0])
        vtk_filter.SetUpperThreshold(scalar_range[1])
        vtk_filter.Update()

        lut = filter_mapper.GetLookupTable()
        lut.SetRange(scalar_range)
        lut.Build()

        self.app.ctrl.view_update()

    @trigger("start_animation")
    @asynchronous.task
    async def _update(self, **kwargs):
        # print("start_animation")
        self.app.server.state.keep_animating = True
        max_warp_scale = self.app.server.state.warp_scale
        warp_scale_start = -max_warp_scale
        warp_scale_end = max_warp_scale
        current_warp_scale = self.app.server.state.warp_scale
        direction = 1
        while self.app.server.state.keep_animating:
            if current_warp_scale > warp_scale_end:
                direction = -1
            elif current_warp_scale < warp_scale_start:
                direction = 1
            current_warp_scale += 0.1 * direction
            self.app.model.fields.warp_vector.SetScaleFactor(current_warp_scale)  # Set the scale factor as needed
            self.app.ctrl.view_update()
            # print(f"{current_warp_scale=}")
            await asyncio.sleep(1/15)

    @trigger("stop_animation")
    @asynchronous.task
    async def _stop(self, **kwargs):
        # print("stop_animation")
        self.app.server.state.keep_animating = False

    def toggle_drawer(self, *args):
        self.app.state.drawer = not self.app.state.drawer
        self.app.ctrl.view_update()


def representation_drawer(app: App):
    app.state.drawer = True
    dui = DrawUI(app)
    sel = "pt-2"
    with ui_card("Representation", dui.toggle_drawer):
        with vuetify.VCol(outlined=False, v_show=f"drawer == true", dense=True):
            vuetify.VSelect(
                # Representation
                v_model=("mesh_representation", Representation.Surface),
                items=(
                    "representations",
                    [
                        {"text": "Points", "value": 0},
                        {"text": "Wireframe", "value": 1},
                        {"text": "Surface", "value": 2},
                        {"text": "Surface With Edges", "value": 3},
                    ],
                ),
                label="Mesh Representation",
                hide_details=True,
                dense=True,
                outlined=True,
                classes=sel,
            )

            vuetify.VSelect(
                # Representation
                v_model=("filter_representation", Representation.SurfaceWithEdges),
                items=(
                    "representations",
                    [
                        {"text": "Points", "value": 0},
                        {"text": "Wireframe", "value": 1},
                        {"text": "Surface", "value": 2},
                        {"text": "Surface With Edges", "value": 3},
                    ],
                ),
                label="Filter Representation",
                hide_details=True,
                dense=True,
                outlined=True,
                classes=sel,
            )

            vuetify.VSlider(
                # Mesh Opacity
                v_model=("mesh_opacity", 0.5),
                min=0,
                max=1,
                step=0.1,
                label="Mesh Opacity",
                classes="mt-1",
                hide_details=True,
                dense=True,
            )

            vuetify.VSlider(
                # Filter Opacity
                v_model=("filter_opacity", 1.0),
                min=0,
                max=1,
                step=0.1,
                label="Filter Opacity",
                classes="mt-1",
                hide_details=True,
                dense=True,
            )

            vuetify.VRangeSlider(
                thumb_size=16,
                thumb_label=True,
                label="Threshold",
                v_model=("scalar_range", [0, 300]),
                min=("full_min", -1),
                max=("full_max", 1),
                step=("range_step", 1),
                dense=True,
                hide_details=True,
                style="max-width: 400px",
            )

            vuetify.VSlider(
                # Opacity
                v_model=("warp_scale", 1.0),
                thumb_label=True,
                min=0,
                max=10,
                step=0.1,
                label="Warp Scale",
                classes="mt-1",
                hide_details=True,
                dense=True,
            )
            with vuetify.VBtn(click=("start_animation", )):
                vuetify.VIcon("mdi-play")
            with vuetify.VBtn(click=("stop_animation", )):
                vuetify.VIcon("mdi-stop")
