from __future__ import annotations

from typing import TYPE_CHECKING

from trame.widgets import vuetify
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkFiltersCore import vtkContourFilter
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import vtkDataSetMapper, vtkActor, vtkRenderer, vtkRenderWindow, \
    vtkRenderWindowInteractor

if TYPE_CHECKING:
    from simview.apptrame.app00.views.file_reader import ModelDataStore


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





def apply_countour(model_data: ModelDataStore, renderer):
    fields = model_data.current_mesh.fields
    default_min, default_max = fields.default_min, fields.default_max
    default_array = fields.default_array

    # Contour
    contour = vtkContourFilter()
    contour.SetInputData(model_data.vtk_grid)
    contour_mapper = vtkDataSetMapper()
    contour_mapper.SetInputConnection(contour.GetOutputPort())
    contour_actor = vtkActor()
    contour_actor.SetMapper(contour_mapper)
    renderer.AddActor(contour_actor)
    model_data.contour_actor = contour_actor

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


def create_render_window(model_data: ModelDataStore):
    mapper = vtkDataSetMapper()
    mapper.SetInputData(model_data.vtk_grid)
    # mapper.SetScalarVisibility(True)
    # mapper.ScalarVisibilityOn()
    # mapper.SetScalarModeToUseCellData()

    # # Actors
    actor = vtkActor()
    actor.SetMapper(mapper)

    # # Mesh: Setup default representation to surface
    actor.GetProperty().SetRepresentationToSurface()
    actor.GetProperty().SetPointSize(1)
    actor.GetProperty().EdgeVisibilityOn()

    # Render stuff
    colors = vtkNamedColors()
    renderer = vtkRenderer()
    renderer.SetBackground(colors.GetColor3d("SlateGray"))  # SlateGray
    renderer.AddActor(actor)

    # Mesh: Apply rainbow color map
    mesh_lut = mapper.GetLookupTable()
    mesh_lut.SetHueRange(0.666, 0.0)
    mesh_lut.SetSaturationRange(1.0, 1.0)
    mesh_lut.SetValueRange(1.0, 1.0)
    mesh_lut.Build()

    fields = model_data.current_mesh.fields
    mapper.SelectColorArray(fields.default_array.get("text"))
    mapper.GetLookupTable().SetRange(fields.default_min, fields.default_max)
    if fields.default_array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
        mapper.SetScalarModeToUsePointFieldData()
    else:
        mapper.SetScalarModeToUseCellFieldData()
    mapper.SetScalarVisibility(True)
    mapper.SetUseLookupTableScalarRange(True)

    apply_countour(model_data, renderer)

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


def contour_card(model_data: ModelDataStore):
    dataset_arrays = model_data.current_mesh.fields.datasets
    default_min, default_max = model_data.current_mesh.fields.default_min, model_data.current_mesh.fields.default_max
    contour_value = 0.5 * (default_max + default_min)

    with ui_card(title="Contour", ui_name="contour"):
        vuetify.VSelect(
            # Contour By
            label="Contour by",
            v_model=("contour_by_array_idx", 0),
            items=("array_list", dataset_arrays),
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
        )
        vuetify.VSlider(
            # Contour Value
            v_model=("contour_value", contour_value),
            min=("contour_min", default_min),
            max=("contour_max", default_max),
            step=("contour_step", 0.01 * (default_max - default_min)),
            label="Value",
            classes="my-1",
            hide_details=True,
            dense=True,
        )
        vuetify.VSelect(
            # Representation
            v_model=("contour_representation", Representation.Surface),
            items=(
                "representations",
                [
                    {"text": "Points", "value": 0},
                    {"text": "Wireframe", "value": 1},
                    {"text": "Surface", "value": 2},
                    {"text": "SurfaceWithEdges", "value": 3},
                ],
            ),
            label="Representation",
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
        )
        with vuetify.VRow(classes="pt-2", dense=True):
            with vuetify.VCol(cols="6"):
                vuetify.VSelect(
                    # Color By
                    label="Color by",
                    v_model=("contour_color_array_idx", 0),
                    items=("array_list", dataset_arrays),
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="pt-1",
                )
            with vuetify.VCol(cols="6"):
                vuetify.VSelect(
                    # Color Map
                    label="Colormap",
                    v_model=("contour_color_preset", LookupTable.Rainbow),
                    items=(
                        "colormaps",
                        [
                            {"text": "Rainbow", "value": 0},
                            {"text": "Inv Rainbow", "value": 1},
                            {"text": "Greyscale", "value": 2},
                            {"text": "Inv Greyscale", "value": 3},
                        ],
                    ),
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="pt-1",
                )
        vuetify.VSlider(
            # Opacity
            v_model=("contour_opacity", 1.0),
            min=0,
            max=1,
            step=0.1,
            label="Opacity",
            classes="mt-1",
            hide_details=True,
            dense=True,
        )


def ui_card(title, ui_name):
    with vuetify.VCard(to="/", v_show=f"default == '{ui_name}'"):
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


def representation_drawer():
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
