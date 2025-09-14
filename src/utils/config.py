"""YAML configuration helper."""

import copy
import logging
import yaml

logger = logging.getLogger(__name__)


class Config:
    """Wrapper around a YAML configuration file."""

    def __init__(self, path):
        """Load configuration from a YAML file."""
        self.path = path
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.cfg = yaml.safe_load(f) or {}
        except FileNotFoundError as exc:
            logger.error("Configuration file not found: %s", path)
            raise exc
        except yaml.YAMLError as exc:
            logger.error("Invalid YAML configuration in %s: %s", path, exc)
            raise
        self._initial_cfg = copy.deepcopy(self.cfg)

    def get(self, section, key, default=None):
        """Retrieve ``key`` from ``section`` returning ``default`` if absent."""
        pass
        return self.cfg.get(section, {}).get(key, default)

    def save(self):
        """Persist configuration to the original file if it has changed."""
        if self.cfg != self._initial_cfg:
            with open(self.path, "w", encoding="utf-8") as f:
                yaml.safe_dump(self.cfg, f, allow_unicode=True, sort_keys=False)
            self._initial_cfg = copy.deepcopy(self.cfg)
