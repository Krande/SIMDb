from __future__ import annotations

from typing import TYPE_CHECKING

from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkRenderingCore import vtkDataSetMapper, vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor

if TYPE_CHECKING:
    from simview.apptrame.app.model_store import ModelDataStore


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


def create_render_window(model_store: ModelDataStore):
    filter_actor = model_store.filter_actor

    mesh_actor = model_store.mesh_actor

    renderer = vtkRenderer()
    renderer.SetBackground(vtkNamedColors().GetColor3d("SlateGray"))  # SlateGray

    render_window = vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetWindowName("VTK Test")

    render_window_interactor = vtkRenderWindowInteractor()
    interactor_style = vtkInteractorStyleTrackballCamera()
    render_window_interactor.SetInteractorStyle(interactor_style)
    render_window_interactor.SetRenderWindow(render_window)

    fields = model_store.fields
    scalar_range = fields.default_min, fields.default_max

    vtk_filter = fields.vtk_filter
    vtk_filter.SetInputData(model_store.vtk_grid)

    filter_mapper = vtkDataSetMapper()
    filter_mapper.SetInputConnection(vtk_filter.GetOutputPort())
    vtk_filter.SetInputArrayToProcess(0, 0, 0, vtkDataObject.FIELD_ASSOCIATION_POINTS, fields.default_array.get('text'))
    # filter_mapper.SetScalarRange(fields.default_min, fields.default_max)

    filter_actor.SetMapper(filter_mapper)
    renderer.AddActor(filter_actor)

    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    lut.SetRange(scalar_range)
    lut.Build()

    filter_mapper.SetLookupTable(lut)

    mesh_mapper = vtkDataSetMapper()
    mesh_mapper.SetInputData(model_store.vtk_grid)
    mesh_mapper.SetScalarVisibility(0)

    mesh_actor.SetMapper(mesh_mapper)
    renderer.AddActor(mesh_actor)

    scalar_bar = create_scalar_bar_actor(filter_mapper, scalar_range, "u [m]")
    renderer.AddActor2D(scalar_bar)

    renderer.ResetCamera()
    return render_window


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
