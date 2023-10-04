from __future__ import annotations

from trame.widgets import vuetify

from simview.apptrame.app.model_store import ModelDataStore


def file_reader_main(model: ModelDataStore):
    _files = list(model.files.keys())
    with vuetify.VRow(classes="pt-2", dense=True):
        vuetify.VSelect(
            label="Models",
            v_model=("active_model", _files[0] if len(_files) > 0 else None),
            items=("Model", _files),
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
        )

