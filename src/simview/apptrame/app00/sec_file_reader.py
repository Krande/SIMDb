import os
import pathlib
from dataclasses import dataclass

import azure.storage.blob
import meshio
import pyvista as pv
from dotenv import load_dotenv
from trame.app import get_server
from trame.widgets import vuetify
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid

load_dotenv()

server = get_server()
state, ctrl = server.state, server.controller

FILES = {}


@dataclass
class BlobFile:
    name: str
    blob: azure.storage.blob.BlobClient


@ctrl.on_server_ready
def load_files_from_storage_blob():
    container_client = azure.storage.blob.ContainerClient.from_connection_string(
        os.getenv("AZURE_STORAGE_CONNECTION_STRING"), os.getenv('AZURE_STORAGE_CONTAINER_NAME'))

    FILES.clear()
    for blob in container_client.list_blobs():
        if blob.name.endswith(".rmed"):
            FILES[blob.name] = BlobFile(name=blob.name, blob=blob)


@dataclass
class Mesh:
    filepath: pathlib.Path
    mesh: pv.DataSet
    mmesh: meshio.Mesh


def read_file(vtk_grid) -> Mesh:
    data_dir = pathlib.Path(__file__).parent.parent.parent.absolute() / "data"
    rmed_file = data_dir / "Cantilever_CA_EIG_sh_modes.rmed"
    mmesh = meshio.read(rmed_file, "med")
    mesh: pv.DataSet = pv.read_meshio(rmed_file, "med")

    vtk_grid.ShallowCopy(mesh)
    return Mesh(filepath=rmed_file, mesh=mesh, mmesh=mmesh)


def download_file(vtk_grid: vtkUnstructuredGrid):
    blob = FILES[state.active_model]

    blob_data = blob.blob.download_blob().readall()
    mmesh = meshio.read(blob_data, "med")
    mesh: pv.DataSet = pv.read_meshio(blob_data, "med")

    vtk_grid.ShallowCopy(mesh)
    return Mesh(filepath=blob, mesh=mesh, mmesh=mmesh)


def file_reader_main():
    _files = list(FILES.keys())
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

        with vuetify.VBtn(icon=True, click=download_file):
            vuetify.VIcon("mdi-cursor-default-click")
