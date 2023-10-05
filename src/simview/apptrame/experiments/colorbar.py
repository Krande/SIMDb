"""Basic example demonstrating an issue with colorbars."""

from trame.app import get_server

from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.ui.router import RouterViewLayout
from trame.widgets import vtk, vuetify, trame, html, router

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkColorTransferFunction,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader
from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera


# Required for interactor initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa

# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
import vtkmodules.vtkRenderingOpenGL2  # noqa

import pathlib

from simview.helpers import DATA_DIR


# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------


class Representation:
    Points = 0
    Wireframe = 1
    Surface = 2
    SurfaceWithEdges = 3


class LookupTable:
    Rainbow = 0
    Inverted_Rainbow = 1
    Greyscale = 2
    Inverted_Greyscale = 3


# -----------------------------------------------------------------------------
# VTK pipeline
# -----------------------------------------------------------------------------

# Source/Reader

source_path = DATA_DIR / "patch_antenna.vtu"
if not source_path.exists():
    raise FileNotFoundError(source_path.as_posix())


vtk_source = vtkXMLUnstructuredGridReader()
vtk_source.SetFileName(source_path.as_posix())
vtk_source.Update()
show_array = "ElectricField"


# Misc stuff
colors = vtkNamedColors()

# Lookup table & color transfer function
num_colors = 256

ctf = vtkColorTransferFunction()
ctf.SetColorSpaceToDiverging()
ctf.AddRGBPoint(0.0, 0.230, 0.299, 0.754)
ctf.AddRGBPoint(1.0, 0.706, 0.016, 0.150)

lut = vtkLookupTable()
lut.SetNumberOfTableValues(num_colors)
lut.Build()

for i in range(0, num_colors):
    rgb = list(ctf.GetColor(float(i) / num_colors))
    rgb.append(1.0)
    lut.SetTableValue(i, *rgb)

scalar_range = vtk_source.GetOutput().GetScalarRange()

mapper = vtkDataSetMapper()
mapper.SetInputConnection(vtk_source.GetOutputPort())
mapper.ScalarVisibilityOn()
mapper.SetScalarRange(scalar_range)
mapper.SetLookupTable(lut)

# Actors
actor = vtkActor()
actor.SetMapper(mapper)
# Mesh: Setup default representation to surface
actor.GetProperty().SetRepresentationToSurface()
actor.GetProperty().SetPointSize(1)
actor.GetProperty().EdgeVisibilityOn()

scalar_bar = vtkScalarBarActor()
scalar_bar.SetLookupTable(mapper.GetLookupTable())
scalar_bar.SetNumberOfLabels(7)
scalar_bar.UnconstrainedFontSizeOn()
scalar_bar.SetMaximumWidthInPixels(100)
scalar_bar.SetMaximumHeightInPixels(800 // 3)
scalar_bar.SetTitle(show_array)


max_scalar = scalar_range[1]
if max_scalar < 1:
    precision = 4
elif max_scalar < 10:
    precision = 3
elif max_scalar < 100:
    precision = 2
else:
    precision = 1
scalar_bar.SetLabelFormat(f"%-#6.{precision}f")

# Render stuff
renderer = vtkRenderer()
renderer.SetBackground(colors.GetColor3d("SlateGray"))  # SlateGray
renderer.AddActor(actor)
renderer.AddActor2D(scalar_bar)

render_window = vtkRenderWindow()
render_window.SetSize(300, 300)
render_window.AddRenderer(renderer)
render_window.SetWindowName("VTK Test")

render_window_interactor = vtkRenderWindowInteractor()
interactor_style = vtkInteractorStyleTrackballCamera()
render_window_interactor.SetInteractorStyle(interactor_style)
render_window_interactor.SetRenderWindow(render_window)
renderer.ResetCamera()

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller

state.setdefault("active_ui", "geometry")
state.vtk_bground = "SlateGray"

# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------

# Representation Callbacks
def update_representation(actor, mode):
    property = actor.GetProperty()
    if mode == Representation.Points:
        property.SetRepresentationToPoints()
        property.SetPointSize(5)
        property.EdgeVisibilityOff()
    elif mode == Representation.Wireframe:
        property.SetRepresentationToWireframe()
        property.SetPointSize(1)
        property.EdgeVisibilityOff()
    elif mode == Representation.Surface:
        property.SetRepresentationToSurface()
        property.SetPointSize(1)
        property.EdgeVisibilityOff()
    elif mode == Representation.SurfaceWithEdges:
        property.SetRepresentationToSurface()
        property.SetPointSize(1)
        property.EdgeVisibilityOn()


@state.change("mesh_representation")
def update_mesh_representation(mesh_representation, **kwargs):
    update_representation(actor, mesh_representation)
    ctrl.view_update()


# Opacity Callbacks
@state.change("mesh_opacity")
def update_mesh_opacity(mesh_opacity, **kwargs):
    actor.GetProperty().SetOpacity(mesh_opacity)
    ctrl.view_update()


def toggle_background():
    bgcolor = "SlateGray"
    if state.vtk_bground == "SlateGray":
        bgcolor = "black"

    state.vtk_bground = bgcolor
    renderer.SetBackground(colors.GetColor3d(bgcolor))

    ctrl.view_update()


# -----------------------------------------------------------------------------
# GUI ELEMENTS
# -----------------------------------------------------------------------------


def ui_card(title, ui_name):
    with vuetify.VCard(to="/", v_show=f"active_ui == '{ui_name}'"):
        vuetify.VCardTitle(
            title,
            classes="grey lighten-1 py-1 grey--text text--darken-3",
            style="user-select: none; cursor: pointer",
            hide_details=True,
            dense=True,
        )
        content = vuetify.VCardText(classes="py-2")
    return content


def mesh_card():
    with ui_card(title="Geometry", ui_name="geometry"):

        with vuetify.VRow(classes="pt-2", dense=True):
            vuetify.VSelect(
                # Representation
                v_model=("mesh_representation", Representation.Surface),
                items=(
                    "representations",
                    [
                        {"text": "Points", "value": 0},
                        {"text": "Wireframe", "value": 1},
                        {"text": "Surface", "value": 2},
                        {"text": "Surface With Edges", "value": 3},
                    ],
                ),
                label="Representation",
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-1",
            )

        vuetify.VSlider(
            # Opacity
            v_model=("mesh_opacity", 1.0),
            min=0,
            max=1,
            step=0.1,
            label="Opacity",
            classes="mt-1",
            hide_details=True,
            dense=True,
        )


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

with RouterViewLayout(server, "/"):
    with html.Div(style="height: 100%; width: 100%;"):
        view = vtk.VtkLocalView(render_window)
        ctrl.view_update.add(view.update)
        ctrl.on_server_ready.add(view.update)

with RouterViewLayout(server, "/foo"):
    with vuetify.VCard():
        vuetify.VCardTitle("This is foo")
        with vuetify.VCardText():
            vuetify.VBtn("Take me back", click="$router.back()")


with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text("Colorbar issue example")

    with layout.toolbar as toolbar:
        toolbar.dense = True
        vuetify.VSpacer()
        vuetify.VDivider(vertical=True, classes="mx-2")
        vuetify.VSwitch(
            v_model=("$vuetify.theme.dark"),
            inset=True,
            hide_details=True,
            dense=True,
            change=toggle_background,
        )

    with layout.drawer as drawer:
        drawer.width = 325
        with vuetify.VList(shaped=True, v_model=("selectedRoute", 0)):
            with vuetify.VListGroup(value=("true",), sub_group=True):
                with vuetify.Template(v_slot_activator=True):
                    vuetify.VListItemTitle("3D View")
                mesh_card()

    with layout.content:
        with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
            router.RouterView(style="width: 100%; height: 100%")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start(port=5000)
