"""Whole-stream A/B with explicitly selected native yt-dlp runtimes."""
import json
import multiprocessing
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.option_builder import build_opts
from core.info_extractor import extract_info
from core.task import DownloadTask
from core.credentials import redact


def validate(out, runtime, js, ffmpeg, baseline=False, only=None):
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    shared = {'js_runtimes': {runtime: {'path': str(js)}}, 'ffmpeg_location': str(ffmpeg.parent),
              'socket_timeout': 30, 'retries': 3, 'fragment_retries': 3,
              'paths': {'home': str(out)}, 'embed_metadata': False, 'embed_chapters': False}
    cases = [('1080p', 1080, {}), ('4k', 2160, {})]
    if not baseline:
        cases += [('8k', 'best', {}), ('vp9-webm', 'best', {'format': '313+251', 'merge_output_format': 'webm'}),
                  ('h264-mp4', 1080, {'format': '137+140', 'merge_output_format': 'mp4'}),
                  ('av1-opus-mkv', 1080, {'format': '399+251', 'merge_output_format': 'mkv'})]
        cases += [('audio-' + fmt, 'audio', {'extract_audio': True, 'audio_format': fmt})
                  for fmt in ('mp3', 'm4a', 'opus', 'flac', 'wav', 'best')]
    if only:cases=[case for case in cases if case[0] in only]
    url = 'https://www.youtube.com/watch?v=E86EwGT_c2M'
    for name, target, extra in cases:
        row = {'case': name, 'runtime': runtime, 'ffmpeg': str(ffmpeg), 'result': 'FAIL'}
        start = time.monotonic()
        try:
            inputs = {**shared, 'outtmpl': name + '_%(id)s.%(ext)s', **extra}
            if 'format' not in extra:
                inputs['quality_target'] = target
            opts = build_opts(inputs)
            info = extract_info(url, opts)
            row['selected'] = [{k: f.get(k) for k in ('format_id', 'width', 'height', 'fps', 'vcodec', 'acodec', 'dynamic_range')}
                               for f in info.get('requested_formats') or [info]]
            last = [0]
            def progress(tid, data):
                if time.monotonic() - last[0] > 20:
                    last[0] = time.monotonic()
                    print(name, 'bytes', data.get('downloaded_bytes'), flush=True)
            task = DownloadTask(url, opts, on_progress=progress)
            task.run()
            if task.status.value=='failed' and '403' in str(task.error):
                row['failed_attempts']=[redact(task.error)]
                print(name,'fresh extraction/retry after HTTP 403',flush=True)
                info=extract_info(url,opts)
                task=DownloadTask(url,opts,on_progress=progress);task.run()
            row.update(status=task.status.value, outputs=task.output_files)
            assert task.status.value == 'completed', redact(task.error)
            assert task.output_files
            output = Path(task.output_files[0])
            probe = json.loads(subprocess.check_output([str(ffmpeg.with_name('ffprobe.exe')), '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(output)], encoding='utf-8'))
            (out / (name + '-ffprobe.json')).write_text(json.dumps(probe, indent=2), encoding='utf-8')
            assert any(s['codec_type'] == 'audio' for s in probe['streams'])
            assert abs(float(probe['format']['duration']) - info['duration']) < 2
            if not name.startswith('audio-'):
                video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
                selected = row['selected'][0]
                assert (video['width'], video['height']) == (selected['width'], selected['height'])
                if name == '8k':
                    assert (video['width'], video['height']) == (7680, 4320)
                codec = {'av01': 'av1', 'vp09': 'vp9', 'vp9': 'vp9', 'avc1': 'h264'}[selected['vcodec'].split('.')[0]]
                assert video['codec_name'] == codec
                num, den = map(int, video['avg_frame_rate'].split('/'))
                assert abs(num / den - selected['fps']) < .1
            with (out / (name + '-decode-errors.log')).open('wb') as errors, (out / (name + '-decode-progress.log')).open('wb') as log:
                result = subprocess.run([str(ffmpeg), '-v', 'error', '-stats_period', '10', '-progress', 'pipe:1', '-i', str(output),
                                         '-fps_mode', 'passthrough', '-enc_time_base:v', 'demux', '-f', 'null', '-'], stdout=log, stderr=errors)
            row.update(decode_exitcode=result.returncode, decode_error_bytes=(out / (name + '-decode-errors.log')).stat().st_size,
                       bytes=output.stat().st_size, duration=probe['format']['duration'])
            assert result.returncode == 0 and row['decode_error_bytes'] == 0
            row['result'] = 'PASS'
        except Exception as error:
            row['error'] = redact(error)
        row['seconds'] = round(time.monotonic() - start, 3)
        rows.append(row)
        (out / 'results.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
        print(json.dumps(row), flush=True)
        assert row['result'] == 'PASS', row.get('error')


if __name__ == '__main__':
    multiprocessing.freeze_support()
    only=next((arg.split('=',1)[1].split(',') for arg in sys.argv if arg.startswith('--only=')),None)
    validate(Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3]).resolve(), Path(sys.argv[4]).resolve(), '--baseline' in sys.argv,only)
