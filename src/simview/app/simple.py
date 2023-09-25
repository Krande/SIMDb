import trame

# Create a layout with a file input and a 3D view
layout = trame.layouts.SinglePage("VTK Viewer")
file_input = trame.widgets.FileInput(label="Select a vtk file")
view = trame.widgets.VtkView()

# Add the widgets to the layout
layout.content.children.append(file_input)
layout.content.children.append(view)


# Define a callback function that loads the vtk file and renders it
def load_vtk_file():
    # Get the file content from the file input widget
    file_content = file_input.get_file_content()
    if file_content:
        # Create a vtk reader from the file content
        reader = trame.vtk_io.create_reader(file_content)
        if reader:
            # Set the reader as the source of the 3D view
            view.set_source(reader)


# Register the callback function to the file input widget
file_input.on_change(load_vtk_file)

if __name__ == '__main__':
    # Start the trame app
    trame.start(layout)
