from tools.main import app
from typer.testing import CliRunner


def test_data2yaml_writes_config():
    result = CliRunner().invoke(
        app,
        [
            "data2yaml",
            "test/data2yaml/data/morro.buoy_z06-waves.a1.20201201.000000.nc",
            "--outdir",
            "data/data2yaml",
        ],
    )
    assert result.exit_code == 0, result.stdout
