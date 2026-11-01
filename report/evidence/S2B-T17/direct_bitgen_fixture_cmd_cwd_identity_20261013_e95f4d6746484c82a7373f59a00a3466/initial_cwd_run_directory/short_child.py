import json,os,pathlib,sys,time
time.sleep(0.6)
pathlib.Path(sys.argv[1]).write_text(json.dumps({'cwd':os.getcwd(),'pid':os.getpid(),'ppid':os.getppid()}),encoding='utf-8')
