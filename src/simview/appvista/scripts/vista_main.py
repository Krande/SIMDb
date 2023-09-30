import pyvista as pv
from pyvista import examples

sphere = examples.load_sphere_vectors()
warped = sphere.warp_by_vector()

warp_factors = [0, 1.5, 3.5, 5.5]
p = pv.Plotter(shape=(2, 2))
for i in range(2):
    for j in range(2):
        idx = 2 * i + j
        p.subplot(i, j)
        p.add_mesh(sphere.warp_by_vector(factor=warp_factors[idx]))
        p.add_text(f'factor={warp_factors[idx]}')
p.show()