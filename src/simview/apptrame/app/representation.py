from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np
from vtkmodules.numpy_interface.dataset_adapter import numpyTovtkDataArray as np2da
from vtkmodules.util.numpy_support import vtk_to_numpy
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkFiltersCore import vtkThreshold
from vtkmodules.vtkFiltersGeneral import vtkWarpVector
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkRenderingCore import vtkDataSetMapper, vtkRenderer

if TYPE_CHECKING:
    from simview.apptrame.app.model_store import ModelDataStore


@dataclass
class Fields:
    datasets: list
    default_array: dict
    default_min: float
    default_max: float
    vtk_filter: vtkThreshold = field(default_factory=vtkThreshold)
    warp_vector: vtkWarpVector = field(default_factory=vtkWarpVector)


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


def update_magnitude_array(magn_name, vtk_grid, array_name):
    # Step 1: Extract point data to NumPy array
    point_data_array = vtk_to_numpy(vtk_grid.GetPointData().GetArray(array_name))

    # Step 2: Calculate the magnitude
    magnitude = np.sqrt(np.sum(point_data_array**2, axis=1))

    # Step 3: Convert back to VTK array and add to vtkUnstructuredGrid
    magnitude_vtk = np2da(magnitude, name=magn_name)
    vtk_grid.GetPointData().SetScalars(magnitude_vtk)


def init_filter_pipeline(model_store: ModelDataStore, renderer: vtkRenderer):
    vtk_grid = model_store.vtk_grid
    filter_actor = model_store.filter_actor
    mesh_actor = model_store.mesh_actor
    fields = model_store.fields
    vtk_filter = fields.vtk_filter

    # Create Filter
    vtk_filter.SetInputData(vtk_grid)

    # Warp Vector
    warp_vector = fields.warp_vector
    warp_vector.SetInputData(vtk_grid)

    vtk_filter.SetInputConnection(warp_vector.GetOutputPort())

    filter_mapper = vtkDataSetMapper()
    filter_mapper.SetInputConnection(vtk_filter.GetOutputPort())
    filter_mapper.ScalarVisibilityOn()
    filter_actor.SetMapper(filter_mapper)
    renderer.AddActor(filter_actor)

    lut = vtkLookupTable()
    lut.SetHueRange(0.667, 0)
    filter_mapper.SetLookupTable(lut)

    mesh_mapper = vtkDataSetMapper()
    mesh_mapper.SetInputData(model_store.vtk_grid)
    mesh_mapper.SetScalarVisibility(0)
    mesh_actor.SetMapper(mesh_mapper)
    renderer.AddActor(mesh_actor)

    scalar_bar = create_scalar_bar_actor(filter_mapper)
    renderer.AddActor2D(scalar_bar)


def set_current_filter_array(model_store: ModelDataStore, array_name, num_range_steps=50):
    filter_mapper = model_store.filter_actor.GetMapper()
    lut = filter_mapper.GetLookupTable()
    scalar_bar = model_store.renderer.GetActors2D().GetLastActor2D()
    fields = model_store.fields
    vtk_filter = fields.vtk_filter
    warp_vector = fields.warp_vector

    # Set Warp Vector
    warp_vector.SetInputArrayToProcess(0, 0, 0, vtkDataObject.FIELD_ASSOCIATION_POINTS, array_name)

    # Set Magnitude Scalar Array
    magn_name = f"{array_name}_magn"
    update_magnitude_array(magn_name, model_store.vtk_grid, array_name)
    vtk_filter.SetInputArrayToProcess(0, 0, 0, vtkDataObject.FIELD_ASSOCIATION_POINTS, magn_name)
    scalar_range = vtk_filter.GetOutput().GetScalarRange()
    full_min, full_max = scalar_range

    model_store.server.state.scalar_range = scalar_range
    model_store.server.state.full_min = full_min
    model_store.server.state.full_max = full_max
    model_store.server.state.range_step = (full_max - full_min) / num_range_steps

    filter_mapper.SelectColorArray(magn_name)
    filter_mapper.SetScalarRange(full_min, full_max)

    lut.SetRange(scalar_range)
    lut.Build()

    update_scalar_bar("u [m]", scalar_bar, full_max)





def create_scalar_bar_actor(mapper):
    scalar_bar = vtkScalarBarActor()
    scalar_bar.SetLookupTable(mapper.GetLookupTable())
    scalar_bar.SetNumberOfLabels(7)
    scalar_bar.UnconstrainedFontSizeOn()
    scalar_bar.SetMaximumWidthInPixels(100)
    scalar_bar.SetMaximumHeightInPixels(800 // 3)

    return scalar_bar


def update_scalar_bar(title, scalar_bar, max_scalar):
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
