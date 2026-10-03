"""Offline selection contract and native yt-dlp callback checks."""
import pickle
import unittest
from dataclasses import replace
import yt_dlp
from core.format_selector import *
from core.option_builder import build_opts, QualitySelector
from models.format import FormatKind


def video(fid='v', height=1080, **kw):
    return normalize_format(dict(format_id=fid, width=height*16//9, height=height, fps=30,
                                 vcodec='av01.0.08M.08', acodec='none', ext='mp4',
                                 url='https://example.invalid/video', protocol='https', **kw))


def audio(fid='a', **kw):
    return normalize_format(dict(format_id=fid, vcodec='none', acodec='opus', ext='webm',
                                 url='https://example.invalid/audio', protocol='https', **kw))


class FormatSelectorTests(unittest.TestCase):
    def resolution(self, high, low):
        a,b=video('hi',high),video('lo',low)
        self.assertEqual(select_best_video([b,a]),a)
    def test_1080_over_720(self): self.resolution(1080,720)
    def test_4k_over_1080(self): self.resolution(2160,1080)
    def test_8k_over_4k(self): self.resolution(4320,2160)
    def test_above_8k(self):
        self.resolution(8640,4320)
        self.assertIn('8640P',video(height=8640).label)
        self.assertNotIn('8K',video(height=8640).label)
    def test_fps(self):
        p=video();self.assertEqual(select_best_video([p,replace(p,fps=60)]).fps,60)
        self.assertEqual(select_best_video([replace(p,fps=120),video('4k',2160)]).height,2160)
    def test_hdr(self):
        p=video(dynamic_range='SDR');h=video('hdr',dynamic_range='HDR10')
        self.assertEqual(select_best_video([p,h]),h)
        self.assertEqual(len(build_quality_options([p,h])),2)
    def test_av1_over_vp9(self):
        p=video();self.assertEqual(select_best_video([replace(p,video_codec_family='VP9'),p]),p)
    def test_vp9_over_h264(self):
        p=replace(video(),video_codec_family='VP9')
        self.assertEqual(select_best_video([replace(p,video_codec_family='H264'),p]),p)
    def test_video_kind(self): self.assertEqual(video().kind,FormatKind.VIDEO_ONLY)
    def test_audio_kind(self): self.assertEqual(audio().kind,FormatKind.AUDIO_ONLY)
    def test_muxed_kind(self):
        p=normalize_format({'format_id':'m','vcodec':'h264','acodec':'aac'})
        self.assertEqual(p.kind,FormatKind.MUXED)
    def test_missing_width(self): self.assertEqual(normalize_format({'height':1080}).height,1080)
    def test_missing_height(self): self.assertIsNone(normalize_format({'width':1920}).height)
    def test_missing_fps(self): self.assertIsNone(normalize_format({}).fps)
    def test_missing_bitrate(self): self.assertIsNone(normalize_format({}).vbr)
    def test_missing_filesize(self): self.assertIsNone(estimate_size(video()))
    def test_unknown_codec(self):
        self.assertEqual(normalize_format({'vcodec':'newcodec'}).video_codec_family,'OTHER')
        self.assertEqual(normalize_format({'vcodec':None,'ext':'mp4'}).video_codec_family,'UNKNOWN')
    def test_deduplication(self):
        p=video('one');q=video('two',vbr=900)
        options=build_quality_options([p,q,replace(q,width=1900)])
        self.assertEqual(len(options),2);self.assertIn(q,options)
    def test_audio_ranking(self):
        small=audio('small',abr=160,asr=48000,audio_channels=2,filesize=100)
        large=audio('large',abr=64,asr=44100,audio_channels=2,filesize=999999)
        self.assertEqual(select_best_audio([large,small]),small)
    def test_muxed_fallback(self):
        m=normalize_format({'format_id':'mux','vcodec':'h264','acodec':'aac','height':720,'ext':'mp4'})
        self.assertEqual(select_best_combination([video(),m]).muxed,m)
    def test_split(self):
        result=select_best_combination([video(),audio()])
        self.assertEqual(result.mode,'split');self.assertEqual(result.yt_dlp_format_expression,'v+a')
    def test_container(self):
        for v,a,ext in [('H264','AAC','mp4'),('AV1','AAC','mp4'),('VP9','OPUS','mkv'),('AV1','OPUS','mp4')]:
            s=select_best_combination([replace(video(),video_codec_family=v),replace(audio(),audio_codec_family=a)])
            self.assertEqual(s.final_container,ext)
    def test_no_formats(self):
        with self.assertRaises(FormatSelectionError) as e: select_best_combination([])
        self.assertEqual(e.exception.category,'NoFormats')
    def test_malformed(self):
        for bad in (None,0,'unknown',{},[],float('nan'),float('inf'),True,10**5000):
            for key in ('width','height','fps','filesize','tbr','vcodec','acodec','dynamic_range','format_id','language_preference'):
                with self.subTest(bad=bad,key=key): normalize_formats([{key:bad},bad])
    def test_size_precedence(self):
        p=video(tbr=800,duration=10,filesize=100,filesize_approx=200)
        self.assertEqual(estimate_size(p),100)
        self.assertEqual(estimate_size(replace(p,filesize=None)),200)
        self.assertEqual(estimate_size(replace(p,filesize=None,filesize_approx=None)),1000000)
    def test_ranges(self):
        for value in ('SDR','HDR','HDR10','HLG','DV'):
            self.assertEqual(video(dynamic_range=value).dynamic_range,value)
        self.assertIsNone(video().hdr)
        self.assertEqual(video().dynamic_range,'UNKNOWN')
    def test_codec_variants(self):
        for code,family in [('av01','AV1'),('vp09','VP9'),('avc1','H264'),('h264','H264'),('hev1','H265'),('hvc1','H265'),('hevc','H265')]:
            self.assertEqual(normalize_format({'vcodec':code}).video_codec_family,family)
    def test_target(self):
        formats=[video(),video('4k',2160),audio()]
        self.assertEqual(select_quality(formats,1080).video.height,1080)
        self.assertEqual(select_quality(formats,formats[1]).video.height,2160)
        with self.assertRaises(FormatSelectionError): select_quality(formats,4320)
    def test_audio_only(self):
        self.assertEqual(select_quality([audio()],'audio').mode,'audio')
        self.assertEqual(select_quality([audio()],'a').audio.format_id,'a')
    def test_drm_and_storyboard(self):
        self.assertIsNone(select_best_video([video(has_drm=True),normalize_format({'format_id':'sb','vcodec':'images','acodec':'none'})]))
    def test_error_categories(self):
        for formats,category in [([audio()],'NoPlayableVideo'),([video()],'NoPlayableAudio')]:
            with self.assertRaises(FormatSelectionError) as e: select_best_combination(formats)
            self.assertEqual(e.exception.category,category)
    def test_rank_priority(self):
        self.assertEqual(select_best_video([replace(video(),video_codec_family='AV1'),replace(video('4k',2160),video_codec_family='H264')]).height,2160)
        self.assertEqual(select_best_video([video('hdr',dynamic_range='HDR10'),replace(video('sdr',dynamic_range='SDR'),fps=60)]).fps,60)
    def test_callback_native(self):
        opts=pickle.loads(pickle.dumps(build_opts()))
        with yt_dlp.YoutubeDL(opts) as y:
            result=y._select_formats([video().source_format,audio().source_format],y.format_selector)[0]
        self.assertEqual(result['format_id'],'v+a');self.assertEqual(result['ext'],'mp4')
        self.assertEqual(len(result['requested_formats']),2)
    def test_custom_unchanged(self):
        expr='bv[height<=1080]+ba/b'
        self.assertEqual(build_opts({'format':expr})['format'],expr)
        self.assertEqual(build_opts({'format':'ba'})['format'],'ba')
        self.assertEqual(build_opts({'extract_audio':True})['format'].target,'audio')
    def test_selection_builder(self):
        s=select_best_combination([video(),audio()]);opts=build_opts({'format_selection':s})
        self.assertEqual(opts['format'],s.yt_dlp_format_expression)
        self.assertEqual(opts['merge_output_format'],s.final_container)
    def test_private_metadata(self):
        p=video(http_headers={'Cookie':'SECRET'}, extra='SECRET')
        self.assertNotIn('SECRET',repr(p));self.assertNotIn('SECRET',select_best_combination([p,audio()]).reason)
    def test_stable_order(self):
        p,q=video('a'),video('b')
        self.assertEqual(select_best_video([p,q]),select_best_video([q,p]))
    def test_preset_clears_quality(self):
        from services.settings_service import merge_preset
        self.assertNotIn('quality_target',merge_preset({'quality_target':'v'},{'format':'ba'}))
    def test_original_audio_preferred(self):
        original=audio('original',abr=130)
        self.assertEqual(select_best_audio([original,audio('compressed',abr=131,format_note='medium, DRC')]),original)
    def test_damaged_and_upscaled_rejected(self):
        for note in ('AI-upscaled','DAMAGED'):
            self.assertEqual(select_best_video([video(),video('higher',8640,format_note=note)]).height,1080)
    def test_language_preference(self):
        original=audio('original',abr=128,language_preference=10)
        self.assertEqual(select_best_audio([original,audio('dub',abr=256,language_preference=-1)]),original)
    def test_no_invented_options(self):
        options=build_quality_options([video(),audio()])
        self.assertEqual(len(options),1);self.assertEqual(options[0].height,1080)
    def test_container_override_and_no_transcode(self):
        opts=build_opts({'quality_target':'best','merge_output_format':'mkv'})
        self.assertEqual(opts['format'].container,'mkv')
        self.assertFalse(opts.get('postprocessors'))
    def test_identifier_validation(self):
        with self.assertRaises(FormatSelectionError) as e: select_best_combination([video('x/y'),audio()])
        self.assertEqual(e.exception.category,'UnsupportedSelection')
    def test_preview_quality_to_builder(self):
        from PySide6.QtWidgets import QApplication
        from gui.widgets.format_preview import FormatPreviewDialog
        from gui.widgets.settings_panel import SettingsPanel
        app=QApplication.instance() or QApplication([])
        dialog=FormatPreviewDialog({'formats':[video().source_format,audio().source_format]})
        dialog._table.selectRow(0);dialog._on_use()
        self.assertEqual(dialog.selected_format,'v')
        self.assertIn('1080P',dialog.selected_label)
        panel=SettingsPanel();panel.format_combo.addItem(dialog.selected_label,dialog.selected_format)
        panel.format_combo.setCurrentIndex(panel.format_combo.count()-1)
        opts=build_opts(panel.collect_opts());self.assertEqual(opts['format'].target,'v')
        panel.format_combo.setEditText('bv+ba')
        self.assertEqual(build_opts(panel.collect_opts())['format'],'bv+ba')
        dialog.close();panel.close()

if __name__=='__main__': unittest.main()
