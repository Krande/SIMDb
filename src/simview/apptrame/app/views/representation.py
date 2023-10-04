from __future__ import annotations

from typing import TYPE_CHECKING
import pyvista as pv
from trame.widgets import vuetify
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkRenderingCore import vtkDataSetMapper, vtkActor, vtkRenderer, vtkRenderWindow, \
    vtkRenderWindowInteractor, vtkColorTransferFunction

if TYPE_CHECKING:
    from simview.apptrame.app.views.file_reader import ModelDataStore


class Representation:
    Points = 0
    Wireframe = 1
    Surface = 2
    SurfaceWithEdges = 3


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


def color_by_array(mapper, lut, array):
    _min, _max = array.get("range")
    mapper.SelectColorArray(array.get("text"))
    lut.SetRange(_min, _max)
    if array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
        mapper.SetScalarModeToUsePointFieldData()
    else:
        mapper.SetScalarModeToUseCellFieldData()

    mapper.ScalarVisibilityOn()
    mapper.UseLookupTableScalarRangeOn()


def create_render_window(model_data: ModelDataStore):
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

    fields = model_data.current_mesh.fields
    scalar_range = fields.default_min, fields.default_max
    default_array = fields.default_array

    mapper = vtkDataSetMapper()
    mapper.SetInputData(model_data.vtk_grid)
    mapper.ScalarVisibilityOn()
    mapper.SetScalarRange(scalar_range)
    mapper.SetLookupTable(lut)

    if default_array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
        model_data.vtk_grid.GetPointData().SetActiveScalars(default_array.get("text"))
        mapper.SetScalarModeToUsePointData()
    else:
        model_data.vtk_grid.GetCellData().SetActiveScalars(default_array.get("text"))
        mapper.SetScalarModeToUseCellData()

    mapper.SelectColorArray(default_array.get("text"))

    # # Actors
    actor = vtkActor()
    actor.SetMapper(mapper)
    # Mesh: Setup default representation to surface
    actor.GetProperty().SetRepresentationToSurface()
    actor.GetProperty().SetPointSize(1)
    actor.GetProperty().EdgeVisibilityOn()

    scalar_bar = create_scalar_bar_actor(mapper, scalar_range, "u [m]")

    # color_by_array(mapper, lut, fields.default_array)

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

    return actor, render_window


def create_scalar_bar_actor(mapper, scalar_range, title):
    scalar_bar = vtkScalarBarActor()
    scalar_bar.SetLookupTable(mapper.GetLookupTable())
    scalar_bar.SetNumberOfLabels(7)
    scalar_bar.UnconstrainedFontSizeOn()
    scalar_bar.SetMaximumWidthInPixels(100)
    scalar_bar.SetMaximumHeightInPixels(800 // 3)
    scalar_bar.SetTitle(title)

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

    return scalar_bar


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


def representation_drawer():
    with ui_card(title="Geometry", ui_name="geometry"):
        with vuetify.VRow(classes="pt-2", dense=True):
            vuetify.VSelect(
                # Representation
                v_model=("mesh_representation", Representation.SurfaceWithEdges),
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
