import os
from collections.abc import Callable, Generator
from typing import Any

from mesh_common import try_strtobool


class EnvConfig:
    def __init__(self, from_env=True, feature_overrides: dict[str, bool] | None = None, **kwargs):
        settings: dict[str, Any] = {}

        if from_env:
            features = {}
            for key, value in os.environ.items():
                if not key.startswith("MESH_"):
                    continue
                key = key.replace("MESH_", "", 1).replace("-", "_").lower()
                if key.startswith("feature_"):
                    features[key.replace("feature_", "", 1)] = try_strtobool(value)
                    continue

                settings[key] = value
            settings["feature"] = EnvConfig(from_env=False, **features)  # type: ignore[arg-type]
        settings.update(kwargs)
        if feature_overrides:
            for feature, toggle in feature_overrides.items():
                settings["feature"].__setattr__(feature, toggle)

        self._keys: list[str] = sorted(settings.keys())

        for key, value in settings.items():
            self.__setattr__(key, value)

    # This is here to keep the linter happy as it does not recognise the magic getter method. This seems to pacify it"""
    def __getattr__(self, item):
        super().__getattribute__(item)

    def get(self, key: str, default: Any | None = None) -> Any | None:
        key = (key or "").strip().lower()
        if not key:
            raise KeyError("empty key")

        return self.__dict__.get(key, default)

    def keys(self, predicate: Callable[[str], bool] | None = None) -> Generator[str, None, None]:
        for key in self._keys:
            if predicate is not None and not predicate(key):
                continue
            yield key

    def values(self, predicate: Callable[[str], bool] | None = None) -> Generator[Any, None, None]:
        for key in self._keys:
            if predicate is not None and not predicate(key):
                continue
            yield self.__dict__[key]
