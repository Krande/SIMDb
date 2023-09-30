import fastapi
import pyvista as pv
import uvicorn

# Create a FastAPI app
app = fastapi.FastAPI()

# Create a PyVista plotter
plotter = pv.Plotter("trame")


# Define a route for the web app
@app.get("/")
def index():
    # Return a HTML page with a 3D view of a sphere
    sphere = pv.Sphere()
    plotter.add_mesh(sphere)
    return plotter


# Run the app with Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
