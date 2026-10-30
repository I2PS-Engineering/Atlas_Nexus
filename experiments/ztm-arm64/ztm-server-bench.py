#!/usr/bin/env python3
"""ZTM Special Ops ARM64 server experimental benchmark adapter (non-qualifying)."""
import argparse, datetime, json, os, pathlib, platform, re, shutil, subprocess, sys

def main():
    p=argparse.ArgumentParser(description='ZTM ARM64 terminal-only offline RandomX benchmark (experimental)')
    p.add_argument('--hashes', choices=['1M','10M'], default='1M')
    p.add_argument('--threads',type=int,default=None,help='XMRig benchmark threads (default: XMRig auto)')
    p.add_argument('--xmrig',default='xmrig')
    p.add_argument('--output',default=str(pathlib.Path.home()/'ztm-arm64-benchmark-results'))
    p.add_argument('--yes',action='store_true',help='Authorize CPU load and electricity use')
    a=p.parse_args()
    if platform.system()!='Linux' or platform.machine().lower() not in ('aarch64','arm64'):
        p.error('This experimental package requires Linux ARM64')
    if a.threads is not None and not 1<=a.threads<=(os.cpu_count() or 1):
        p.error('Thread count exceeds visible logical CPUs')
    exe=shutil.which(a.xmrig) if '/' not in a.xmrig else a.xmrig
    if not exe or not os.access(exe,os.X_OK):p.error('XMRig executable not found; install it first')
    if os.geteuid()==0:p.error('Run as normal user, not root')
    if not a.yes:
        print('This offline benchmark uses CPU power and electricity; no pool mining or wallet transfers.')
        if input('Type YES to start: ').strip()!='YES':return 2
    out=pathlib.Path(a.output).expanduser();out.mkdir(parents=True,exist_ok=True)
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    cmd=[exe,'--bench='+a.hashes]
    if a.threads:cmd.extend(['--threads',str(a.threads)])
    log=out/(stamp+'.log'); report=out/(stamp+'.json')
    print('Running:', ' '.join(cmd));print('Log:',log)
    with log.open('w',encoding='utf-8') as f:
        proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace',bufsize=1)
        try:
            for line in proc.stdout:
                print(line,end='',flush=True);f.write(line);f.flush()
            code=proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
            code=130
    raw=log.read_text(errors='replace')
    def matches(pattern):return re.findall(pattern,raw,re.I)
    dataset=matches(r'allocated\s+2336\s+MB[^\n]*huge pages\s+(\d+%)\s+(\d+/\d+)')
    scratch=matches(r'READY threads\s+(\d+/\d+)[^\n]*huge pages\s+(\d+%)\s+(\d+/\d+)')
    result=matches(r'benchmark finished in\s+([\d.]+)\s+seconds\s+\(([\d.]+)\s+h/s\)')
    data={'type':'experimental-offline-benchmark','qualifies_24h_baseline':False,'unlocks_personal_mining':False,'created_utc':stamp,'platform':platform.platform(),'logical_cpus':os.cpu_count(),'command':cmd,'exit_code':code,'dataset_hugepages':dataset[-1] if dataset else None,'scratchpad_hugepages':scratch[-1] if scratch else None,'final_seconds_and_hashrate':result[-1] if result else None,'log':str(log)}
    report.write_text(json.dumps(data,indent=2)+'\n');print('\nReport:',report)
    return code
if __name__=='__main__':sys.exit(main())
