from trame.widgets import vuetify


def clickme():
    print("You clicked me Update!")


def toolbar_main(curr_mesh):
    vuetify.VSpacer()
    # Icons https://pictogrammers.com/library/mdi/
    with vuetify.VBtn(icon=True, click=clickme):
        vuetify.VIcon("mdi-cursor-default-click")

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
