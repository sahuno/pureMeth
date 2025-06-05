import json
from typing import Any, IO, Union

# Minimal YAML stub used when PyYAML is unavailable.
# Implements a subset of the PyYAML API relied on by this project.

class _Resolver:
    class BaseResolver:
        DEFAULT_MAPPING_TAG = 'tag:yaml.org,2002:map'

resolver = _Resolver()


def safe_load(stream: Union[str, bytes, IO[str]]) -> Any:
    """Parse a JSON/YAML string or file-like object into Python objects."""
    if hasattr(stream, "read"):
        return json.load(stream)
    return json.loads(stream)


def dump(data: Any, stream: IO[str] = None, default_flow_style: bool = False,
         sort_keys: bool = True, indent: int = 2) -> str:
    """Serialize *data* to YAML. Only a JSON subset is supported."""
    if stream is None:
        return json.dumps(data, indent=indent, sort_keys=sort_keys)
    json.dump(data, stream, indent=indent, sort_keys=sort_keys)
    return ""


def add_representer(*args, **kwargs) -> None:  # pragma: no cover - stub
    """Stub for compatibility with PyYAML's add_representer."""
    # This stub intentionally does nothing because the simplified JSON
    # serialization used here does not support custom representers.
    return None
