import os
from dataclasses import dataclass


@dataclass
class LoginPreviewSettings:
    n_recent_icons: int = int(os.getenv("PREVIEW_N_RECENT", 10))
    icon_size: int = int(os.getenv("PREVIEW_ICON_SIZE", 100))
    icon_margin: int = int(os.getenv("PREVIEW_ICON_MARGIN", 10))
    icon_border: int = int(os.getenv("PREVIEW_ICON_BORDER", 8))
    speed_sec: int = int(os.getenv("PREVIEW_CAROUSEL_SPEED_SEC", 10))


@dataclass
class LoginEntriesSettings:
    n_recent_rows: int = int(int(os.getenv("ENTRIES_N_RECENT", 5)))
