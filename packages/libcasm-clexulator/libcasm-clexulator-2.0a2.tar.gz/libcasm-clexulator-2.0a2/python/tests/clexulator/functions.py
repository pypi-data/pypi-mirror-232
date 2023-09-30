import pathlib


def make_source(dir, title, bsetname):
    return str(
        pathlib.Path(dir)
        / title
        / "basis_sets"
        / ("bset." + bsetname)
        / (title + "_Clexulator_" + bsetname + ".cc")
    )
