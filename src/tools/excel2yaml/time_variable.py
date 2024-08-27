from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from typing_extensions import Self


@dataclass
class TimeVariable:
    old_name: str
    old_timezone: str
    string_format: str | None = None

    def __post_init__(self):
        self.new_name = "time"
        self.dtype = "datetime64[ns]"
        self.units = "Seconds since 1970-01-01 00:00:00 UTC"
        self.long_name = "Time"
        self.standard_name = "time"

    @classmethod
    def from_sheet(cls, filepath: str | Path) -> Self:
        sheet = pd.read_excel(
            filepath, sheet_name="Independent Variables", header=1, nrows=1
        )
        data = sheet.where(pd.notnull(sheet), None).to_dict(orient="records")
        variables: list[Self] = []
        for row in data:
            row_data = {k: v for k, v in row.items() if not pd.isnull(v)}
            variables.append(
                cls(
                    old_name=row_data.pop("Original Name", None),
                    old_timezone=row_data.pop("Original Timezone", "UTC"),
                    string_format=row_data.pop("String Format", None),
                )
            )
        return variables[0]
