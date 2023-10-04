from __future__ import annotations

from trame.widgets import vuetify

from simview.apptrame.app.representation import Representation


def representation_drawer():
    with vuetify.VRow(classes="pt-2", dense=True):
        vuetify.VSelect(
            # Representation
            v_model=("mesh_representation", Representation.SurfaceWithEdges),
            items=(
                "representations",
                [
                    {"text": "Points", "value": 0},
                    {"text": "Wireframe", "value": 1},
                    {"text": "Surface", "value": 2},
                    {"text": "Surface With Edges", "value": 3},
                ],
            ),
            label="Representation",
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
    vuetify.VRangeSlider(
        thumb_size=16,
        thumb_label=True,
        label="Range",
        v_model=("scalar_range", [0, 300]),
        min=("0",),
        max=("500",),
        dense=True,
        hide_details=True,
        style="max-width: 400px",
    )
