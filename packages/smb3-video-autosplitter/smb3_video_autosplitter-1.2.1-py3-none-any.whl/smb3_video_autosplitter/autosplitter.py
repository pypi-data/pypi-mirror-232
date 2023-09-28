"""
video based autosplitter for smb3
"""
from dataclasses import dataclass
import logging
import time
from typing import Optional

import cv2

from smb3_video_autosplitter.livesplit import Livesplit
from smb3_video_autosplitter.settings import Settings
from smb3_video_autosplitter.util import locate_all_opencv

LOGGER = logging.getLogger(__name__)


@dataclass
class Split:
    path: str
    image: any
    region: list[int, int, int, int]
    command_name: str
    split_offset_s: Optional[float] = 0
    split_wait_s: Optional[float] = 0


class Autosplitter:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.initialize_splits()
        self.earliest_next_trigger_time = 0
        self.livesplit = Livesplit()

    def tick(self, frame):
        if frame is None or self.earliest_next_trigger_time >= time.time():
            return
        for split in self.candidate_splits:
            results = list(
                locate_all_opencv(
                    split.image,
                    frame,
                    region=split.region,
                    confidence=self.settings.confidence,
                )
            )
            if results:
                if self.settings.sequential:
                    self.splits.pop(0)
                self.handle_split_image_found(split, results)

    def handle_split_image_found(self, split: Split, results):
        sleep_duration = (
            split.split_offset_s
            if split.split_offset_s
            else self.settings.split_offset_s_default
        )
        time.sleep(sleep_duration)
        split_wait_s = (
            split.split_wait_s
            if split.split_wait_s
            else self.settings.split_wait_s_default
        )
        self.earliest_next_trigger_time = time.time() + split_wait_s

        log_str = (
            f"{split.path} observed {len(results)} times at {list(map(str, results))}"
        )
        if split.command_name:
            LOGGER.info(f"Triggering {split.command_name} after {log_str}")
            self.livesplit.send(split.command_name)
        else:
            LOGGER.info(log_str)

    def initialize_splits(self):
        self.splits: list[Split] = []
        for split in self.settings.splits:
            if not split.active:
                continue
            image = cv2.imread(split.path)
            region = [split.x, split.y, split.width, split.height]
            self.splits.append(
                Split(
                    path=split.path,
                    image=image,
                    region=region,
                    command_name=split.command_name,
                    split_offset_s=split.split_offset_s,
                    split_wait_s=split.split_wait_s,
                )
            )

    @property
    def candidate_splits(self):
        if self.settings.sequential:
            return self.splits[:1]
        return self.splits

    def reset(self):
        self.initialize_splits()

    def terminate(self):
        self.livesplit.terminate()
