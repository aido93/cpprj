import re

class enum_t:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    is_class=False
    elements=[]

def get_all_enums(text):
    t=re.findall('enum\s+(class)?\s*(\w+)(?:[\s\n]*)\{\s*(.*?)\}\s*;', text.replace('\n',''))
    ret={}
    for en in t:
        elements=re.sub('\s+', '', en[-1]).split(',')
        if en[0]=='class':
            ret[en[1]]=enum_t(is_class=True,  elements=elements)
        else:
            if en[1]!='':
                ret[en[1]]=enum_t(is_class=False, elements=elements)
            else:
                if '' not in ret:
                    ret['']=elements
                else:
                    ret[''].extend(elements)
    return ret

def enum(name, elements, upper=False, is_class=True, ts=' '*4):
    elements=re.sub('\s+',' ', elements)
    elements=elements.split(' ')
    if upper:
        a=(s.upper() for s in elements)
    else:
        a=elements
    els=(',\n'+ts).join(a)
    if is_class:
        return 'enum class '+name+'\n{\n'+ts+els+'\n};\n'
    else:
        return 'enum '+name+'\n{\n'+ts+els+'\n};\n'

def switch(enums, enum_name, var_name, ts=' '*4):
    e=enums[enum_name]
    body=''
    if enum_name=='':
        for v in e:
            if '=' in v:
                name=v.split('=')[0]
            else:
                name=v
            body=body+'case '+name+':\n'+ts+'{\n'+ts*2+'\n'+ts*2+'break;\n'+ts+'}\n'
    else:
        prefix=''
        if e.is_class:
            prefix=enum_name+'::'
        for v in e.elements:
            if '=' in v:
                name=v.split('=')[0]
            else:
                name=v
            body=body+'case '+prefix+name+':\n'+ts+'{\n'+ts*2+'\n'+ts*2+'break;\n'+ts+'}\n'+ts
    return 'switch ('+var_name+')\n{\n'+ts+body+'default:\n'+ts+'{\n'+ts*2+'\n'+ts+'}\n}\n'


