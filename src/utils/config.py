"""YAML configuration helper."""

import logging
import yaml

logger = logging.getLogger(__name__)


class Config:
    """Wrapper around a YAML configuration file."""

    def __init__(self, path):
        """Load configuration from a YAML file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.cfg = yaml.safe_load(f) or {}
        except FileNotFoundError as exc:
            logger.error("Configuration file not found: %s", path)
            raise exc
        except yaml.YAMLError as exc:
            logger.error("Invalid YAML configuration in %s: %s", path, exc)
            raise

    def get(self, section, key, default=None):
        """Retrieve ``key`` from ``section`` returning ``default`` if absent."""
        pass
        return self.cfg.get(section, {}).get(key, default)
