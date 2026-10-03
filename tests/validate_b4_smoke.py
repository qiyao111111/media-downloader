"""Fresh-download smoke test of the final release artifact."""
import json
import os
import subprocess
import sys
from pathlib import Path

exe,out,mode=(Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3])
out.mkdir(parents=True,exist_ok=True)
url='https://www.youtube.com/watch?v=E86EwGT_c2M'
manifest={'evidence':str(out),'download_directory':r'D:\下载测试\YouTube视频\B4下载验证',
          'cases':[{'name':'final-'+mode+'-1080','url':url,'target':1080},
                   {'name':'final-'+mode+'-8k','url':url,'metadata_only':True}]}
file=out/'acceptance.json';file.write_text(json.dumps(manifest))
env=dict(os.environ);windows=os.environ['SystemRoot'];env['PATH']=windows+'\\System32;'+windows
for key in ('PYTHONPATH','QT_PLUGIN_PATH','QML2_IMPORT_PATH'):env.pop(key,None)
subprocess.run([str(exe),'--validate-release',str(file)],env=env,check=True,timeout=300)
print('Final artifact smoke PASS',flush=True)
