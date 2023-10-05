"""
Version for trame 1.x - https://github.com/Kitware/trame/blob/release-v1/examples/VTK/Applications/FiniteElementAnalysis/app_local_view.py
Delta v1..v2          - https://github.com/Kitware/trame/commit/03f28bb0084490acabf218264b96a1dbb3a17f19
"""

import io

import numpy as np
import pandas as pd
import trame_server.controller
import vtkmodules.vtkRenderingOpenGL2  # noqa
# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
import vtkmodules.vtkRenderingOpenGL2  # noqa
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, vtk
from vtkmodules.numpy_interface.dataset_adapter import numpyTovtkDataArray as np2da
from vtkmodules.util import vtkConstants
from vtkmodules.util.numpy_support import vtk_to_numpy
from vtkmodules.vtkCommonCore import vtkPoints, vtkLookupTable, vtkTypeFloat64Array
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid, vtkCellArray, vtkDataObject, vtkPointData
from vtkmodules.vtkFiltersCore import vtkThreshold
from vtkmodules.vtkFiltersGeneral import vtkWarpVector
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader
# Add import for the rendering
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

# Change data directory to a pathlib variable of your local directory containing the mesh files
from simview.helpers import DATA_DIR

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller

STEPS = {}

# -----------------------------------------------------------------------------
# VTK pipeline
# -----------------------------------------------------------------------------

vtk_grid = vtkUnstructuredGrid()
vtk_filter = vtkThreshold()
vtk_filter.SetInputData(vtk_grid)

renderer = vtkRenderer()
renderer.SetBackground(0.8, 0.8, 0.8)
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

warp_vector = vtkWarpVector()
warp_vector.SetInputData(vtk_grid)

filter_mapper = vtkDataSetMapper()
filter_mapper.SetInputConnection(vtk_filter.GetOutputPort())

filter_actor = vtkActor()
filter_actor.SetMapper(filter_mapper)
renderer.AddActor(filter_actor)

lut = vtkLookupTable()
lut.SetHueRange(0.667, 0)
lut.Build()
filter_mapper.SetLookupTable(lut)

mesh_mapper = vtkDataSetMapper()
mesh_mapper.SetInputData(vtk_grid)
mesh_mapper.SetScalarVisibility(0)

mesh_actor = vtkActor()
mesh_actor.SetMapper(mesh_mapper)
renderer.AddActor(mesh_actor)

scalar_bar = vtkScalarBarActor()
scalar_bar.SetLookupTable(filter_mapper.GetLookupTable())
scalar_bar.SetNumberOfLabels(7)
scalar_bar.UnconstrainedFontSizeOn()
scalar_bar.SetMaximumWidthInPixels(100)
scalar_bar.SetMaximumHeightInPixels(800 // 3)
renderer.AddActor2D(scalar_bar)


def set_scalar_bar_precision(max_scalar, title):
    scalar_bar.SetTitle(title)

    if max_scalar < 1:
        precision = 4
    elif max_scalar < 10:
        precision = 3
    elif max_scalar < 100:
        precision = 2
    else:
        precision = 1

    scalar_bar.SetLabelFormat(f"%-#6.{precision}f")

    return scalar_bar


@state.change("threshold_range")
def update_filter(threshold_range, **kwargs):
    if len(STEPS) > 0:
        float_range = STEPS[threshold_range[0]], STEPS[threshold_range[1]]
    else:
        float_range = threshold_range

    filter_mapper.SetScalarRange(*float_range)  # Comment if you want to have a fix color range

    vtk_filter.SetLowerThreshold(float_range[0])
    vtk_filter.SetUpperThreshold(float_range[1])
    vtk_filter.Update()
    lut.SetRange(*float_range)
    lut.Build()

    print(f"{float_range=}, Scalar Range: {filter_mapper.GetScalarRange()}")
    ctrl.view_update()


def update_mesh_representations():
    color = [0.3, 0.3, 0.3]
    representation = 1
    opacity = 0.2

    property = mesh_actor.GetProperty()
    property.SetRepresentation(representation)
    property.SetColor(color)
    property.SetOpacity(opacity)
    ctrl.view_update()


@state.change("warp_scale")
def update_warp(warp_scale, **kwargs):
    warp_vector.SetScaleFactor(warp_scale)  # Set the scale factor as needed
    ctrl.view_update()


def load_solid_model():
    """Load a solid model from a set of files"""
    nodes_bytes = (DATA_DIR / "ip_nodes.txt").read_bytes()
    elems_bytes = (DATA_DIR / "ip_elems.txt").read_bytes()
    field_bytes = (DATA_DIR / "ip_elems_seqv.txt").read_bytes()

    df_nodes = pd.read_csv(
        io.StringIO(nodes_bytes.decode("utf-8")),
        delim_whitespace=True,
        header=None,
        skiprows=1,
        names=["id", "x", "y", "z"],
    )

    df_nodes["id"] = df_nodes["id"].astype(int)
    df_nodes = df_nodes.set_index("id", drop=True)
    # fill missing ids in range as VTK uses position (index) to map cells to points
    df_nodes = df_nodes.reindex(np.arange(df_nodes.index.min(), df_nodes.index.max() + 1), fill_value=0)

    df_elems = pd.read_csv(
        io.StringIO(elems_bytes.decode("utf-8")),
        skiprows=1,
        header=None,
        delim_whitespace=True,
        engine="python",
        index_col=None,
    ).sort_values(0)
    # order: 0: eid, 1: eshape, 2+: nodes, iloc[:,0] is index
    df_elems.iloc[:, 0] = df_elems.iloc[:, 0].astype(int)

    n_nodes = df_elems.iloc[:, 1].map(lambda x: int("".join(i for i in x if i.isdigit())))
    df_elems.insert(2, "n_nodes", n_nodes)
    # fill missing ids in range as VTK uses position (index) to map data to cells
    new_range = np.arange(df_elems.iloc[:, 0].min(), df_elems.iloc[:, 0].max() + 1)
    df_elems = df_elems.set_index(0, drop=False).reindex(new_range, fill_value=0)

    # mapping specific to Ansys Mechanical data
    vtk_shape_id_map = {
        "Tet4": vtkConstants.VTK_TETRA,
        "Tet10": vtkConstants.VTK_QUADRATIC_TETRA,
        "Hex8": vtkConstants.VTK_HEXAHEDRON,
        "Hex20": vtkConstants.VTK_QUADRATIC_HEXAHEDRON,
        "Tri6": vtkConstants.VTK_QUADRATIC_TRIANGLE,
        "Quad8": vtkConstants.VTK_QUADRATIC_QUAD,
        "Tri3": vtkConstants.VTK_TRIANGLE,
        "Quad4": vtkConstants.VTK_QUAD,
        "Wed15": vtkConstants.VTK_QUADRATIC_WEDGE,
    }
    df_elems["cell_types"] = np.nan
    df_elems.loc[df_elems.loc[:, 0] > 0, "cell_types"] = df_elems.loc[df_elems.loc[:, 0] > 0, 1].map(
        lambda x: vtk_shape_id_map[x.strip()] if x.strip() in vtk_shape_id_map.keys() else np.nan
    )
    df_elems = df_elems.dropna(subset=["cell_types"], axis=0)

    # convert dataframes to vtk-desired format
    points = df_nodes[["x", "y", "z"]].to_numpy()
    cell_types = df_elems["cell_types"].to_numpy()
    n_nodes = df_elems.loc[:, "n_nodes"].to_numpy()
    # subtract starting node id from all grid references in cells to avoid filling from 0 to first used node (in case mesh doesnt start at 1)
    p = df_elems.iloc[:, 3:-1].to_numpy() - df_nodes.index.min()
    # if you need to, re-order nodes here-ish
    a = np.hstack((n_nodes.reshape((len(n_nodes), 1)), p))
    # convert to flat numpy array
    cells = a.ravel()
    # remove nans (due to elements with different no. of nodes)
    cells = cells[np.logical_not(np.isnan(cells))]
    cells = cells.astype(int)

    # update grid
    vtk_pts = vtkPoints()
    vtk_pts.SetData(np2da(points))
    vtk_grid.SetPoints(vtk_pts)

    vtk_cells = vtkCellArray()
    vtk_cells.SetCells(cell_types.shape[0], np2da(cells, array_type=vtkConstants.VTK_ID_TYPE))
    vtk_grid.SetCells(np2da(cell_types, array_type=vtkConstants.VTK_UNSIGNED_CHAR), vtk_cells)

    # Add field if any

    df_elem_data = pd.read_csv(
        io.StringIO(field_bytes.decode("utf-8")),
        delim_whitespace=True,
        header=None,
        skiprows=1,
        names=["id", "val"],
    )
    df_elem_data = df_elem_data.sort_values("id").set_index("id", drop=True)
    # fill missing ids in range as VTK uses position (index) to map data to cells
    df_elem_data = df_elem_data.reindex(np.arange(df_elems.index.min(), df_elems.index.max() + 1), fill_value=0.0)
    np_val = df_elem_data["val"].to_numpy()
    # assign data to grid with the name 'my_array'
    vtk_array = np2da(np_val, name="my_array")
    vtk_grid.GetCellData().SetScalars(vtk_array)
    full_min, full_max = vtk_array.GetRange()
    state.full_min = full_min
    state.full_max = full_max
    state.threshold_range = list(vtk_array.GetRange())

    # Color handling in plain VTK
    filter_mapper.SetScalarRange(full_min, full_max)

    renderer.ResetCamera()
    ctrl.view_update()


@state.change("active_eigenmode")
def update_eigenmode(active_eigenmode, **kwargs):
    point_data: vtkPointData = vtk_grid.GetPointData()
    vtk_array: vtkTypeFloat64Array = point_data.GetArray(EIGEN_MODES[active_eigenmode])
    array_name = vtk_array.GetName()

    # Warp Vector
    warp_vector.SetInputArrayToProcess(0, 0, 0, vtkDataObject.FIELD_ASSOCIATION_POINTS, array_name)
    warp_vector.SetScaleFactor(0.0)  # Set the scale factor as needed
    vtk_filter.SetInputConnection(warp_vector.GetOutputPort())

    # Coloring
    magn_name = "Magnitude"
    # Step 1: Extract point data to NumPy array
    point_data_array = vtk_to_numpy(vtk_grid.GetPointData().GetArray(array_name))

    # Step 2: Calculate the magnitude
    magnitude = np.sqrt(np.sum(point_data_array ** 2, axis=1))

    # Step 3: Convert back to VTK array and add to vtkUnstructuredGrid
    magnitude_vtk = np2da(magnitude, name=magn_name)
    vtk_grid.GetPointData().SetScalars(magnitude_vtk)

    # Step 4: Set the new array for coloring
    vtk_filter.SetInputArrayToProcess(0, 0, 0, vtkDataObject.FIELD_ASSOCIATION_POINTS, magn_name)
    scalar_range = vtk_filter.GetOutput().GetScalarRange()
    full_min, full_max = scalar_range

    filter_mapper.SelectColorArray(magn_name)
    filter_mapper.SetScalarRange(full_min, full_max)
    filter_mapper.ScalarVisibilityOn()

    set_scalar_bar_precision(full_max, "u [m]")

    max_num = 10

    global STEPS
    STEPS = {i: full_min + (full_max - full_min) * (i / max_num) for i in range(max_num + 1)}

    state.full_min = 0
    state.full_max = max_num
    state.threshold_range = [0, max_num]

    renderer.ResetCamera()
    update_mesh_representations()


# -----------------------------------------------------------------------------
# Web App setup
# -----------------------------------------------------------------------------

state.trame__title = "FEA - Mesh viewer"
EIGEN_MODES = {}


def load_shell_model():
    """Load a shell model from a vtu file"""
    vtu_file = DATA_DIR / "Cantilever_CA_EIG_sh_modes.vtu"
    reader = vtkXMLUnstructuredGridReader()
    reader.SetFileName(str(vtu_file))
    reader.Update()

    vtu = reader.GetOutput()
    vtk_grid.ShallowCopy(vtu)

    point_data: vtkPointData = vtu.GetPointData()
    global EIGEN_MODES
    EIGEN_MODES = {point_data.GetArray(i).GetName(): i for i in range(point_data.GetNumberOfArrays())}

    keys = list(EIGEN_MODES.keys())
    state.active_eigenmode = keys[0]
    renderer.ResetCamera()
    try:
        update_eigenmode(keys[0])
    except trame_server.controller.FunctionNotImplementedError:
        pass

# load_solid_model()
# -----------------------------------------------------------------------------


load_shell_model()

with SinglePageLayout(server) as layout:
    layout.title.set_text("Mesh Viewer")

    # Toolbar ----------------------------------------
    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VSelect(
            label="EigenModes",
            v_model=("active_eigenmode", 0),
            items=("modes", list(EIGEN_MODES.keys())),
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
        )
        vuetify.VSpacer()
        vuetify.VSlider(
            # Opacity
            v_model=("warp_scale", 1.0),
            min=0,
            max=10,
            step=0.1,
            label="Warp Scale",
            classes="mt-1",
            hide_details=True,
            dense=True,
        )
        vuetify.VSpacer()
        vuetify.VRangeSlider(
            thumb_size=16,
            thumb_label=True,
            label="Threshold",
            v_model=("threshold_range", [-1, 1]),
            min=("full_min", -1),
            max=("full_max", 1),
            dense=True,
            hide_details=True,
            style="max-width: 400px",
        )
        with vuetify.VBtn(icon=True, click=ctrl.view_reset_camera):
            vuetify.VIcon("mdi-crop-free")

    # Content ----------------------------------------
    with layout.content:
        with vuetify.VContainer(
                fluid=True,
                classes="pa-0 fill-height",
                style="position: relative",
        ):
            html_view = vtk.VtkLocalView(renderWindow)
            # html_view = vtk.VtkRemoteView(renderWindow)
            ctrl.view_update = html_view.update
            ctrl.view_reset_camera = html_view.reset_camera



if __name__ == "__main__":
    server.start(port=5000)
