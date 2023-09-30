from dataclasses import dataclass

from vtkmodules.vtkCommonDataModel import vtkDataObject

from simview.apptrame.data import LookupTable, Representation, VtkData
from trame.app import get_server

server = get_server()
state, ctrl = server.state, server.controller


# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------
@dataclass
class ViewCalls:
    vtk_data: VtkData = None

    @state.change("cube_axes_visibility")
    def update_cube_axes_visibility(self, cube_axes_visibility, **kwargs):
        self.vtk_data.cube_axes.SetVisibility(cube_axes_visibility)
        ctrl.view_update()

    # Selection Change
    def actives_change(self, ids):
        _id = ids[0]
        if _id == "1":  # Mesh
            state.active_ui = "mesh"
        elif _id == "2":  # Contour
            state.active_ui = "contour"
        else:
            state.active_ui = "nothing"

    # Visibility Change
    def visibility_change(self, event):
        _id = event["id"]
        _visibility = event["visible"]

        if _id == "1":  # Mesh
            self.vtk_data.mesh_actor.SetVisibility(_visibility)
        elif _id == "2":  # Contour
            self.vtk_data.contour_actor.SetVisibility(_visibility)
        ctrl.view_update()

    # Representation Callbacks
    def update_representation(self, actor, mode):
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
    def update_mesh_representation(self, mesh_representation, **kwargs):
        self.update_representation(self.vtk_data.mesh_actor, mesh_representation)
        ctrl.view_update()

    @state.change("contour_representation")
    def update_contour_representation(self, contour_representation, **kwargs):
        self.update_representation(self.vtk_data.contour_actor, contour_representation)
        ctrl.view_update()

    # Color By Callbacks
    def color_by_array(self, actor, array):
        _min, _max = array.get("range")
        mapper = actor.GetMapper()
        mapper.SelectColorArray(array.get("text"))
        mapper.GetLookupTable().SetRange(_min, _max)
        if array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
            self.vtk_data.mesh_mapper.SetScalarModeToUsePointFieldData()
        else:
            self.vtk_data.mesh_mapper.SetScalarModeToUseCellFieldData()
        mapper.SetScalarVisibility(True)
        mapper.SetUseLookupTableScalarRange(True)

    @state.change("mesh_color_array_idx")
    def update_mesh_color_by_name(self, mesh_color_array_idx, **kwargs):
        array = self.vtk_data.dataset_arrays[mesh_color_array_idx]
        self.color_by_array(self.vtk_data.mesh_actor, array)
        ctrl.view_update()

    @state.change("contour_color_array_idx")
    def update_contour_color_by_name(self, contour_color_array_idx, **kwargs):
        array = self.vtk_data.dataset_arrays[contour_color_array_idx]
        self.color_by_array(self.vtk_data.contour_actor, array)
        ctrl.view_update()

    # Color Map Callbacks
    def use_preset(self, actor, preset):
        lut = actor.GetMapper().GetLookupTable()
        if preset == LookupTable.Rainbow:
            lut.SetHueRange(0.666, 0.0)
            lut.SetSaturationRange(1.0, 1.0)
            lut.SetValueRange(1.0, 1.0)
        elif preset == LookupTable.Inverted_Rainbow:
            lut.SetHueRange(0.0, 0.666)
            lut.SetSaturationRange(1.0, 1.0)
            lut.SetValueRange(1.0, 1.0)
        elif preset == LookupTable.Greyscale:
            lut.SetHueRange(0.0, 0.0)
            lut.SetSaturationRange(0.0, 0.0)
            lut.SetValueRange(0.0, 1.0)
        elif preset == LookupTable.Inverted_Greyscale:
            lut.SetHueRange(0.0, 0.666)
            lut.SetSaturationRange(0.0, 0.0)
            lut.SetValueRange(1.0, 0.0)
        lut.Build()

    @state.change("mesh_color_preset")
    def update_mesh_color_preset(self, mesh_color_preset, **kwargs):
        self.use_preset(self.vtk_data.mesh_actor, mesh_color_preset)
        ctrl.view_update()

    @state.change("contour_color_preset")
    def update_contour_color_preset(self, contour_color_preset, **kwargs):
        self.use_preset(self.vtk_data.contour_actor, contour_color_preset)
        ctrl.view_update()

    # Opacity Callbacks
    @state.change("mesh_opacity")
    def update_mesh_opacity(self, mesh_opacity, **kwargs):
        self.vtk_data.mesh_actor.GetProperty().SetOpacity(mesh_opacity)
        ctrl.view_update()

    @state.change("contour_opacity")
    def update_contour_opacity(self, contour_opacity, **kwargs):
        self.vtk_data.contour_actor.GetProperty().SetOpacity(contour_opacity)
        ctrl.view_update()

    # Contour Callbacks
    @state.change("contour_by_array_idx")
    def update_contour_by(self, contour_by_array_idx, **kwargs):
        array = self.vtk_data.dataset_arrays[contour_by_array_idx]
        contour_min, contour_max = array.get("range")
        contour_step = 0.01 * (contour_max - contour_min)
        contour_value = 0.5 * (contour_max + contour_min)
        self.vtk_data.contour.SetInputArrayToProcess(0, 0, 0, array.get("type"), array.get("text"))
        self.vtk_data.contour.SetValue(0, contour_value)

        # Update UI
        state.contour_min = contour_min
        state.contour_max = contour_max
        state.contour_value = contour_value
        state.contour_step = contour_step

        # Update View
        ctrl.view_update()

    @state.change("contour_value")
    def update_contour_value(self, contour_value, **kwargs):
        self.vtk_data.contour.SetValue(0, float(contour_value))
        ctrl.view_update()
