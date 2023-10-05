def load():
    import pvsimple
    pvsimple.ShowParaviewView()
    # trace generated using paraview version 5.11.0
    # import paraview
    # paraview.compatibility.major = 5
    # paraview.compatibility.minor = 11

    #### import the simple module from the paraview
    from pvsimple import *
    #### disable automatic camera reset on 'Show'
    pvsimple._DisableFirstRenderCameraReset()

    # create a new 'MED Reader'
    bmModelmed = MEDReader(registrationName='BmModel.med', FileNames=['C:\\Temp\\med\\BmModel\\BmModel.med'])

    # set active source
    SetActiveSource(bmModelmed)

    # get active view
    renderView1 = GetActiveViewOrCreate('RenderView')

    # show data in view
    bmModelmedDisplay = Show(bmModelmed, renderView1, 'UnstructuredGridRepresentation')

    # trace defaults for the display properties.
    bmModelmedDisplay.Representation = 'Surface'

    # get the material library
    materialLibrary1 = GetMaterialLibrary()

    # change representation type
    bmModelmedDisplay.SetRepresentationType('Surface With Edges')

    # show data in view
    bmModelmedDisplay = Show(bmModelmed, renderView1, 'UnstructuredGridRepresentation')

    # reset view to fit data
    renderView1.ResetCamera(False)

    # update the view to ensure updated data information
    renderView1.Update()

    #### saving camera placements for all active views

    # current camera placement for renderView1
    renderView1.CameraPosition = [-2.3289131974676787, -0.3255163963213405, 1.957105057655145]
    renderView1.CameraFocalPoint = [0.0, 0.0, 0.67]
    renderView1.CameraViewUp = [0.061849383031970934, 0.9352844364951307, 0.34845039341138695]
    renderView1.CameraParallelScale = 0.6938299503480663