"""Explicit local acceptance runner; exercises the same frozen GUI and Manager."""
import json
import multiprocessing
import time
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication,QMessageBox
from PySide6.QtGui import QIcon
from app.paths import PATHS
from core.runtime_manager import health
from core.ffmpeg_utils import validate_media
from core.credentials import redact
from gui.main_window import MainWindow


def run(manifest_path):
    spec=json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    out=Path(spec['evidence']);out.mkdir(parents=True,exist_ok=True)
    app=QApplication([]);app.setWindowIcon(QIcon(str(PATHS.resources_dir/'app.ico')))
    w=MainWindow();w.show();results=[];states={};index=[-1];task=[None];last=[time.monotonic()];gap=[0.0]
    from gui.theme_manager import apply_theme
    apply_theme(app,w._settings.get('theme','system'))
    # Acceptance automation chooses Yes; ordinary close retains the real question.
    original_question=QMessageBox.question;QMessageBox.question=lambda *args,**kwargs:QMessageBox.Yes
    cases=spec.get('cases',[]);d=w._downloader;p=w._settings_panel
    collect=p.collect_opts
    def acceptance_inputs():
        inputs=collect()
        if index[0]>=0:
            for key in ('http_headers','js_runtimes'):
                if key in cases[index[0]].get('options',{}):inputs[key]=cases[index[0]]['options'][key]
        return inputs
    p.collect_opts=acceptance_inputs
    w._manager.configure_workers(1)
    Path(spec['download_directory']).mkdir(parents=True,exist_ok=True)
    if spec.get('product_checks'):
        from app.product_validation import startup
        startup(w,out/'product-startup',spec['download_directory'])
    p.path_edit.setText(spec['download_directory'])
    p.workers_spin.setValue(1);p.retries_spin.setValue(7);w._save_settings()
    def save():
        (out/'results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf-8')
    def next_case():
        index[0]+=1;task[0]=None
        if index[0]>=len(cases):w.close();return
        case=cases[index[0]];folder=Path(spec['download_directory']);folder.mkdir(parents=True,exist_ok=True)
        p.apply_settings({'download_path':str(folder),'outtmpl':case['name']+'_%(id)s.%(ext)s','format':'','cookiesfrombrowser':'None',
                          'cookiefile':'','proxy':'','embed_metadata':False,'embed_chapters':False,**case.get('options',{})})
        d.path.setText(str(folder));d.urls._text_edit.setPlainText(case['url']);w._on_list_formats()
    def ready(url,info):
        case=cases[index[0]];target=case.get('target','best')
        if not d.info:return
        if target=='audio':d.audio_only.setChecked(True);d.audio_format.setCurrentIndex(d.audio_format.findData(case.get('audio_format','best')))
        elif isinstance(target,int):
            profile=w._manager.selection(info,target).video
            for i in range(1,d.quality.count()):
                if d.quality.itemData(i).format_id==profile.format_id:d.quality.setCurrentIndex(i);break
        row={'name':case['name'],'formats':len(info.get('formats') or []),'selection':d.selection.yt_dlp_format_expression if d.selection else 'custom',
             'height':(d.selection.video or d.selection.muxed).height if d.selection and (d.selection.video or d.selection.muxed) else None,
             'labels':[d.quality.itemText(i) for i in range(d.quality.count())]}
        if spec.get('product_checks'):
            from app.product_validation import capture
            row['product_ui']=capture(w,out/(case['name']+'-ui'))
            selected=(d.selection.video or d.selection.muxed or d.selection.audio) if d.selection else None
            row.update(fps=selected.fps if selected else None,dynamic_range=selected.dynamic_range if selected else None)
        if case.get('metadata_only'):
            row['status']='metadata-pass';results.append(row);save();QTimer.singleShot(0,next_case);return
        expected=d.selection;d.download.click();task[0]=w._manager.get_all_tasks()[-1];assert task[0].selection==expected
        task[0]._acceptance=row
    def failed(url,error):
        results.append({'name':cases[index[0]]['name'],'status':'preview-failed','error':redact(error[1] if isinstance(error,tuple) else error)})
        save()
        if hasattr(w,'_error_dialog'):w._error_dialog.reject()
        QTimer.singleShot(0,next_case)
    def event(record):
        states.setdefault(record['id'],[]).append(str(record['status']))
        if spec.get('product_checks') and record['status'] in ('downloading','postprocessing','completed','cancelled'):
            shot=out/('state-'+str(record['status'])+'.png')
            if not shot.is_file():
                w.navigation.setCurrentRow(1);w.grab().save(str(shot))
        if task[0] and record['id']==task[0].id:
            case=cases[index[0]]
            row=task[0]._acceptance
            if record.get('downloaded_bytes',0)>0:row.setdefault('resume_first_bytes' if row.get('retried') else 'first_bytes',record['downloaded_bytes'])
            if case.get('cancel') and not row.get('retried') and record.get('downloaded_bytes',0)>1024**2:w._manager.cancel_task(task[0].id)
            if case.get('exit_active') and record.get('downloaded_bytes',0)>1024**2:QTimer.singleShot(0,w.close)
    def tick():
        now=time.monotonic();gap[0]=max(gap[0],now-last[0]);last[0]=now
        if spec.get('navigate'):w.navigation.setCurrentRow(int(now*3)%5);w.move(40+int(now)%3,40)
        if not task[0] or not task[0].status.terminal:return
        t=task[0];row=t._acceptance;row.update(status=t.status.value,error=redact(t.error) if t.error else '',outputs=t.output_files,states=states.get(t.id,[]))
        if t.status.value=='cancelled' and cases[index[0]].get('retry') and not row.get('retried'):
            row['retried']=True;w._task_table._on_retry(t.id);task[0]=w._manager.get_all_tasks()[-1];task[0]._acceptance=row;return
        if t.output_files:
            probe=validate_media(t.output_files[0]);(out/(row['name']+'-ffprobe.json')).write_text(json.dumps(probe,indent=2),encoding='utf-8')
        results.append(row);save();task[0]=None
        if hasattr(w,'_error_dialog'):w._error_dialog.reject()
        QTimer.singleShot(0,next_case)
    w._bridge.info_extracted.connect(ready);w._bridge.preview_failed.connect(failed)
    w._bridge.task_updated.connect(event);w._bridge.task_progress.connect(event)
    timer=QTimer();timer.timeout.connect(tick);timer.start(25)
    QTimer.singleShot(0,next_case);QTimer.singleShot(spec.get('timeout_ms',1800000),w.close)
    last[0]=time.monotonic();app.exec();timer.stop();w._manager.shutdown(wait=True);QMessageBox.question=original_question
    if task[0] and cases[index[0]].get('exit_active'):
        row=task[0]._acceptance;row.update(status=task[0].status.value,active_exit=True);results.append(row);save()
    summary={'health':health(download_dir=spec['download_directory']),'paths':{k:str(v) for k,v in vars(PATHS).items()},
             'children':len(multiprocessing.active_children()),'max_tick_gap':gap[0],'cases':len(results),'history':len(w._history.list_records())}
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return 0 if len(results)==len(cases) and all(r['status'] in ('completed','metadata-pass','cancelled') for r in results) and summary['children']==0 else 1
