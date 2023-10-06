from __future__ import annotations

import os
import pathlib
import tempfile
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import azure.storage.blob
import pyvista as pv
from dotenv import load_dotenv
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkDataObject, vtkUnstructuredGrid
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import vtkActor, vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor

from simview.apptrame.app.representation import Fields, init_filter_pipeline, set_current_filter_array

if TYPE_CHECKING:
    from trame_server import Server
load_dotenv()


@dataclass
class BlobFile:
    name: str
    suffix: str
    blob: azure.storage.blob.BlobClient


class MeshSource:
    files: dict[str, BlobFile] = {}

    def __init__(self, blob: BlobFile):
        self.blob = blob


@dataclass
class ModelDataStore:
    server: Server

    mesh_source: MeshSource = None
    fields: Fields = None

    vtk_grid: vtkUnstructuredGrid = field(default_factory=vtkUnstructuredGrid)
    filter_actor: vtkDataObject = field(default_factory=vtkActor)
    mesh_actor: vtkDataObject = field(default_factory=vtkActor)
    renderer: vtkRenderer = field(default_factory=vtkRenderer)
    render_window: vtkRenderWindow = field(default_factory=vtkRenderWindow)

    def _extract_fields(self) -> Fields:
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

        default_array = dataset_arrays[0]
        default_min, default_max = default_array.get("range")

        return Fields(
            datasets=dataset_arrays, default_array=default_array, default_min=default_min, default_max=default_max
        )

    def download_and_activate_file(self):
        blob = MeshSource.files[self.server.state.active_model]

        with tempfile.NamedTemporaryFile(delete=False, suffix=blob.suffix) as temp:
            temp.write(blob.blob.download_blob().readall())
            temp.seek(0)

            filepath = temp.name

        try:
            if blob.suffix == ".rmed":
                mesh: pv.DataSet = pv.read_meshio(filepath, "med")
                self.vtk_grid.ShallowCopy(mesh)
            else:
                reader = vtkXMLUnstructuredGridReader()
                reader.SetFileName(filepath)
                reader.Update()
                self.vtk_grid.ShallowCopy(reader.GetOutput())
        finally:
            os.remove(filepath)  # Manually delete the file

        self.fields = self._extract_fields()
        self.mesh_source = MeshSource(blob=blob)
        self.server.state.loaded_file = self.server.state.active_model

    def load_files_from_storage_blob(self):
        container_client = azure.storage.blob.ContainerClient.from_connection_string(
            os.getenv("AZURE_STORAGE_CONNECTION_STRING"), os.getenv("AZURE_STORAGE_CONTAINER_NAME")
        )
        MeshSource.files.clear()
        files = {}
        for blob in container_client.list_blobs():
            blob_client = container_client.get_blob_client(blob.name)
            suffix = pathlib.Path(blob.name).suffix
            if suffix != ".vtu":
                continue
            files[blob.name] = BlobFile(name=blob.name, suffix=suffix, blob=blob_client)
        MeshSource.files.update(files)

        if len(MeshSource.files) > 0:
            keys = list(MeshSource.files.keys())
            self.server.state.fea_files = keys
            self.server.state.active_model = keys[0]

    def init(self, update=False, active_model=None):
        if len(MeshSource.files) == 0 or update is True:
            self.load_files_from_storage_blob()

        self.download_and_activate_file()

        renderer = self.renderer
        render_window = self.render_window
        renderer.SetBackground(vtkNamedColors().GetColor3d("SlateGray"))  # SlateGray

        render_window.AddRenderer(renderer)
        render_window.SetWindowName("FEA Main")

        render_window_interactor = vtkRenderWindowInteractor()
        interactor_style = vtkInteractorStyleTrackballCamera()
        render_window_interactor.SetInteractorStyle(interactor_style)
        render_window_interactor.SetRenderWindow(render_window)

        init_filter_pipeline(self, renderer)
        set_current_filter_array(self, self.fields.default_array.get("text"))

        renderer.ResetCamera()
