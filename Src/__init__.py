# -*- coding: utf-8 -*-
"""
File __init__.py để package Src
"""

# Import các class chính
from .components.image_detector import ImageDetector
from .components.automation_core import AutomationCore
from .components.stats_manager import StatsManager
from .components.loop_detector import LoopDetector
from .components.ui_components import AutoSICUI

__version__ = "1.0.0"
__all__ = [
    "ImageDetector",
    "AutomationCore", 
    "StatsManager",
    "LoopDetector",
    "AutoSICUI"
]
