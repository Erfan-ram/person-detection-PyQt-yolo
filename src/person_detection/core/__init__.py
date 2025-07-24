"""Core configuration and model management."""

from .config import Config

def get_model_manager():
    """Get the model manager instance (lazy import)."""
    from .models import model_manager
    return model_manager

__all__ = ["Config", "get_model_manager"]