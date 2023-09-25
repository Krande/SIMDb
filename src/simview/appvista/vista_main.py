import pyvista as pv
import numpy as np

dargs = dict(
    cmap="jet",
    show_scalar_bar=True,
)
mesh = pv.read('../data/Cantilever_CA_EIG_sh_modes.rmed', file_format='med')
pv.save_meshio('output.vtu', mesh)
p = pv.Plotter(shape=(2, 1))
p.subplot(0, 0)
scalar_str = '00000026DEPL[0] - 5.05423'
# mesh_warped = mesh.warp_by_scalar(scalar_str, factor=6)

warp_vectors = mesh.get_array(scalar_str).reshape(-1, 3)
magnitude = np.sum(warp_vectors, axis=1)
mesh_warped = mesh.warp_by_vector(vectors=warp_vectors, factor=6.0)
p.add_mesh(mesh_warped, show_edges=True, **dargs)
# split_cells = mesh.explode(0.5)
# p.add_mesh(split_cells, color='red', show_edges=True)
p.show()
