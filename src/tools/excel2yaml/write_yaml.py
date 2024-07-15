from pathlib import Path
from typing import Any

import ruamel.yaml.comments

yaml = ruamel.yaml.YAML()


def write_yaml(cfg: dict[str, Any], filepath: Path) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)

    data = ruamel.yaml.comments.CommentedMap(cfg)
    top_level_keys = list(cfg)
    for key in top_level_keys[1:]:
        data.yaml_set_comment_before_after_key(key, before="\n")

    yaml.dump(data, filepath)
    return
