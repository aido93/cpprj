import time
import os
import re
import json
from itertools import groupby
from functions import arg, method, add_methods
from header_detection import subtypes_autodetection

pre_field_modifiers    = ['static', 'const', 'mutable']
pre_var_modifiers      = ['static', 'const', 'extern']
post_class_modifiers   = ['final', ]

class parent:
    type           = 'public'
    name           = ''
    template_types = []

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
    
    def __init__(self, **kwargs):
        if 'template_types' in kwargs:
            if isinstance(kwargs['template_types'], str):
                self.template_types=kwargs['template_types'].split(' ')
        if 'parents' in kwargs:
            if isinstance(kwargs['parents'], str):
                self.parents=kwargs['parents'].split(' ')
        self.__dict__.update(kwargs)
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
        ret=[]
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
        ret.append(default)

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
        ret.append(op)
        ret.append(copyc)

        mop=method(return_type=templated_class, name="operator=", hint='move', args=[arg(pre_modifier='const', type=self.name+"&&"),])
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
        ret.append(mop)
        ret.append(movec)
    
        if custom:
            for constructor_params in custom:
                ret.append(method(name=self.name, args=constructor_params))
        if   vd==0:
            ret.append(method(name='~'+self.name))
        elif vd==1:
            ret.append(method(pre_modifier='virtual', name='~'+self.name))
        elif vd==2:
            ret.append(method(pre_modifier='virtual', name='~'+self.name, post_modifier='=0'))
        elif vd==3:
            self.protected_methods.append(method(name='~'+self.name, pre_modifier='virtual'))
        self.public_methods.extend(ret)


    def decl(self, ts=' '*4):
        ret=''
        if self.template_types:
            ret+='template <class '+', class '.join(self.template_types)+'>\n'
        ret+="class "+self.name
        if self.parents:
            ret+=' : '
            for p in self.parents:
                ret+=(p.type+' '+p.name)
                if p.template_types:
                    ret+=('<'+', '.join(p.template_types)+'>')
        if self.post_modifier:
            ret+=self.post_modifier
        ret+='\n{\n'+ts+'public:\n'+ts*2
        if self.public_methods:
            i=1
            for p in self.public_methods:
                if self.public_comments and i in self.public_comments:
                    ret+=self.public_comments[i]
                ret+=p.decl()
                i=i+1
        if self.protected_methods or self.protected_fields:
            ret+=('\n'+ts+'protected:\n'+ts*2)
            if self.protected_methods:
                i=1
                for p in self.protected_methods:
                    if self.protected_comments and i in self.protected_comments:
                        ret+=self.protected_comments[i]
                    ret+=(p.decl()+'\n'+ts*2)
                    i=i+1
            if self.protected_fields:
                for p in self.protected_fields:
                    ret+=(str(p)+'; //!< \n'+ts*2)
        ret+=('\n'+ts+'private:\n'+ts*2)
        if self.private_methods:
            i=1
            for p in self.private_methods:
                if self.private_comments and i in self.private_comments:
                    ret+=self.private_comments[i]
                i=i+1
                ret+=(p.decl()+'\n'+ts*2)
        if self.private_fields:
            for p in self.private_fields:
                ret+=(str(p)+'; //!< \n'+ts*2)
        ret+='\n};\n'

def fields(line):
    line=line.replace('\n','')
    line=line.replace(';','; ')
    line=re.sub('\s+',' ', line)
    args=line.split('; ')
    ret=[]
    for a in args:
        p=a.split(' ')
        t=' '.join(p[:-1])
        kv=p[-1].split('=')
        if len(kv)==1:
            ret.append(arg(type=t, name=kv[0]))
        elif len(kv)==2:
            ret.append(arg(type=t, name=kv[0], value=kv[1]))
    del ret[-1]
    return ret

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

def combine_class(private_vars=None, protected_vars=None, public_methods=None, protected_methods=None, private_methods=None):
    class_fields=[]
    if isinstance(private_vars, list):
        class_fields.extend(private_vars)
    if isinstance(protected_vars, list):
        class_fields.extend(protected_vars)
    
    class_methods=[]
    if isinstance(private_methods, list):
        class_methods.extend(private_methods)
    if isinstance(protected_methods, list):
        class_methods.extend(protected_methods)
    if isinstance(public_methods, list):
        class_methods.extend(public_methods)
    return {'fields': class_fields, 'methods': class_methods}

def add_sg(var, setters, getters):
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
            if t.find('const ')==-1: 
                 pm=None
                 if t.find('static ')!=-1:
                     t=t.replace('static ','')
                     pm='static'
            args=[arg(type="const "+t+'&', name='_'+v.name), ]
            sgetters.append(method( return_type='void',
                                    name=setter,
                                    args=args,
                                    post_modifier=None,
                                    body=v.name+" = _"+v.name+";",
                                    hint='setter'))
    return sgetters

def create_class(class_name,template_types=None, class_parents=None,
                 private_vars=None,protected_vars=None, deps_includes=None,
                 private_setters=False, private_getters=False, protected_setters=False, protected_getters=False,
                 public_methods=None,protected_methods=None,private_methods=None,
                 tabstop=4,snake_case=True):
    cc=combine_class(private_vars, protected_vars, public_methods, protected_methods, private_methods)
    autodetected=[]
    if cc['fields']:
        for v in cc['fields']:
            autodetected.extend(subtypes_autodetection(v, deps_includes))
    if cc['methods']:
        for v in cc['methods']:
            autodetected.extend(subtypes_autodetection(v, deps_includes))
    sgetters=add_sg(private_vars, private_setters, private_getters)
    sgetters.extend(add_sg(protected_vars, protected_setters, protected_getters))
    pub=[]
    if isinstance(public_methods, list):
        pub.extend(public_methods)
    if isinstance(sgetters, list):
        pub.extend(sgetters)
    hpp, cpp, cpp_template=add_methods(class_name, template_types, pub, class_fields, ts )
    hpp1, cpp1, cpp_template1='', '', ''
    hpp2, cpp2, cpp_template2='', '', ''
    ts=' '*tabstop
    ret="""/**
 * \\brief
 * \\details
 **/\n"""
    ret=ret+hpp
    ret=ret+'\n'+ts*2
    if protected_vars or protected_methods:
        ret=ret+'\n'+ts+'protected:\n'
    if protected_vars:
        for v in protected_vars:
            ret=ret+ts*2+v.type+' '+v.name+'; //!< \n'
    if protected_methods:
        hpp1, cpp1, cpp_template1=add_methods(class_name, template_types, protected_methods, class_fields, ts)
        ret=ret+hpp1
        ret=ret+'\n'+ts*2
    ret=ret+'\n'+ts+'private:\n'
    if private_vars:
        for v in private_vars:
            ret=ret+ts*2+v.type+' '+v.name+'; //!< \n'
    if private_methods:
        hpp2, cpp2, cpp_template2=add_methods(class_name, template_types, private_methods, class_fields, ts)
        ret=ret+hpp2
        ret=ret+'\n'+ts*2
    ret=ret+"\n};\n\n"
    headers = [el for el, _ in groupby(sorted(autodetected))]
    return (headers, ret, cpp+cpp1+cpp2, cpp_template+cpp_template1+cpp_template2)

# TODO: Change maintainer to somebody from developers
# TODO: Add simple variable checking to method body
# TODO: Add to copy constructor copying of containers if they're exist in class
# TODO: Add loggers to methods
# TODO: Add automatic test creation
# TODO: Add common programming patterns
# TODO: Add automatic client(C++)-server(django) generation
