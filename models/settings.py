from dataclasses import dataclass, field


PROTECTED_SETTINGS = frozenset(('proxy', 'geo_verification_proxy', 'proxy_url', 'proxy_enabled',
    'cookiefile', 'cookiesfrombrowser', 'cookies_source', 'cookies_path', 'browser', 'browser_profile',
    'download_path', 'download_directory', 'outtmpl', 'filename_template', 'paths',
    'ffmpeg_location', 'ffmpeg_path', 'ffprobe_path', 'username', 'password', 'netrc',
    'max_workers', 'max_concurrent_downloads', 'theme', 'language'))


@dataclass(frozen=True)
class Settings:
    download_directory: str = ''
    filename_template: str = ''
    default_quality_mode: str = 'source'
    default_container: str = ''
    audio_only_format: str = 'mp3'
    cookies_source: str = 'none'
    cookies_path: str = ''
    browser: str = ''
    browser_profile: str | None = None
    proxy_enabled: bool = False
    proxy_url: str = ''
    ffmpeg_path: str = ''
    ffprobe_path: str = ''
    max_concurrent_downloads: int = 3
    concurrent_fragments: int = 1
    retries: int = 10
    fragment_retries: int = 10
    theme: str = 'light'
    language: str = 'en'


@dataclass(frozen=True)
class DownloadPreset:
    options: dict = field(default_factory=dict)

    def download_options(self):
        return {k: v for k, v in self.options.items() if k not in PROTECTED_SETTINGS}
