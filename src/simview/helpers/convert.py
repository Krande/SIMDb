import meshio
import numpy as np
import pathlib


def basic_convert(filepath):
    if isinstance(filepath, str):
        filepath = pathlib.Path(filepath)

    if filepath.suffix == '.rmed':
        mesh: meshio.Mesh = meshio.read(filepath, "med")
        # RMED files have a field_data attribute that is a dict of numpy arrays
        mesh.field_data = {}
        mesh.point_data.pop('point_tags')
        # RMED has 6xN DOF's vectors, but VTU has 3xN DOF's vectors
        new_fields = {}
        for key, field in mesh.point_data.items():
            new_fields[key] = np.array_split(field, 2, axis=1)[0]

        mesh.point_data = new_fields
    else:
        raise NotImplementedError(f"Unsupported file extension {filepath.suffix}")


    mesh.write(filepath.with_suffix('.vtu'), file_format="vtu")
    return mesh


if __name__ == '__main__':
    basic_convert("../data/Cantilever_CA_EIG_sh_modes.rmed")