from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel

config_path = Path("~/.config/paperlibrary.yaml").expanduser()


class Config(BaseModel):
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
            return Config.model_validate(data)
    except FileNotFoundError:
        return


def config_check(config: Config):
    if not config:
        print('please run "pap init" first to create a config file')
        exit()

def save_config(config: Config) -> None:
    with config_path.open("w") as f:
        yaml.safe_dump(config.to_dict(), f)
