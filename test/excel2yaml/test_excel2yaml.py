from pathlib import Path

from tools.excel2yaml.cli import app
from tsdat.config.dataset import DatasetConfig
from tsdat.config.retriever import RetrieverConfig
from typer.testing import CliRunner

runner = CliRunner()


def test_excel2yaml():
    result = runner.invoke(
        app,
        ["src/tools/excel2yaml/template.xlsx", "--output-dir", "data/excel2yaml"],
    )
    assert result.exit_code == 0, result.stdout

    output_dataset_cfg_path = Path("data/excel2yaml/dataset.yaml")
    output_retriever_cfg_path = Path("data/excel2yaml/retriever.yaml")
    assert output_dataset_cfg_path.exists()
    assert output_retriever_cfg_path.exists()
    output_dataset = DatasetConfig.from_yaml(output_dataset_cfg_path)
    output_retriever = RetrieverConfig.from_yaml(output_retriever_cfg_path)

    expected_dataset_cfg_path = Path("test/excel2yaml/data/dataset.yaml")
    expected_retriever_cfg_path = Path("test/excel2yaml/data/retriever.yaml")
    assert expected_dataset_cfg_path.exists()
    assert expected_retriever_cfg_path.exists()
    expected_dataset = DatasetConfig.from_yaml(expected_dataset_cfg_path)
    expected_retriever = RetrieverConfig.from_yaml(expected_retriever_cfg_path)

    assert output_dataset == expected_dataset
    assert output_retriever == expected_retriever
