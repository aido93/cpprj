import re

class field:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    type=''
    name=''
    bits=0
    value=''

#def get_all_structs(text):

def gen_struct(name, fields, ts=4*' '):
    text=[]
    for f in fields:
        if f.bits==0:
            if f.value=='':
                text.append(f.type+' '+f.name)
            else:
                text.append(f.type+' '+f.name+' = '+f.value)
        elif f.bits==1:
            if f.value=='':
                text.append('unsigned '+f.name+': 1')
            else:
                text.append('unsigned '+f.name+': 1 = '+f.value)
        else:
            if f.value=='':
                text.append(f.type+' '+f.name+': '+str(bits))
            else:
                text.append(f.type+' '+f.name+': '+str(bits)+' = '+f.value)
    return 'struct '+name+'\n{\n'+ts+(';///> \n'+ts).join(text)+';///> \n};\n'

def flags(name, line):
    fields=line.split(' ')
    ff=[]
    for f in fields:
        if '=' in f:
            name, val=f.split('=')
        else:
            name=f
            val=''
        ff.append(field(bits=1, name=name, value=val))
    return gen_struct(name, ff)
