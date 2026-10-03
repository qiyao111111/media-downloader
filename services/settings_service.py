from configs.app_settings import AppSettings
from models.settings import Settings, DownloadPreset


def merge_preset(settings, preset):
    result = {**settings, **DownloadPreset(preset).download_options()}
    if 'format' in preset and 'quality_target' not in preset:
        result.pop('quality_target', None)
        result.pop('quality_label', None)
    if 'embedsubtitles' in preset:
        result['embed_subs'] = preset['embedsubtitles']
    return result


class SettingsService(AppSettings):
    """Reuse the existing JSON store; typed projection does not migrate its schema."""

    def model(self):
        d = self.to_dict()
        browser = d.get('cookiesfrombrowser', 'None')
        return Settings(download_directory=d.get('download_path', ''), filename_template=d.get('outtmpl', ''),
            default_quality_mode=d.get('format') or 'source', default_container=d.get('merge_output_format', ''),
            audio_only_format=d.get('audio_format', 'mp3'), cookies_path=d.get('cookiefile', ''),
            cookies_source='file' if d.get('cookiefile') else ('browser' if browser != 'None' else 'none'),
            browser=browser if browser != 'None' else '', proxy_enabled=bool(d.get('proxy')),
            proxy_url=d.get('proxy', ''), ffmpeg_path=d.get('ffmpeg_location', ''),
            max_concurrent_downloads=d.get('max_workers', 3), concurrent_fragments=d.get('concurrent_fragment_downloads', 1),
            theme=d.get('theme', 'light'), language=d.get('language', 'en'))
