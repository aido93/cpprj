import time
import os
import re
import json
from itertools import groupby
from functions import arg, method, add_methods
from header_detection import subtype_autodetection

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
    # Constructors:
    # dd=0 - custom constructor (delete default)
    # dd=1 - deleted constructor
    # dd=2 - default constructor
    def basic_class_content(class_name, template_types, dd=0, dc=0, dm=0, vd=0, custom=None):
        ret=[]
        self.name=class_name
        self.template_types=template_types
        templated_class=class_name
        if template_types and  isinstance(template_types,list):
            templated_class=templated_class+'<'+', '.join(template_types)+'>'

        if dd==0:
            d1=method(name=class_name)
            d1.post_modifier="noexcept"
            ret.append(d1)
        elif dd==1:
            d1=method(name=class_name)
            d1.post_modifier="=delete"
            ret.append(d1)
        elif dd==2:
            d1=method(name=class_name)
            d1.post_modifier="=default"
            ret.append(d1)

        if dc==0:
            op=method(return_type=templated_class, name="operator=", args=[arg(type="const "+class_name+"&"),])
            op.hint='copy'
            ret.append(op)
            d1=method(name=class_name)
            d1.hint='copy'
            d1.args=[arg(type="const "+class_name+"&"),]
            ret.append(d1)
        elif dc==1:
            d1=method(name=class_name)
            d1.hint='copy'
            d1.args=[arg(type="const "+class_name+"&"),]
            d1.post_modifier="=delete"
            ret.append(d1)
        elif dc==2:
            op=method(return_type=templated_class, name="operator=", args=[arg(type="const "+class_name+"&"),])
            op.hint='copy'
            op.post_modifier='=default'
            ret.append(op)
            d1=method(name=class_name)
            d1.hint='copy'
            d1.args=[arg(type="const "+class_name+"&"),]
            d1.post_modifier="=default"
               ret.append(d1)

        if dm==0:
            op=method(return_type=templated_class+'&', name="operator=", args=[arg(type="const "+class_name+"&&"),])
            op.hint='move'
            ret.append(op)
            d1=method(name=class_name)
            d1.hint='move'
            d1.args=[arg(type="const "+class_name+"&&"),]
            ret.append(d1)
        elif dm==1:
            d1=method(name=class_name)
            d1.hint='move'
            d1.args=[arg(type="const "+class_name+"&&"),]
            d1.post_modifier="=delete"
            ret.append(d1)
        elif dm==2:
            op=method(return_type=class_name+'&', name="operator=", args=[arg(type="const "+class_name+"&&"),])
            op.hint='move'
            op.post_modifier='=default'
            ret.append(op)
            d1=method(name=class_name)
            d1.hint='move'
            d1.args=[arg(type="const "+class_name+"&&"),]
            d1.post_modifier="=default"
            ret.append(d1)
    
        if custom:
            for constructor_params in custom:
                d1=method(name=class_name)
                d1.args=constructor_params
                ret.append(d1)
        if vd==0:
            d1=method(name=class_name)
            d1.name="~"+class_name
            ret.append(d1)
        elif vd==1:
            d1=method(name=class_name)
            d1.name="~"+class_name
            d1.pre_modifier="virtual"
            ret.append(d1)
        elif vd==2:
            d1=method(name=class_name)
            d1.name="~"+class_name
            d1.pre_modifier="virtual"
            d1.post_modifier="=0"
            ret.append(d1)
        self.public_methods=ret


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

def to_camel(snake_str):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    components = snake_str.split('_')
    return components[0] + "".join(x.title() for x in components[1:])

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def to_snake(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()

def header(class_name, author, email):
    return """/**
 * Description: Interface to the """+class_name+"""-class
 * TODO: 
 * Author: """+author+"<"+email+">"+"""
 * Date:   """+time.strftime('%d.%m.%Y')+"""
 * */
#pragma once\n"""

def includes(quinc, autodetected, binc):
    ret=""
    if isinstance(quinc,list):
        for name in quinc:
            ret=ret+'#include "'+name+'"\n'
    if isinstance(autodetected, list):
        for name in autodetected:
            ret=ret+'#include <'+name+'>\n'
    if isinstance(binc, list):
        for name in binc:
            ret=ret+'#include <'+name+'>\n'
    ret=ret+"// Common used types - uint32_t, etc.\n"
    ret=ret+"#include <stdint.h>\n"
    return ret

def namespace(namespaces_name, body, tabstop):
    ts='\n'+' '*tabstop
    namespace_name=''
    if isinstance(namespaces_name, list):
        namespace_name="::".join(namespaces_name)
    if isinstance(namespaces_name, str):
        namespace_name=namespaces_name
    if namespace_name=='':
        return body
    return """/**
 * \\brief """+namespace_name+""" - 
 **/
namespace """+namespace_name+"""
{
"""+ts+body.replace('\n',ts)+"\n}; //"+namespace_name.upper()+" namespace\n"

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
    if var:
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
            autodetected.extend(subtypes_autodetection(, deps_includes))
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

def bundle( class_name, author, email,
            namespaces_name=None,
            template_types=None, class_parents=None,
            dd=0, dc=0, dm=0, vd=0, custom=None,
            private_vars=None,protected_vars=None, deps_includes=None,
            private_setters=False, private_getters=False, protected_setters=False, protected_getters=False,
            public_methods=None,protected_methods=None,private_methods=None,
            quinch=None, binch=None, quincs=None, bincs=None,
            tabstop=4, snake_case=True):
    if snake_case:
        class_name=to_snake(class_name)
    else:
        class_name=to_camel(class_name)
    publics=basic_class_content(class_name, template_types, dd, dc,dm, vd, custom)
    if isinstance(public_methods, list):
        publics.extend(public_methods)
    header_autodetected, hpp_gen, cpp_gen, cpp_template_gen=create_class(class_name,template_types, class_parents,
                 private_vars,protected_vars, deps_includes,
                 private_setters, private_getters, protected_setters, protected_getters,
                 publics,protected_methods,private_methods,
                 tabstop,snake_case)
    src_autodetected=[]
    hpp=header(class_name, author, email)+includes(quinch,header_autodetected,binch)+namespace(namespaces_name, hpp_gen+cpp_template_gen, tabstop)
    cpp=''
    if not template_types:
        cpp=header(class_name, author, email)+includes(quincs,src_autodetected,   bincs)+namespace(namespaces_name, cpp_gen, tabstop)
    #test=header(class_name, author, email)+gen_test(class_name)
    #return (hpp.replace('\n', os.linesep), cpp.replace('\\n', '\n'))
    return (hpp, cpp)

# TODO: Change maintainer to somebody from developers
# TODO: Add simple variable checking to method body
# TODO: Add to copy constructor copying of containers if they're exist in class
# TODO: Add loggers to methods
# TODO: Add automatic test creation
# TODO: Add common programming patterns
# TODO: Add automatic client(C++)-server(django) generation
