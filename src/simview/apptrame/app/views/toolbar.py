from __future__ import annotations

from typing import TYPE_CHECKING

from trame.widgets import vuetify

if TYPE_CHECKING:
    from simview.apptrame.app.main import App


def click_me(*args):
    print(f"click with {args}")


def toolbar_main(app: App):
    vuetify.VSpacer()
    vuetify.VDivider(vertical=True, classes="mx-2")

    with vuetify.VBtn(icon=True, click=(click_me, "['edit',]")):
        vuetify.VIcon("mdi-cursor-default-click")

    curr_mesh = app.model.current_mesh
    if curr_mesh is not None:
        with vuetify.VBtn(icon=True,
                          click=f"utils.download('{curr_mesh.blob.name}', trigger('download_binary'), 'application/octet-stream')", ):
            vuetify.VIcon("mdi-download")

    vuetify.VSlider(
        hide_details=True,
        v_model=("resolution", 6),
        max=60,
        min=3,
        step=1,
        style="max-width: 300px;",
    )

    vuetify.VSwitch(
        hide_details=True,
        v_model=("$vuetify.theme.dark",),
    )

    with vuetify.VBtn(icon=True, click="$refs.view.resetCamera()"):
        vuetify.VIcon("mdi-crop-free")
