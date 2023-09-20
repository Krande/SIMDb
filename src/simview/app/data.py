import pathlib
from dataclasses import dataclass

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

CURRENT_DIRECTORY = pathlib.Path(__file__).parent.absolute()


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


@dataclass
class VtkData:
    dataset_arrays: list[dict] = None
    default_array: list[dict] = None
    reader: vtkXMLUnstructuredGridReader = None
    renderer: vtkRenderer = None
    renderWindow: vtkRenderWindow = None
    default_min: float = None
    default_max: float = None
    contour_value: float = None
    cube_axes: vtkCubeAxesActor = None
    contour: vtkContourFilter = None
    contour_actor: vtkActor = None
    mesh_actor: vtkActor = None
    mesh_mapper: vtkDataSetMapper = None

    def initialize(self):
        renderer = vtkRenderer()
        render_window = vtkRenderWindow()
        render_window.AddRenderer(renderer)
        self.renderer = renderer
        self.renderWindow = render_window

        render_window_interactor = vtkRenderWindowInteractor()
        render_window_interactor.SetRenderWindow(render_window)
        render_window_interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        self.read_data()
        self.contour_mapper()

    def read_data(self):
        reader = vtkXMLUnstructuredGridReader()
        # @server.state.change()
        reader.SetFileName(CURRENT_DIRECTORY / "files/disk_out_ref.vtu")
        reader.Update()
        self.reader = reader

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
        self.dataset_arrays = dataset_arrays
        self.default_array = dataset_arrays[0]
        self.default_min, self.default_max = self.default_array.get("range")

    def contour_mapper(self):
        # Mesh
        mesh_mapper = vtkDataSetMapper()
        mesh_mapper.SetInputConnection(self.reader.GetOutputPort())
        self.mesh_mapper = mesh_mapper
        mesh_actor = vtkActor()
        mesh_actor.SetMapper(mesh_mapper)
        self.mesh_actor = mesh_actor
        self.renderer.AddActor(mesh_actor)

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
        mesh_mapper.SelectColorArray(self.default_array.get("text"))
        mesh_mapper.GetLookupTable().SetRange(self.default_min, self.default_max)
        if self.default_array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
            mesh_mapper.SetScalarModeToUsePointFieldData()
        else:
            mesh_mapper.SetScalarModeToUseCellFieldData()
        mesh_mapper.SetScalarVisibility(True)
        mesh_mapper.SetUseLookupTableScalarRange(True)

        # Contour
        contour = vtkContourFilter()
        contour.SetInputConnection(self.reader.GetOutputPort())
        contour_mapper = vtkDataSetMapper()
        contour_mapper.SetInputConnection(contour.GetOutputPort())
        contour_actor = vtkActor()
        contour_actor.SetMapper(contour_mapper)
        self.renderer.AddActor(contour_actor)

        # Contour: ContourBy default array
        contour_value = 0.5 * (self.default_max + self.default_min)
        self.contour_value = contour_value
        contour.SetInputArrayToProcess(
            0, 0, 0, self.default_array.get("type"), self.default_array.get("text")
        )
        contour.SetValue(0, contour_value)
        self.contour = contour

        # Contour: Setup default representation to surface
        contour_actor.GetProperty().SetRepresentationToSurface()
        contour_actor.GetProperty().SetPointSize(1)
        contour_actor.GetProperty().EdgeVisibilityOff()
        self.contour_actor = contour_actor
        # Contour: Apply rainbow color map
        contour_lut = contour_mapper.GetLookupTable()
        contour_lut.SetHueRange(0.666, 0.0)
        contour_lut.SetSaturationRange(1.0, 1.0)
        contour_lut.SetValueRange(1.0, 1.0)
        contour_lut.Build()

        # Contour: Color by default array
        contour_mapper.SelectColorArray(self.default_array.get("text"))
        contour_mapper.GetLookupTable().SetRange(self.default_min, self.default_max)
        if self.default_array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
            contour_mapper.SetScalarModeToUsePointFieldData()
        else:
            contour_mapper.SetScalarModeToUseCellFieldData()
        contour_mapper.SetScalarVisibility(True)
        contour_mapper.SetUseLookupTableScalarRange(True)

        # Cube Axes
        cube_axes = vtkCubeAxesActor()
        self.renderer.AddActor(cube_axes)

        # Cube Axes: Boundaries, camera, and styling
        cube_axes.SetBounds(mesh_actor.GetBounds())
        cube_axes.SetCamera(self.renderer.GetActiveCamera())
        cube_axes.SetXLabelFormat("%6.1f")
        cube_axes.SetYLabelFormat("%6.1f")
        cube_axes.SetZLabelFormat("%6.1f")
        cube_axes.SetFlyModeToOuterEdges()
        self.cube_axes = cube_axes
        self.renderer.ResetCamera()
