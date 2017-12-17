import time
import os
import re
import json
from difflib import SequenceMatcher
from itertools import groupby
from functions import arg, method, add_methods

stl={
    'containers'            : [ "vector","list","map","queue","deque","string","array","set","stack","forward_list","unordered_set","unordered_map"],
    'memory'                : [ "auto_ptr","shared_ptr","weak_ptr","unique_ptr","auto_ptr_ref","default_delete",
                                "allocator","allocator_arg","allocator_arg_t","allocator_traits",
                                "enable_shared_from_this","owner_less","raw_storage_iterator","pointer_traits","pointer_safety"],
    'chrono'                : [ "duration","time_point","system_clock","steady_clock","high_resolution_clock","treat_as_floating_point",
                                "duration_values","hours","minutes","seconds","milliseconds"],
    'functional'            : [ "function",],
    'initializer_list'      : [ "initializer_list",],
    'random'                : [ "random_device",],
    'string'                : [ "string","wstring","basic_string","u16string","u32string"],
    'valarray'              : [ "valarray","slice","gslice","slice_array","gslice_array","mask_array","indirect_array"],
    'utility'               : [ "pair",],
    'mutex'                 : [ "mutex","recursive_mutex","timed_mutex","recursive_timed_mutex","unique_lock","lock_guard","once_flag"],
    'thread'                : [ "thread",],
    'future'                : [ "future","promise","packaged_task","shared_future","future_status","future_error","future_errc"],
    'condition_variable'    : [ "condition_variable","condition_variable_any","cv_status"],
    'atomic'                : [ "atomic","atomic_flag"],
    'tuple'                 : [ "tuple","tuple_size","tuple_element"],
    'complex'               : [ "complex",]
}

pre_field_modifiers    = ['static', 'const', 'mutable']
pre_var_modifiers      = ['static', 'const', 'extern']
post_class_modifiers   = ['final', ]
not_cpp_post_mod     = ['=delete', '=0', '=default']
constructor_post_mod = ['=delete', '=0', '=default', 'noexcept']

class parents:
    type='public'
    name=''
    template_types=None

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

def subtypes_autodetection(typ, deps_includes):
    autodetected=[]
    # Cleaning
    t1=typ
    if not t1:
        return autodetected
    for pre in pre_field_modifiers:
        t1=re.sub(str(pre)+'\s+', '', t1)
    for inc, t in stl.items():
        if any("std::"+substring in t1 for substring in t):
            if inc=='containers':
                for substring in t:
                    if "std::"+substring in t1:
                        autodetected.append(substring)
            elif inc not in autodetected:
                autodetected.append(inc)
    if t1[0]=='Q' and len(t1)!=1:
        del_templ=re.sub('<.*>', '', t1)
        autodetected.append(del_templ)
    elif isinstance(deps_includes, list):
        for dep in deps_includes:
            for file in os.walkdir(dep):
                if "class "+t1 in open(file).read():
                    autodetected.append(file)
    return autodetected

def create_class(class_name,template_types=None, class_parents=None,
                 private_vars=None,protected_vars=None, deps_includes=None,
                 private_setters=False, private_getters=False, protected_setters=False, protected_getters=False,
                 public_methods=None,protected_methods=None,private_methods=None,
                 tabstop=4,snake_case=True):
    autodetected=[]
    if isinstance(private_vars, list):
        for v in private_vars:
            autodetected.extend(subtypes_autodetection(v.type, deps_includes))
    if isinstance(protected_vars, list):
        for v in protected_vars:
            autodetected.extend(subtypes_autodetection(v.type, deps_includes))
    if private_methods and  isinstance(private_methods, list):
        for v in private_methods:
            autodetected.extend(subtypes_autodetection(v.return_type, deps_includes))
    if protected_methods and  isinstance(protected_methods, list):
        for v in protected_methods:
            autodetected.extend(subtypes_autodetection(v.return_type, deps_includes))
    if public_methods and  isinstance(public_methods, list):
        for v in public_methods:
            autodetected.extend(subtypes_autodetection(v.return_type, deps_includes))
    ts=' '*tabstop
    ret="""/**
 * \\brief
 * \\details
 **/\n"""
    if template_types:
        ret=ret+'template <class '+', class '.join(template_types)
        ret=ret+">\n"
    ret=ret+"class "+class_name;
    if class_parents:
        ret=ret+': '
        i=1
        for c in class_parents:
            ret=ret+c.type+' '+c.name
            if c.template_types and isinstance(c.template_types, list):
                ret=ret+'<'+', '.join(c.template_types)+'>'
            if i<len(class_parents):
                ret=ret+', '
            i=i+1
    ret=ret+"\n{\n"+ts+'public:\n';
    sgetters=[]
    if protected_vars:
        for v in protected_vars:
            if not snake_case:
                setter=to_camel("set_"+v.name)
                getter=to_camel("get_"+v.name)
            else:
                setter=to_snake("set_"+v.name)
                getter=to_snake("get_"+v.name)
            if protected_getters:
                sgetters.append(method( return_type=v.type,
                                        name=getter,
                                        args=None,
                                        post_modifier="const",
                                        body="return "+v.name+";",
                                        hint='getter'))
            if protected_setters:
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
    if private_vars:
        for v in private_vars:
            if not snake_case:
                setter=to_camel("set_"+v.name)
                getter=to_camel("get_"+v.name)
            else:
                setter=to_snake("set_"+v.name)
                getter=to_snake("get_"+v.name)
            if private_getters:
                sgetters.append(method( return_type=v.type,
                                        name=getter,
                                        args=None,
                                        post_modifier="const",
                                        body="return "+v.name+";",
                                        hint='getter'))
            if private_setters:
                t=v.type
                if t.find('const ')==-1: 
                    pm=None
                    if t.find('static ')!=-1:
                        t=t.replace('static ','')
                        pm='static'
                    args=[arg(type="const "+t+'&', name='_'+v.name),]
                    sgetters.append(method( return_type='void',
                                            name=setter,
                                            args=args,
                                            post_modifier=None,
                                            pre_modifier=pm,
                                            body=v.name+" = _"+v.name+";",
                                            hint='setter'))
    class_fields=[]
    if isinstance(private_vars, list):
        class_fields.extend(private_vars)
    if isinstance(protected_vars, list):
        class_fields.extend(protected_vars)
    pub=[]
    if isinstance(public_methods, list):
        pub.extend(public_methods)
    if isinstance(sgetters, list):
        pub.extend(sgetters)
    hpp, cpp, cpp_template=add_methods(class_name, template_types, pub, ts, class_fields)
    hpp1, cpp1, cpp_template1='', '', ''
    hpp2, cpp2, cpp_template2='', '', ''
    ret=ret+hpp
    ret=ret+'\n'+ts*2
    if protected_vars or protected_methods:
        ret=ret+'\n'+ts+'protected:\n'
    if protected_vars:
        for v in protected_vars:
            ret=ret+ts*2+v.type+' '+v.name+'; //!< \n'
    if protected_methods:
        hpp1, cpp1, cpp_template1=add_methods(class_name, template_types, protected_methods, ts, class_fields)
        ret=ret+hpp1
        ret=ret+'\n'+ts*2
    ret=ret+'\n'+ts+'private:\n'
    if private_vars:
        for v in private_vars:
            ret=ret+ts*2+v.type+' '+v.name+'; //!< \n'
    if private_methods:
        hpp2, cpp2, cpp_template2=add_methods(class_name, template_types, private_methods, ts, class_fields)
        ret=ret+hpp2
        ret=ret+'\n'+ts*2
    ret=ret+"\n};\n\n"
    headers = [el for el, _ in groupby(sorted(autodetected))]
    return (headers, ret, cpp+cpp1+cpp2, cpp_template+cpp_template1+cpp_template2)

# vd=0 - not virtual
# vd=1 - virtual
# vd=2 - pure virtual
# Constructors:
# dd=0 - custom constructor (delete default)
# dd=1 - deleted constructor
# dd=2 - default constructor
def basic_class_content(class_name, template_types, dd=0, dc=0, dm=0, vd=0, custom=None):
    ret=[]
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
    return ret

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
