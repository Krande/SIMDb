from trame.widgets import vuetify
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkDataArray
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import vtkDataSetMapper, vtkActor, vtkRenderer, vtkRenderWindow, \
    vtkRenderWindowInteractor


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


def create_render_window(vtk_grid):
    vtk_array = vtk_grid.GetCellData().GetScalars()
    vtk_array: vtkDataArray

    data_name = vtk_array.GetName()
    mapper = vtkDataSetMapper()
    mapper.SetInputData(vtk_grid)
    mapper.SetScalarVisibility(True)
    mapper.ScalarVisibilityOn()
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
