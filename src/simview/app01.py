import pathlib

import os

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vtk, vuetify, trame
from trame_vuetify.ui.vuetify import SinglePageWithDrawerLayout
from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkFiltersCore import vtkContourFilter
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader
from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

# Required for interactor initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa

# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
import vtkmodules.vtkRenderingOpenGL2  # noqa

CURRENT_DIRECTORY = pathlib.Path(__file__).parent.absolute()

# Read Data
reader = vtkXMLUnstructuredGridReader()
reader.SetFileName(CURRENT_DIRECTORY / "../../files/disk_out_ref.vtu")
reader.Update()

# Extract Array/Field information
dataset_arrays = []
fields = [
    (reader.GetOutput().GetPointData(), vtkDataObject.FIELD_ASSOCIATION_POINTS),
    (reader.GetOutput().GetCellData(), vtkDataObject.FIELD_ASSOCIATION_CELLS),
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

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# VTK pipeline
# -----------------------------------------------------------------------------

renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

# Mesh
mesh_mapper = vtkDataSetMapper()
mesh_mapper.SetInputConnection(reader.GetOutputPort())
mesh_actor = vtkActor()
mesh_actor.SetMapper(mesh_mapper)
renderer.AddActor(mesh_actor)

# Mesh: Setup default representation to surface
mesh_actor.GetProperty().SetRepresentationToSurface()
mesh_actor.GetProperty().SetPointSize(1)
mesh_actor.GetProperty().EdgeVisibilityOff()

# Mesh: Apply rainbow color map
mesh_lut = mesh_mapper.GetLookupTable()
mesh_lut.SetHueRange(0.666, 0.0)
mesh_lut.SetSaturationRange(1.0, 1.0)
mesh_lut.SetValueRange(1.0, 1.0)
mesh_lut.Build()

# Mesh: Color by default array
mesh_mapper.SelectColorArray(default_array.get("text"))
mesh_mapper.GetLookupTable().SetRange(default_min, default_max)
if default_array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
    mesh_mapper.SetScalarModeToUsePointFieldData()
else:
    mesh_mapper.SetScalarModeToUseCellFieldData()
mesh_mapper.SetScalarVisibility(True)
mesh_mapper.SetUseLookupTableScalarRange(True)

# Contour
contour = vtkContourFilter()
contour.SetInputConnection(reader.GetOutputPort())
contour_mapper = vtkDataSetMapper()
contour_mapper.SetInputConnection(contour.GetOutputPort())
contour_actor = vtkActor()
contour_actor.SetMapper(contour_mapper)
renderer.AddActor(contour_actor)

# Contour: ContourBy default array
contour_value = 0.5 * (default_max + default_min)
contour.SetInputArrayToProcess(
    0, 0, 0, default_array.get("type"), default_array.get("text")
)
contour.SetValue(0, contour_value)

# Contour: Setup default representation to surface
contour_actor.GetProperty().SetRepresentationToSurface()
contour_actor.GetProperty().SetPointSize(1)
contour_actor.GetProperty().EdgeVisibilityOff()

# Contour: Apply rainbow color map
contour_lut = contour_mapper.GetLookupTable()
contour_lut.SetHueRange(0.666, 0.0)
contour_lut.SetSaturationRange(1.0, 1.0)
contour_lut.SetValueRange(1.0, 1.0)
contour_lut.Build()

# Contour: Color by default array
contour_mapper.SelectColorArray(default_array.get("text"))
contour_mapper.GetLookupTable().SetRange(default_min, default_max)
if default_array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
    contour_mapper.SetScalarModeToUsePointFieldData()
else:
    contour_mapper.SetScalarModeToUseCellFieldData()
contour_mapper.SetScalarVisibility(True)
contour_mapper.SetUseLookupTableScalarRange(True)

# Cube Axes
cube_axes = vtkCubeAxesActor()
renderer.AddActor(cube_axes)

# Cube Axes: Boundaries, camera, and styling
cube_axes.SetBounds(mesh_actor.GetBounds())
cube_axes.SetCamera(renderer.GetActiveCamera())
cube_axes.SetXLabelFormat("%6.1f")
cube_axes.SetYLabelFormat("%6.1f")
cube_axes.SetZLabelFormat("%6.1f")
cube_axes.SetFlyModeToOuterEdges()

# Read Data

# Extract Array/Field information

# Mesh
# Mesh: Setup default representation to surface
# Mesh: Apply rainbow color map
# Mesh: Color by default array

# Contour
# Contour: ContourBy default array
# Contour: Setup default representation to surface
# Contour: Apply rainbow color map
# Contour: Color by default array

# Cube Axes
# Cube Axes: Boundaries, camera, and styling

renderer.ResetCamera()

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()
server.client_type = "vue2"
state, ctrl = server.state, server.controller

# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# GUI elements
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------
with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text("Viewer")

    with layout.toolbar:
        # toolbar components
        pass

    with layout.drawer as drawer:
        # drawer components
        pass

    with layout.content:
        # content components
        with vuetify.VContainer(
                fluid=True,
                classes="pa-0 fill-height",
        ):
            view = vtk.VtkRemoteLocalView(renderWindow, namespace="view", mode="local", interactive_ratio=1)
            ctrl.view_update = view.update  # capture view update method
            ctrl.view_reset_camera = view.reset_camera  # capture view reset_camera method


def standard_buttons():
    vuetify.VCheckbox(
        v_model=("cube_axes_visibility", True),
        on_icon="mdi-cube-outline",
        off_icon="mdi-cube-off-outline",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
    vuetify.VCheckbox(
        v_model="$vuetify.theme.dark",
        on_icon="mdi-lightbulb-off-outline",
        off_icon="mdi-lightbulb-outline",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
    vuetify.VCheckbox(
        v_model=("viewMode", "local"),  # VtkRemoteLocalView => {namespace}Mode=['local', 'remote']
        on_icon="mdi-lan-disconnect",
        off_icon="mdi-lan-connect",
        true_value="local",
        false_value="remote",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
    with vuetify.VBtn(icon=True, click=ctrl.view_reset_camera):
        vuetify.VIcon("mdi-crop-free")


with layout.toolbar:
    # toolbar components
    vuetify.VSpacer()
    vuetify.VDivider(vertical=True, classes="mx-2")
    standard_buttons()

# State use to track active UI card
state.setdefault("active_ui", None)  # prevent resetting value if already present


def ui_card(title, ui_name):
    with vuetify.VCard(v_show=f"active_ui == '{ui_name}'"):
        vuetify.VCardTitle(
            title,
            classes="grey lighten-1 py-1 grey--text text--darken-3",
            style="user-select: none; cursor: pointer",
            hide_details=True,
            dense=True,
        )
        content = vuetify.VCardText(classes="py-2")
    return content


def contour_card():
    with ui_card(title="Contour", ui_name="contour"):
        vuetify.VSelect(
            # Contour By
        )
        vuetify.VSlider(
            # Contour Value
        )


def mesh_card():
    with ui_card(title="Mesh", ui_name="mesh"):
        vuetify.VSelect(
            # Representation
        )
        with vuetify.VRow(classes="pt-2", dense=True):
            with vuetify.VCol(cols="6"):
                vuetify.VSelect(
                    # Color By
                )
            with vuetify.VCol(cols="6"):
                vuetify.VSelect(
                    # Color Map
                )
        vuetify.VSlider(
            # Opacity
        )


def pipeline_widget():
    widgets.GitTree(
        sources=(
            "pipeline",
            [
                {"id": "1", "parent": "0", "visible": 1, "name": "Mesh"},
                {"id": "2", "parent": "1", "visible": 1, "name": "Contour"},
            ],
        ),
        actives_change=(actives_change, "[$event]"),
        visibility_change=(visibility_change, "[$event]"),
    )


with layout.drawer as drawer:
    # drawer components
    drawer.width = 325
    pipeline_widget()
    vuetify.VDivider(classes="mb-2")
    mesh_card()
    contour_card()
class Representation:
    Points = 0
    Wireframe = 1
    Surface = 2
    SurfaceWithEdges = 3
# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
