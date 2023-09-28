from dataclasses import dataclass
from typing import Optional

from dataclass_wizard import YAMLWizard


NES_FRAMERATE = 1008307711 / 256 / 65536
NES_MS_PER_FRAME = 1000.0 / NES_FRAMERATE


@dataclass
class Split:
    path: str
    x: int
    y: int
    width: int
    height: int
    command_name: Optional[str] = None
    active: bool = True
    split_offset_s: Optional[float] = 0
    split_wait_s: Optional[float] = 0
    description: Optional[str] = None


@dataclass
class Settings(YAMLWizard):
    splits: list[Split]
    video_capture_source: int
    split_wait_s_default: Optional[float] = 5.0
    split_offset_s_default: Optional[float] = 0.65
    file_log_level: Optional[str] = "INFO"
    console_log_level: Optional[str] = "INFO"
    show_capture_video: Optional[bool] = False
    write_capture_video: Optional[bool] = False
    sequential: Optional[bool] = False
    confidence: float = 0.95

    @classmethod
    def load(cls, path="config.yml"):
        return Settings.from_yaml_file(path)
