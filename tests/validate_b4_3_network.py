"""Reuse the established live proxy/cookie acceptance with explicit runtimes."""
import multiprocessing
import sys
from pathlib import Path
import validate_network


if __name__ == '__main__':
    multiprocessing.freeze_support()
    root=Path(__file__).resolve().parents[1]
    runtime,js,ffmpeg=sys.argv[2],str(Path(sys.argv[3]).resolve()),Path(sys.argv[4]).resolve()
    # The full legacy binary generates host-only fixtures; download/processing
    # explicitly use the candidate. No system PATH or installation is changed.
    original=validate_network.build_opts
    def options(inputs):
        inputs=dict(inputs);inputs.setdefault('js_runtimes',{runtime:{'path':js}})
        inputs.setdefault('ffmpeg_location',str(ffmpeg.parent))
        return original(inputs)
    validate_network.build_opts=options
    validate_network.validate(Path(sys.argv[1]).resolve(),str(root/'bin/ffmpeg.exe'),'mpeg4')
