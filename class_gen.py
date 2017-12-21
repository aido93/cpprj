import time
import os
import re
import json
from itertools import groupby
from decor import to_snake, to_camel
from functions import arg, method, create_comments
from header_detection import subtypes_autodetection

not_cpp_post_mod       = ['=delete', '=0', '=default']
post_class_modifiers   = ['final', ]
generic_types          = [  'char', 'unsigned char', 'bool', 'short', 'unsigned short', 'int', 'unsigned int', 'long', 'unsigned long', 'float', 'double', 'long long',
                            'int8_t', 'uint8_t', 'int16_t', 'uint16_t', 'int32_t', 'uint32_t', 'int64_t', 'uint64_t']
class parent:
    type           = 'public'
    name           = ''
    template_types = []
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __str__(self):
        return self.type+' '+self.name+' <'+str(self.template_types)+'>'

def fields(line):
    line=line.replace('\n','')
    line=line.replace(';','; ')
    line=re.sub('\s+',' ', line)
    args=line.split('; ')
    ret=[]
    for a in args:
        p=a.split(' ')
        kv=p[-1].split('=')
        pm=None
        if 'static' in p:
            pm='static'
            p.remove('static')
        t=' '.join(p[:-1])
        if len(kv)==1:
            ret.append(arg(pre_modifier=pm, type=t, name=kv[0]))
        elif len(kv)==2:
            ret.append(arg(pre_modifier=pm, type=t, name=kv[0], value=kv[1]))
    del ret[-1]
    return ret

def add_sg(var, setters, getters, snake_case):
    sgetters=[]
    for v in var:
        if not snake_case:
            setter=to_camel("set_"+v.name)
            getter=to_camel("get_"+v.name)
        else:
            setter=to_snake("set_"+v.name)
            getter=to_snake("get_"+v.name)
        if getters:
            sgetters.append(method( return_type=v.type,
                                    name=getter,
                                    args=None,
                                    post_modifier="const",
                                    body="return "+v.name+";",
                                    hint='getter'))
        if setters:
            t=v.type
            if v.pre_modifier!='const': 
                 pm=None
                 if t.find('static ')!=-1:
                     t=t.replace('static ','')
                     pm='static'
            if t in generic_types or '*':
                args=[arg(type=t, name='_'+v.name), ]
            elif '*' in t:
                args=[arg(type=t, name='_'+v.name), ]
            else:
                args=[arg(pre_modifier="const ", type=t+'&', name='_'+v.name), ]
            sgetters.append(method( return_type='void',
                                    name=setter,
                                    args=args,
                                    pre_modifier=pm,
                                    post_modifier=None,
                                    body=v.name+" = _"+v.name+";",
                                    hint='setter'))
    return sgetters


class class_:
    template_types     = []
    parents            = []
    del_comments       = False
    name               = ''
    post_modifier      = ''

    public_methods     = []
    public_comments    = []

    protected_methods  = []
    protected_comments = []
    
    private_methods    = []
    private_comments   = []
    
    protected_fields   = []
    private_fields     = []
    set                = []
    get                = []
    snake_case         = True
    gen_test           = True
    pre_class          = ''
    post_class_hpp     = ''
    post_class_cpp     = ''
    
    def __init__(self, **kwargs):
        self.public_methods=[]
        self.protected_methods=[]
        self.private_methods=[]
        self.__dict__.update(kwargs)
        if 'template_types' in kwargs:
            self.template_types=[]
            if isinstance(kwargs['template_types'], str):
                self.template_types=kwargs['template_types'].split(' ')
        if 'parents' in kwargs:
            if isinstance(kwargs['parents'], str):
                s=kwargs['parents'].split(',')
                self.parents=[]
                for d in s:
                    self.parents.append(parent(name=d))
        if 'private_fields' in kwargs:
            if isinstance(kwargs['private_fields'], str):
                self.private_fields=fields(kwargs['private_fields'])
        if 'protected_fields' in kwargs:
            if isinstance(kwargs['protected_fields'], str):
                self.protected_fields=fields(kwargs['protected_fields'])
        ss=False
        gg=False
        if 'private' in self.set:
            ss=True
        if 'private' in self.get:
            gg=True
        self.public_methods.extend(add_sg(self.private_fields, ss, gg, self.snake_case))
        if 'protected' in self.set:
            ss=True
        if 'protected' in self.get:
            gg=True
        self.public_methods.extend(add_sg(self.protected_fields, ss, gg, self.snake_case))
        templated_class=self.name
        if self.template_types:
            templated_class=templated_class+'<'+', '.join(self.template_types)+'>'
        for m in self.public_methods:
            m.class_name=templated_class
        for m in self.protected_methods:
            m.class_name=templated_class
        for m in self.private_methods:
            m.class_name=templated_class
        if not self.del_comments:
            self.comment_methods()

    def comment_methods(self):
        self.public_comments    = create_comments(self.public_methods)
        self.protected_comments = create_comments(self.protected_methods)
        self.private_comments   = create_comments(self.private_methods)
        
    def uncomment_methods(self):
        self.public_comments    = []
        self.protected_comments = []
        self.private_comments   = []

    # vd=0 - not virtual
    # vd=1 - virtual
    # vd=2 - pure virtual
    # vd=3 - virtual protected
    # Constructors:
    # dd=0 - custom constructor (delete default)
    # dd=1 - deleted constructor
    # dd=2 - default constructor
    def basic_class_content(self, dd=0, dc=0, dm=0, vd=0, custom=None):
        templated_class=self.name
        if self.template_types and  isinstance(self.template_types,list):
            templated_class=templated_class+'<'+', '.join(self.template_types)+'>'
        
        default=method(name=self.name)
        if dd==0:
            default.post_modifier="noexcept"
        elif dd==1:
            default.post_modifier="=delete"
        elif dd==2:
            default.post_modifier="=default"
        self.public_methods.append(default)

        op=method(return_type=templated_class, name="operator=", hint='copy', args=[arg(pre_modifier='const', type=self.name+"&"),])
        copyc=method(name=self.name, hint='copy', args=[arg(pre_modifier="const", type=self.name+"&"),])
        if dc==0:
            copyc.post_modifier="noexcept"
            op.post_modifier="noexcept"
        elif dc==1:
            copyc.post_modifier="=delete"
            op.post_modifier="=delete"
        elif dc==2:
            copyc.post_modifier="=default"
            op.post_modifier="=default"
        self.public_methods.append(op)
        self.public_methods.append(copyc)

        mop=method(return_type=templated_class+'&', name="operator=", hint='move', args=[arg(pre_modifier='const', type=self.name+"&&"),])
        movec=method(name=self.name, hint='move', args=[arg(pre_modifier="const", type=self.name+"&&"),])
        if dm==0:
            movec.post_modifier="noexcept"
            mop.post_modifier="noexcept"
        elif dm==1:
            movec.post_modifier="=delete"
            mop.post_modifier="=delete"
        elif dm==2:
            movec.post_modifier="=default"
            mop.post_modifier="=default"
        self.public_methods.append(mop)
        self.public_methods.append(movec)
    
        if custom:
            for constructor_params in custom:
                self.public_methods.append(method(name=self.name, args=constructor_params, class_name=self.name))
        if   vd==0:
            self.public_methods.append(method(name='~'+self.name))
        elif vd==1:
            self.public_methods.append(method(pre_modifier='virtual', name='~'+self.name))
        elif vd==2:
            self.public_methods.append(method(pre_modifier='virtual', name='~'+self.name, post_modifier='=0'))
        elif vd==3:
            self.protected_methods.append(method(name='~'+self.name, pre_modifier='virtual'))
        for m in self.public_methods:
            m.class_name=templated_class
        for m in self.protected_methods:
            m.class_name=templated_class


    def decl(self, ts=' '*4):
        ret=''
        if self.pre_class and isinstance(self.pre_class, str):
            ret+=self.pre_class
        if self.template_types:
            ret+='template <class '+', class '.join(self.template_types)+'>\n'
        ret+="class "+self.name
        if self.parents:
            ret+=' : '
            i=1
            for p in self.parents:
                ret+=(p.type+' '+p.name)
                if p.template_types:
                    ret+=('<'+', '.join(p.template_types)+'>')
                if i<len(self.parents):
                    ret+=', '
                i=i+1
        if self.post_modifier:
            ret+=self.post_modifier
        ret+='\n{\n'+ts+'public:\n'+ts*2
        if self.public_methods:
            i=1
            for p in self.public_methods:
                if self.public_comments and i in self.public_comments:
                    ret+=self.public_comments[i].replace('\n','\n'+ts*2)
                ret+=(p.decl().replace('\n','\n'+ts*2)+'\n'+ts*2)
                ret+=('\n'+2*ts)
                i=i+1
        if self.protected_methods or self.protected_fields:
            ret+=('\n'+ts+'protected:\n'+ts*2)
            if self.protected_methods:
                i=1
                for p in self.protected_methods:
                    if self.protected_comments and i in self.protected_comments:
                        ret+=self.protected_comments[i].replace('\n','\n'+ts*2)
                    ret+=(p.decl().replace('\n','\n'+ts*2)+'\n'+ts*2)
                    ret+=('\n'+ts*2)
                    i=i+1
            if self.protected_fields:
                max_len=0
                for p in self.protected_fields:
                    max_len=max(max_len, len(str(p)))
                for p in self.protected_fields:
                    ret+=(str(p)+';'+' '*(max_len-len(str(p))+1)+'//!< \n'+ts*2)
        ret+=('\n'+ts+'private:\n'+ts*2)
        if self.private_methods:
            i=1
            for p in self.private_methods:
                if self.private_comments and i in self.private_comments:
                    ret+=self.private_comments[i].replace('\n','\n'+ts*2)
                i=i+1
                ret+=(p.decl().replace('\n','\n'+ts*2)+'\n'+ts*2)
                ret+=('\n'+ts*2)
        if self.private_fields:
            max_len=0
            for p in self.private_fields:
                max_len=max(max_len, len(str(p)))
            for p in self.private_fields:
                ret+=(str(p)+';'+' '*(max_len-len(str(p))+1)+'//!< \n'+ts*2)
        ret+='\n};\n'
        if self.post_class_hpp and isinstance(self.post_class_hpp, str):
            ret+=self.post_class_hpp
        return ret
    
    def impl(self, ts=' '*4):
        spp=''
        cpp=''
        cppt=''
        methods=self.public_methods+self.protected_methods+self.private_methods
        class_fields=self.private_fields+self.protected_fields
        templated_class=self.name
        if self.template_types:
            templated_class=templated_class+'<'+', '.join(self.template_types)+'>'
        for v in class_fields:
            if v.pre_modifier=='static':
                if self.template_types and  isinstance(self.template_types,list):
                    spp+="template <class "+', class '.join(self.template_types)+'>\n'
                spp+=('static '+v.type+' '+templated_class+'::'+v.name+';\n')
        for v in methods:
            if v.pre_modifier=='static':
                if self.template_types and  isinstance(self.template_types,list):
                    spp+="template <class "+', class '.join(self.template_types)+'>\n'
                spp+=v.impl()+'\n'
        for m in methods:
            if m.hint=='setter' or m.hint=='getter' or m.pre_modifier=='static':
                continue
            if (m.post_modifier and m.post_modifier not in not_cpp_post_mod) or not m.post_modifier:
                is_template=False
                a=''
                if self.template_types and  isinstance(self.template_types,list):
                    a="template <class "+', class '.join(self.template_types)+'>\n'
                if m.template_args:
                    is_template=True
                    cppt+=a
                    cppt+=(m.impl(class_fields=class_fields)+'\n\n')
                else:
                    cpp+=a
                    cpp+=(m.impl(class_fields=class_fields)+'\n\n')
        if self.template_types and  isinstance(self.template_types,list):
            cppt=cppt+cpp
            cpp=''
        else:
            cpp=spp+cpp
            spp=''
        return (spp, cpp+self.post_class_cpp, cppt)
    
    def autodetect (self):
        types=[]
        f=self.private_fields + self.protected_fields
        for v in f:
            types.append(v.type)
        m=self.private_methods + self.protected_methods + self.public_methods
        autodetected=[]
        for v in m:
            autodetected.extend(v.autodetected)
        autodetected.extend(subtypes_autodetection(types))
        headers = [el for el, _ in groupby(sorted(autodetected))]
        return headers
    
    def save(self, namespace, directory, user, email, tester_name=None, tester_email=None):
        b=self.decl()
        impl=self.impl()
        if self.template_types:
            b+=('\n#include "'+self.name+'_impl.hpp"')
        elif impl[2]:
            b+=('\n'+impl[2])
        a=namespace(namespace, b)
        a=includes(None, c.autodetect(), None)+a
        a=header(self.name, user, email)+a
        f = open(os.path.join(directory, 'include', self.name+'.hpp'), 'w')
        f.write(a)
        f.close()
        if not self.template_types:
            f = open(os.path.join(directory, 'src', self.name+'.cpp'), 'w')
            f.write(impl[0]+impl[1])
            f.close()
        if self.test==True:
            ts=' '*4
            f = open(os.path.join(directory, 'test', self.name+'.cpp'), 'w')
            tester='#include "'+self.name+'.hpp'+'"\n'
            tester+='#include <iostream>\n\n'
            tester+='using namespace std;\n\n'
            tester+='int main(int argc, char** argv)\n{\n'+ts
            constructors=[c for c in self.public_methods if c.name==self.name]
            i=1
            # Test all constructors
            dyns=[]
            for c in constructors:
                if c.post_modifier!='=delete':
                    tester+=c.name+' test'+str(i)
                    if c.args and c.args.type!=self.name+"&" and c.args.type!=self.name+"&&":
                        tester+=('('+str(c.args)+')')
                        dyns.append(c.args)
                    tester+=(';\n'+ts)
                    i=i+1
            i=1
            for d in dyns:
                tester+=self.name+'* dyn_test'+str(i)+' = new '+self.name
                if d and d.type!=self.name+"&" and d.type!=self.name+"&&":
                    tester+=('('+str(d)+')')
                tester+=(';\n'+ts)
                i=i+1
            tester+='\n'+ts
            i=1
            for d in dyns:
                tester+='delete dyn_test'+str(i)
                tester+=(';\n'+ts)
                i=i+1
            
            tester+='\nreturn 0;\n}\n'
            if not tester_name:
                f.write(header(self.name, user, email)+tester)
            else:
                f.write(header(self.name, tester_name, tester_email)+tester)
            f.close()
        else:
            f = open(os.path.join(directory, 'include', self.name+'_impl.hpp'), 'w')
            f.write(impl[2]+'\n'+self.post_class_cpp)
            f.close()

def virtuals(line):
    l=funcs(line)
    for func in l:
        func.pre_modifier='virtual'
    return l

def consts(line):
    l=funcs(line)
    for func in l:
        func.pre_modifier='const'
    return l

# TODO: Change maintainer to somebody from developers
# TODO: Add simple variable checking to method body
# TODO: Add to copy constructor copying of containers if they're exist in class
# TODO: Add loggers to methods
# TODO: Add automatic test creation
# TODO: Add common programming patterns
# TODO: Add automatic client(C++)-server(django) generation
