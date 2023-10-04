from __future__ import annotations

import os
import pathlib
import tempfile
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import azure.storage.blob
import pyvista as pv
from dotenv import load_dotenv
from vtkmodules.vtkCommonDataModel import vtkDataObject, vtkUnstructuredGrid
from vtkmodules.vtkFiltersCore import vtkThreshold
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader
from vtkmodules.vtkRenderingCore import vtkActor

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
    vtk_filter: vtkThreshold = field(default_factory=vtkThreshold)


@dataclass
class MeshSource:
    blob: BlobFile
    fields: Fields


@dataclass
class ModelDataStore:
    server: Server
    vtk_grid: vtkDataObject = field(default_factory=vtkUnstructuredGrid)
    files: dict[str, BlobFile] = field(default_factory=dict)
    mesh_source: MeshSource = None
    filter_actor: vtkDataObject = field(default_factory=vtkActor)
    mesh_actor: vtkDataObject = field(default_factory=vtkActor)

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

        vtk_filter = vtkThreshold()
        vtk_filter.SetInputData(self.vtk_grid)

        return Fields(
            datasets=dataset_arrays,
            default_array=default_array,
            default_min=default_min,
            default_max=default_max,
            vtk_filter=vtk_filter,
        )

    def download_file(self):
        blob = self.files[self.server.state.active_model]

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
                self.vtk_grid = reader.GetOutput()
        finally:
            os.remove(filepath)  # Manually delete the file

        fields = self._extract_fields()
        self.mesh_source = MeshSource(blob=blob, fields=fields)

    def load_files_from_storage_blob(self):
        container_client = azure.storage.blob.ContainerClient.from_connection_string(
            os.getenv("AZURE_STORAGE_CONNECTION_STRING"), os.getenv("AZURE_STORAGE_CONTAINER_NAME")
        )

        self.files.clear()
        files = {}
        for blob in container_client.list_blobs():
            blob_client = container_client.get_blob_client(blob.name)
            suffix = pathlib.Path(blob.name).suffix
            if suffix != ".vtu":
                continue
            files[blob.name] = BlobFile(name=blob.name, suffix=suffix, blob=blob_client)
        self.files.update(files)

        if len(self.files) > 0:
            self.server.state.active_model = list(self.files.keys())[0]

    def init(self):
        self.load_files_from_storage_blob()
        self.download_file()
