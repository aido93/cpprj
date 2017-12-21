import json
import os
import sys
import magic
from os.path import join, split
import subprocess

config={}
with open(sys.argv[1], 'r') as fr:
    config=json.load(fr)

os.makedirs(config['dir'], exist_ok=False)
os.copyfile(join('lic',config['lic']), join(config['dir'], 'LICENSE'))
os.makedirs(join(config['dir'], 'include'), exist_ok=False)
os.makedirs(join(config['dir'], 'src'), exist_ok=False)
deps_path=join(config['dir'], '..', 'deps', 'src')
os.makedirs(deps_path, exist_ok=False)
if config['test_dir']!='':
    os.makedirs(join(config['dir'], config['test_dir']), exist_ok=False)

readme='#'+split(config['dir'])[-1]+' '+config['version']+'\n\n'+config['desc']+'\n'
readme+='## Dependencies:'
for d in config['dependencies']:
    for a in d:
        name=a.split('/')
        name=[v for v in name if v]
        readme+='['+name[-1]+']('+a+')'
readme+='Please contact us:\n*'+config['maintainer_url']+'\n*'+config['maintainer_email']
with open('README.md', 'w') as fw:

os.chdir(deps_path)
archives=[]
dirs={}
aa=[]
for d in config['dependencies']:
    for a in d:
        command=''
        if d=='git':
            command='clone'
        elif d=='svn':
            command='checkout'
        elif d=='wget':
            command='-c'
            archives.append(a.split('/')[-1])
        ps = subprocess.Popen((d, command, a['url']), stdout=subprocess.PIPE)
        ps.wait()
        output = ps.stdout.read()
        print(output+'\n')
        bb=aa
        aa=os.listdir('.')
        dirs[list(set(aa)-set(bb))[0]]=a['build']
print('All dependencies are loaded\n')

for a in archives:
    t=magic.from_file(a, mime=True).split('/')[-1]
    if t=='x-xz' or t=='x-bzip2' or t=='gzip':
        ps = subprocess.Popen(('tar', 'xf', a), stdout=subprocess.PIPE)
        ps.wait()
        output = ps.stdout.read()
        print(output+'\n')
        os.remove(a)
print('All dependencies are unpacked\n')

os.chdir('..')
os.makedirs('include', exist_ok=False)
os.makedirs('lib', exist_ok=False)
os.chdir('src')
for d, build in dirs.items():
    os.chdir(d)
    ps = subprocess.Popen((build), stdout=subprocess.PIPE)
    ps.wait()
    output = ps.stdout.read()
    print(output+'\n')
    os.chdir('..')
