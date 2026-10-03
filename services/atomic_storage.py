"""Same-directory replacement with a last valid JSON backup."""
import json
import os
import tempfile
from pathlib import Path


def load_json(path, default, validator=lambda value: True):
    path = Path(path)
    for candidate in (path, path.with_name(path.name+'.bak')):
        try:
            value = json.loads(candidate.read_text(encoding='utf-8'))
            if validator(value):
                return value
        except (OSError, UnicodeError, ValueError):
            pass
    return default


def _replace_bytes(path, data):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name+'.', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def save_json(path, value, sanitize_previous=None):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    # Serialization failure happens before either existing file is touched.
    data = json.dumps(value, indent=2, ensure_ascii=False).encode('utf-8')
    try:
        previous = path.read_bytes(); parsed = json.loads(previous)
        if sanitize_previous is not None:
            previous = json.dumps(sanitize_previous(parsed),indent=2,ensure_ascii=False).encode('utf-8')
    except (OSError, UnicodeError, ValueError):
        previous = None
    if previous is not None:
        _replace_bytes(path.with_name(path.name+'.bak'), previous)
    _replace_bytes(path, data)
