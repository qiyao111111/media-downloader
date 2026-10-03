from core.credentials import validate_cookie_file, redact
from models.errors import CookieError

SUPPORT_POLICY = {'file': 'SUPPORTED', 'firefox': 'BEST EFFORT',
                  'chrome': 'EXPERIMENTAL', 'edge': 'EXPERIMENTAL'}


def cookie_options(browser=None, path=None):
    browser = None if browser in (None, '', 'None') else browser
    if browser and path:
        raise ValueError('Choose one Cookie source: browser OR cookies.txt; clear the other setting')
    if path:
        return {'cookiefile': path}
    if browser:
        return {'cookiesfrombrowser': (browser,) if isinstance(browser, str) else tuple(browser)}
    return {}


def validate(options):
    try:
        cookie_options(options.get('cookiesfrombrowser'), options.get('cookiefile'))
        validate_cookie_file(options.get('cookiefile'))
    except (ValueError, TypeError) as exc:
        raise CookieError(exc) from None


def safe_display(options):
    spec = options.get('cookiesfrombrowser')
    return {'source': 'browser' if spec else ('file' if options.get('cookiefile') else 'none'),
            'browser': spec[0] if spec else None,
            'profile': redact(spec[1]) if spec and len(spec) > 1 and spec[1] else None}
