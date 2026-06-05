# arcgis-item-dependency-interrogation Python Toolbox (`arcgis_dependency.pyt`)

This is the documentation to be included if planning on packaging the `arcgis_dependency.pyt`
toolbox using the `make pyt_pkg` command invoking the `./scripts/make_pyt_archive.pyt`. This script
packages the `arcgis_dependency.pyt`, supporting Python package 
`./src/arcgis_dependency` and any dependencies listed in `pyproject.toml`. This enables you to
distribute the Python toolbox for non-technical users with any custom libraries you are utilizing.