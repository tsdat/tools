import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Hashable

import pandas as pd
from typing_extensions import Self


@dataclass
class DatasetMetadata:
    title: str
    description: str
    location: str
    dataset_name: str
    data_level: str
    qualifier: str | None
    temporal: str | None
    additional_metadata: dict[Hashable, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.location_id = self.generate_location_id(self.location)

    @staticmethod
    def generate_location_id(location: str) -> str:
        return re.sub(r"[^a-zA-Z0-9]+", "_", location.lower())

    @classmethod
    def from_sheet(cls, filepath: str | Path) -> Self:
        sheet = pd.read_excel(filepath, sheet_name="Metadata", header=1)
        df = sheet[["Metadata Label", "Value"]]
        df.loc[:, "Metadata Label"] = df["Metadata Label"].str.strip()
        df = df[df["Metadata Label"].str.len() > 0].set_index("Metadata Label")
        data = {
            k: v["Value"]
            for k, v in df.to_dict(orient="index").items()
            if v["Value"] is not None
        }
        return cls(
            title=data.pop("Title"),
            description=data.pop("Description"),
            location=data.pop("Location"),
            dataset_name=data.pop("Name"),
            data_level=data.pop("Data Level"),
            qualifier=data.pop("Qualifier", None),
            temporal=data.pop("Temporal", None),
            additional_metadata=data,
        )

    def to_dict(self) -> dict[str, Any]:
        result = dict(
            title=self.title,
            description=self.description,
            location=self.location,
            location_id=self.location_id,
            dataset_name=self.dataset_name,
            data_level=self.data_level,
        )
        result.update(self.additional_metadata)  # type: ignore
        if self.qualifier is not None:
            result["qualifier"] = self.qualifier
        if self.temporal is not None:
            result["temporal"] = self.temporal

        return result
