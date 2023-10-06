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

    curr_mesh = app.model.mesh_source
    if curr_mesh is not None:
        with vuetify.VBtn(icon=True,
                          click=f"utils.download('{curr_mesh.blob.name}', trigger('download_binary'), 'application/octet-stream')", ):
            vuetify.VIcon("mdi-download")

    vuetify.VSwitch(
        hide_details=True,
        v_model=("$vuetify.theme.dark",),
    )

    with vuetify.VBtn(icon=True, click=app.ctrl.view_reset_camera):
        vuetify.VIcon("mdi-crop-free")
