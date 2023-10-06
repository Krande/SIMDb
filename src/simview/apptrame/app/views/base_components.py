from __future__ import annotations

from trame.widgets import vuetify


def ui_card(title, toggle_func):
    with vuetify.VCard(class_="pa-1", outlined=True):
        vuetify.VCardTitle(
            title,
            classes="grey lighten-1 py-1 grey--text text--darken-3",
            style="user-select: none; cursor: pointer",
            hide_details=True,
            dense=True,
            click=toggle_func,
        )
        content = vuetify.VCardText(classes="py-1")
    return content
