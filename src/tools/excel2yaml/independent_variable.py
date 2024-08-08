from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
from typing_extensions import Self


@dataclass
class IndependentVariable:
    new_name: str
    old_name: str
    dtype: str
    new_unit: str = "1"
    old_unit: str = "1"
    timezone: str | None = None
    long_name: str | None = None
    standard_name: str | None = None
    additional_metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.new_unit = self.new_unit if self.new_unit is not None else "1"
        self.old_unit = self.old_unit if self.old_unit is not None else "1"

    @classmethod
    def from_sheet(cls, filepath: str | Path) -> list[Self]:
        sheet = pd.read_excel(filepath, sheet_name="Independent Variables", header=1)
        data = sheet.where(pd.notnull(sheet), None).to_dict(orient="records")
        variables: list[Self] = []
        for row in data:
            row_data = {k: v for k, v in row.items() if not pd.isnull(v)}
            variables.append(
                cls(
                    new_name=row_data.pop("New Name", None),
                    old_name=row_data.pop("Original Name", None),
                    new_unit=row_data.pop("Standardized Unit", None),
                    old_unit=row_data.pop("Original Unit", None),
                    timezone=row_data.pop("Original Timezone", None),
                    dtype=row_data.pop("Datatype", None),
                    long_name=row_data.pop("Long Name", None),
                    standard_name=row_data.pop("Standard Name", None),
                    additional_metadata=row_data,  # type: ignore
                )
            )
        return variables
