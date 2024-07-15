from pathlib import Path

from tsdat.config.dataset import DatasetConfig
from tsdat.config.retriever import RetrieverConfig
from typer.testing import CliRunner

from tsdat_tools.main import app

runner = CliRunner()


def _load_dataset_cfg(cfg_path: str) -> DatasetConfig:
    path = Path(cfg_path)
    assert path.exists()
    return DatasetConfig.from_yaml(path)


def _load_retriever_cfg(cfg_path: str) -> RetrieverConfig:
    path = Path(cfg_path)
    assert path.exists()
    return RetrieverConfig.from_yaml(path)


def test_excel2yaml_generates_excel_template():
    result = runner.invoke(app, ["excel2yaml", "init", "data/excel2yaml/template.xlsx"])
    assert result.exit_code == 0, result.stdout
    assert Path("data/excel2yaml/template.xlsx").exists()


def test_excel2yaml_generates_config_files():
    result = runner.invoke(
        app,
        [
            "excel2yaml",
            "run",
            "tsdat_tools/excel2yaml/template.xlsx",
            "--output-dir",
            "data/excel2yaml",
        ],
    )
    assert result.exit_code == 0, result.stdout

    output_dataset_cfg = _load_dataset_cfg("data/excel2yaml/dataset.yaml")
    expected_dataset_cfg = _load_dataset_cfg("test/excel2yaml/data/dataset.yaml")
    assert output_dataset_cfg == expected_dataset_cfg

    output_retriever_cfg = _load_retriever_cfg("data/excel2yaml/retriever.yaml")
    expected_retriever_cfg = _load_retriever_cfg("test/excel2yaml/data/retriever.yaml")
    assert output_retriever_cfg == expected_retriever_cfg
