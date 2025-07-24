"""Detection and camera management modules."""

from .detector import PersonDetector
from .camera import CameraChecker

__all__ = ["PersonDetector", "CameraChecker"]