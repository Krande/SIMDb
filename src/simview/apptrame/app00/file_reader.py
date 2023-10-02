import pathlib
from dataclasses import dataclass
import pyvista as pv
import meshio


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
