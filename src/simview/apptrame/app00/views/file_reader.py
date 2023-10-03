from __future__ import annotations

import os
import pathlib
import tempfile
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import azure.storage.blob
import meshio
import pyvista as pv
from dotenv import load_dotenv
from trame.widgets import vuetify
from vtkmodules.vtkCommonDataModel import vtkDataObject, vtkUnstructuredGrid

if TYPE_CHECKING:
    from trame_server import Server

load_dotenv()


@dataclass
class BlobFile:
    name: str
    suffix: str
    blob: azure.storage.blob.BlobClient


@dataclass
class Fields:
    datasets: list
    default_array: dict
    default_min: float
    default_max: float


@dataclass
class Mesh:
    blob: BlobFile
    mesh: pv.DataSet
    mmesh: meshio.Mesh
    fields: Fields


@dataclass
class ModelDataStore:
    server: Server
    vtk_grid: vtkDataObject = field(default_factory=vtkUnstructuredGrid)
    files: dict[str, BlobFile] = field(default_factory=dict)
    current_mesh: Mesh = None
    contour_actor: vtkDataObject = None

    def extract_fields(self) -> Fields:
        dataset_arrays = []
        point_data = self.vtk_grid.GetPointData()
        cell_data = self.vtk_grid.GetCellData()
        fields = [
            (point_data, vtkDataObject.FIELD_ASSOCIATION_POINTS),
            (cell_data, vtkDataObject.FIELD_ASSOCIATION_CELLS),
        ]

        for field in fields:
            field_arrays, association = field
            for i in range(field_arrays.GetNumberOfArrays()):
                array = field_arrays.GetArray(i)
                array_range = array.GetRange()
                dataset_arrays.append(
                    {
                        "text": array.GetName(),
                        "value": i,
                        "range": list(array_range),
                        "type": association,
                    }
                )

        default_array = dataset_arrays[1]
        default_min, default_max = default_array.get("range")
        return Fields(datasets=dataset_arrays, default_array=default_array, default_min=default_min,
                      default_max=default_max)

    def download_file(self):
        blob = self.files[self.server.state.active_model]

        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.write(blob.blob.download_blob().readall())
            temp.seek(0)

            filepath = temp.name

        try:
            mmesh = meshio.read(filepath, "med")
            mesh: pv.DataSet = pv.read_meshio(filepath, "med")
        finally:
            os.remove(filepath)  # Manually delete the file

        self.vtk_grid.ShallowCopy(mesh)
        fields = self.extract_fields()
        self.vtk_grid.GetCellData().SetActiveScalars(fields.default_array.get("text"))
        self.current_mesh = Mesh(blob=blob, mesh=mesh, mmesh=mmesh, fields=fields)

    def load_files_from_storage_blob(self):
        container_client = azure.storage.blob.ContainerClient.from_connection_string(
            os.getenv("AZURE_STORAGE_CONNECTION_STRING"), os.getenv('AZURE_STORAGE_CONTAINER_NAME'))

        self.files.clear()
        files = {}
        for blob in container_client.list_blobs():
            blob_client = container_client.get_blob_client(blob.name)
            suffix = pathlib.Path(blob.name).suffix
            files[blob.name] = BlobFile(name=blob.name, suffix=suffix, blob=blob_client)
        self.files.update(files)

        if len(self.files) > 0:
            self.server.state.active_model = list(self.files.keys())[0]


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

        # with vuetify.VBtn(icon=True, click=model.download_file):
        #     vuetify.VIcon("mdi-cursor-default-click")
