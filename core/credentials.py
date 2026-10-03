"""Keep session credentials out of persisted settings and diagnostics."""

import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def redact(text):
    text = re.sub(r'(?i)([a-z][a-z0-9+.-]*://)[^\s/]*@', r'\1***@', str(text))
    text = re.sub(r'(?i)((?:authorization|proxy-authorization|cookie|set-cookie)\s*[:=]\s*)[^\r\n]+', r'\1***', text)
    text = re.sub(r'(?i)((?:__Secure-[13]P)?(?:SID|HSID|SAPISID|APISID|LOGIN_INFO)\s*[:=]\s*)[^\s;,]+', r'\1***', text)
    return re.sub(r'([?&][^=&\s]+=)[^&\s]+', r'\1***', text)


def validate_cookie_file(path):
    """Reject malformed entries before yt-dlp can print their raw values."""
    if not path:
        return
    file = Path(path)
    if not file.is_file():
        raise ValueError('Cookie file does not exist or is not a regular file')
    try:
        with file.open(encoding='utf-8') as stream:
            if not re.match(r'#(?: Netscape)? HTTP Cookie File', stream.readline()):
                raise ValueError('Cookie file must have a Netscape HTTP Cookie File header')
            for number, line in enumerate(stream, 2):
                if line.startswith('#HttpOnly_'):
                    line = line[len('#HttpOnly_'):]
                elif line.startswith('#') or not line.strip():
                    continue
                fields = line.rstrip('\r\n').split('\t')
                if (len(fields) != 7 or fields[1] not in ('TRUE', 'FALSE')
                        or fields[3] not in ('TRUE', 'FALSE')
                        or (fields[4] and not re.fullmatch(r'[0-9]+(?:\.[0-9]+)?', fields[4]))
                        or fields[0].startswith('.') != (fields[1] == 'TRUE')):
                    raise ValueError(f'Invalid Netscape Cookie file entry at line {number}; contents hidden')
    except (OSError, UnicodeError) as exc:
        raise ValueError('Cookie file cannot be read as UTF-8 Netscape cookies') from None


def persistent_url(value):
    if not isinstance(value, str):
        return ''
    try:
        parts = urlsplit(value)
    except ValueError:
        return ''
    query = [(key, val) for key, val in parse_qsl(parts.query, keep_blank_values=True)
             if not re.search(r'(?i)token|password|authorization|signature|^(?:auth|key|sig|lsig)$', key)]
    return urlunsplit(parts._replace(netloc=parts.netloc.rsplit('@', 1)[-1], query=urlencode(query)))


def persistent_options(options):
    """Passwords are session-only; cookie *paths* remain usable across restarts."""
    clean = dict(options)
    for key in list(clean):
        if key.lower() in ('password', 'videopassword', 'token', 'access_token', 'authorization'):
            clean.pop(key)
    for key in ('proxy', 'geo_verification_proxy'):
        value = clean.get(key)
        if value:
            clean[key] = persistent_url(value)
    if 'http_headers' in clean:
        headers = clean['http_headers']
        clean['http_headers'] = {k: v for k, v in headers.items()
                                 if k.lower() not in ('cookie', 'authorization', 'proxy-authorization')} if isinstance(headers, dict) else {}
    return clean


class SafeLogger:
    def debug(self, message):
        pass

    def warning(self, message):
        print(redact(message), file=sys.stderr)

    def error(self, message):
        print(redact(message), file=sys.stderr)
