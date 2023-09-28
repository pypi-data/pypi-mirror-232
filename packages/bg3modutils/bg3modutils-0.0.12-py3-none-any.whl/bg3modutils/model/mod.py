from typing import List
from bg3modutils.model.meta import Meta
from bg3modutils.model.progression import Progression
from bg3modutils.utils.lslib import LSLib


class Mod:
    def __init__(self, meta: Meta = None, progressions: List[Progression] = None) -> None:
        self.meta = meta
        self.progressions = progressions
