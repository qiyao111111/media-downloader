from urllib.parse import urlsplit
from core.credentials import redact


def proxy_options(value='', key='proxy'):
    if not isinstance(value, str):
        raise ValueError('Proxy URL must be text')
    if value:
        try:
            parts = urlsplit(value)
            if parts.scheme not in ('http', 'https', 'socks5', 'socks5h') or not parts.hostname or parts.port == 0:
                raise ValueError()
        except ValueError:
            raise ValueError('Invalid proxy URL; use http://, socks5:// or socks5h://host:port') from None
    return {key: value}


def safe_display(value):
    return redact(value)
