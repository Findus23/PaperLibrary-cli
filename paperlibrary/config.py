from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml
from dataclasses_json import dataclass_json, DataClassJsonMixin

config_path = Path("~/.config/paperlibrary.yaml").expanduser()


@dataclass_json
@dataclass
class Config(DataClassJsonMixin):
    url: str
    auth_token: str
    basedir: str

    @property
    def basedir_path(self):
        return Path(self.basedir)


def get_config() -> Optional[Config]:
    try:
        with config_path.open() as f:
            data = yaml.safe_load(f)
            if not data:
                raise ValueError("config file is empty")
            return Config.from_dict(data)
    except FileNotFoundError:
        return


def save_config(config: Config) -> None:
    with config_path.open("w") as f:
        yaml.safe_dump(config.to_dict(), f)


