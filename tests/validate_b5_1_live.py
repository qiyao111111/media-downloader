import sys,json,multiprocessing,time
from pathlib import Path
from unittest.mock import patch
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
if __name__=='__main__':
    multiprocessing.freeze_support()
    from configs.app_settings import AppSettings
    from services.history_service import HistoryService
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from gui.main_window import MainWindow
    from gui.theme_manager import apply_theme
    from gui.product_dialogs import ProductDialog
    from gui.widgets.presentation import QualityChip
    from app import release_validation as rv
    out=root/'docs/evidence/b5_1/live';out.mkdir(parents=True,exist_ok=True)
    shots=root/'docs/screenshots/b5_1';shots.mkdir(parents=True,exist_ok=True)
    downloads=root/'temp/b51 final downloads';downloads.mkdir(parents=True,exist_ok=True)
    settings=AppSettings(str(root/'temp/b51-profile/settings.json'));settings.update_from({'onboarding_complete':True,'theme':'light','language':'en','download_path':str(downloads),'ffmpeg_location':str(root/'bin')})
    history=HistoryService(str(root/'temp/b51-profile/history.json'))
    url='https://www.youtube.com/watch?v=E86EwGT_c2M'
    cases=[{'name':'1080','url':url,'target':1080},{'name':'4k','url':url,'target':2160,'metadata_only':True},
           {'name':'8k','url':url,'metadata_only':True},{'name':'8k60-hdr','url':'https://www.youtube.com/watch?v=hVvEISFw9w0','metadata_only':True},
           {'name':'audio','url':url,'target':'audio','audio_format':'mp3'},
           {'name':'cancel-retry','url':url,'target':1080,'retry':True}]
    run_id=time.time_ns()
    for case in cases:case.setdefault('options',{})['outtmpl']=str(run_id)+'_'+case['name']+'_%(id)s.%(ext)s'
    spec={'evidence':str(out),'download_directory':str(downloads),'cases':cases,'timeout_ms':900000}
    specfile=root/'build/b51-live.json';specfile.write_text(json.dumps(spec),encoding='utf-8')
    metadata=[];seen=set();analysis=[0]
    def factory():
        w=MainWindow();w.resize(1366,900);w.show();app=QApplication.instance();d=w._downloader;t=w._task_table
        def grab(name,page=None):
            if page is not None:w.navigation.setCurrentRow(page)
            app.processEvents();w.grab().save(str(shots/(name+'.png')))
        def startup():
            for theme in ('light','dark'):
                apply_theme(app,theme);grab('downloader-'+theme,0)
            apply_theme(app,'light')
            for cat,name in [(0,'general'),(4,'runtime'),(2,'cookies')]:
                w._settings_panel.categories.setCurrentRow(cat);grab('settings-'+name,3)
            dialog=ProductDialog(w);dialog.show();app.processEvents();dialog.grab().save(str(shots/'about.png'));dialog.reject();w.navigation.setCurrentRow(0)
        QTimer.singleShot(250,startup)
        def analyzed(url,info):
            index=analysis[0];analysis[0]+=1;best=d.selection;profile=(best.video or best.muxed) if best else None
            row={'name':cases[index]['name'],'url':url,'title':info.get('title'),'uploader':info.get('uploader'),'duration':info.get('duration'),
                 'formats':len(info.get('formats') or []),'height':profile.height if profile else None,'fps':profile.fps if profile else None,
                 'dynamic_range':profile.dynamic_range if profile else None,'chips':[c.text() for c in d.findChildren(QualityChip)],'selection':best.yt_dlp_format_expression if best else None}
            metadata.append(row);(out/'metadata.json').write_text(json.dumps(metadata,indent=2,ensure_ascii=False),encoding='utf-8')
            grab('analyze-'+row['name'],0)
            if row['name']=='1080':
                def later():
                    row['thumbnail_loaded']=bool(d.thumbnail.pixmap() and not d.thumbnail.pixmap().isNull())
                    for theme in ('light','dark'):
                        apply_theme(app,theme);grab('downloader-analyzed-'+theme,0)
                    apply_theme(app,'light');(out/'metadata.json').write_text(json.dumps(metadata,indent=2,ensure_ascii=False),encoding='utf-8')
                QTimer.singleShot(2500,later)
            if row['name']=='8k60-hdr':assert profile.height==4320 and profile.fps==60 and profile.dynamic_range=='HDR10'
        w._bridge.info_extracted.connect(analyzed)
        original_retry=t._on_retry;retrying=[False]
        def retry_button(tid):
            if retrying[0]:return original_retry(tid)
            retrying[0]=True
            try:
                grab('queue-cancelled',1);button=t._table.cellWidget(t._row_map[tid],6);assert button.isEnabled();button.click()
            finally:retrying[0]=False
        t._on_retry=retry_button
        def event(record):
            task=next((item for item in w._manager.get_all_tasks() if item.id==record['id']),None)
            row=getattr(task,'_acceptance',{})
            state=str(record['status'])
            if row.get('name')=='1080' and state in ('downloading','postprocessing','completed') and state not in seen:
                if state!='downloading' or record.get('downloaded_bytes',0)>1024**2:
                    seen.add(state);grab('queue-'+state,1)
                    if state=='completed':
                        button=t._table.cellWidget(t._row_map[task.id],6);assert button.isEnabled();button.click();row['open_folder_clicked']=True
                        grab('history',2);grab('logs',4)
            if row.get('name')=='cancel-retry' and state=='downloading' and record.get('downloaded_bytes',0)>1024**2 and not row.get('cancel_clicked'):
                row['cancel_clicked']=True;grab('queue-before-cancel',1);t._table.cellWidget(t._row_map[task.id],6).click()
        w._bridge.task_updated.connect(event);w._bridge.task_progress.connect(event)
        return w
    with patch('gui.main_window.AppSettings',return_value=settings),patch('gui.main_window.DownloadHistory',return_value=history),patch.object(rv,'MainWindow',factory):
        code=rv.run(specfile)
    print('exit',code,flush=True);sys.exit(code)
