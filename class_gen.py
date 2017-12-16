import time
import os
import re
import json
from difflib import SequenceMatcher
from itertools import groupby

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

pre_method_modifiers   = ['static', 'inline', 'virtual', 'extern', 'friend']
pre_field_modifiers    = ['static', 'const', 'mutable']
pre_var_modifiers      = ['static', 'const', 'extern']
post_method_modifiers  = [  '=0', '=delete', '=default', 'const', 'const =0', 'const =delete', 'volatile', 
                            'const volatile', 'noexcept', 'override', 'final', '&', '&&']
post_class_modifiers   = ['final', ]
not_cpp_post_mod     = ['=delete', '=0', '=default']
constructor_post_mod = ['=delete', '=0', '=default', 'noexcept']

class arg:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    pre_modifier=None
    type=None
    name=''
    value=None
    def __str__(self):
        return str(self.type)+' '+self.name+' = '+str(self.value)

class method:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    template_args=[]
    pre_modifier=None
    return_type=None
    name=''
    args=[]
    post_modifier=None
    body=None
    hint=''

class parents:
    type='public'
    name=''
    template_types=None

def fields(line):
    line=line.replace('\n','')
    line=line.replace(';','; ')
    line=re.sub('[\t ]+',' ', line)
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

# for generating a bunch of dummy functions
def funcs(line):
    line=line.replace('\n','')
    line=line.replace(';','; ')
    line=re.sub('\s+',' ', line)
    funcs=line.split('; ')
    funcs=[value for value in funcs if value]
    ret=[]
    for f in funcs:
        a=re.match('((?:.*)\s)+(\w+)(?:<(.*?)>)?\((.*?)\)(.*?)', f)
        return_type=re.sub('\s+',' ',a.group(1))
        pre=return_type.split(' ')
        if pre[0] in pre_method_modifiers:
            return_type=pre[1:]
            pre=pre[0]
        else:
            pre=None
        name=a.group(2)
        template_list=a.group(3)
        if template_list:
            template_list=template_list.replace(',',', ')
            template_list=re.sub('\s+',' ', template_list)
            template_list=template_list.split(', ')
        args=a.group(4).replace(',',', ')
        if args!='':
            args=re.sub('\s+',' ', args)
            args=args.split(', ')
            new_args=[]
            t1=0
            temp=''
            for ar in args:
                c1=ar.count('<')
                c2=ar.count('>')
                t1=t1+c1-c2
                if t1<0:
                    raise Exception('Count of < is less than >')
                elif t1>0:
                    temp=temp+ar
                else:
                    a1=temp+ar
                    kv1=a1.split('=')
                    value=None
                    if len(kv1)==2:
                        type_name=kv[0]
                        value=kv1[1]
                    else:
                        type_name=a1
                        value=None
                    *type_f, name=type_name.split(' ')
                    new_args.append(arg(type=' '.join(type_f), name=name, value=value))
                    temp=''
        else:
            new_args=None
        #now we cannot continue because of map<int, int, str> - this cannot be parsed correctly
        post_modifier=a.group(5)
        if post_modifier!='' and post_modifier not in post_method_modifiers:
            raise Exception('Undefined post-modifier:'+post_modifier)
        ret.append(method(  template_args=template_list, 
                            pre_modifier=pre, 
                            return_type=return_type, 
                            name=name, 
                            args=new_args, 
                            post_modifier=post_modifier))
    return ret

def virtuals(line):
    l=funcs(line)
    for func in l:
        func.pre_modifier='virtual'
    return l

def statics(line):
    l=funcs(line)
    for func in l:
        func.pre_modifier='static'
    return l

def consts(line):
    l=funcs(line)
    for func in l:
        func.pre_modifier='const'
    return l

def enum(name, upper=False, ts=' '*4, is_class=True, elements=[]):
    if upper:
        a=(s.upper() for s in elements)
    else:
        a=elements
    els=(',\n'+ts).join(a)
    if is_class:
        return 'enum class\n{\n'+ts+els+'\n};\n'
    else:
        return 'enum \n{\n'+ts+els+'\n};\n'

def struct(name, args, ts=' '*4):
    text=[]
    for f in args:
        if not f.value:
            text.append(f.type+' '+f.name)
        else:
            text.append(f.type+' '+f.name+' = '+f.value)
    return 'struct '+name+'\n{\n'+ts+(';///> \n'+ts).join(text)+'\n};\n'

def switch(enum_vars, enum_name='', ts=' '*4):
    body=''
    if enum_name=='':
        for v in enum_vars:
            body=body+'case '+v+':\n'+ts+'{\n'+ts*2+'\n'+ts*2+'break;\n'+ts+'\n}\n'
    else:
        for v in enum_vars:
            body=body+'case '+enum_name+'::'+v+':\n'+ts+'{\n'+ts*2+'\n'+ts*2+'break;\n'+ts+'\n}\n'
    return 'switch ('+var_name+')\n{'+ts+body+'\n'+ts+'default:\n'+ts+'{'+ts*2+'\n'+ts+'}\n}\n'

#TODO IT
cycles=['for', 'while', 'do']
def func_body(line, args, class_fields):
    line=line.replace('\n','')
    line=re.sub('\s+',' ', line)
    ops=line.split(' ')
    def rec(opses):
        v=opses[0]
        if v in cycles or opses=='switch':
            end=rec(opses[1:])
            return gen_code(v, end, args, class_fields, body)
        else:
            return v

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
 */
namespace """+namespace_name+"""
{
"""+ts+body.replace('\n',ts)+"\n}; //"+namespace_name.upper()+" namespace\n"

def add_methods(class_name, template_types, methods, ts, class_fields):
    hpp=""
    for p in methods:
        # Create comments
        hpp=hpp+ts*2+"/**\n"
        if p.hint=='setter':
            hpp=hpp+ts*2+" * \\brief Setter-method for "+p.args[0].name[1:]+" class field \n"
            hpp=hpp+ts*2+" * \\return None\n"+ts*2+" */\n"
        elif p.hint=='getter':
            hpp=hpp+ts*2+" * \\brief Getter-method for "+p.name.replace('get_','')+" class field \n"
            hpp=hpp+ts*2+" * \\return Value of the "+p.name.replace('get_','')+"* class field\n"+2*ts+" */\n"
        elif p.hint=='copy':
            if p.return_type==None:
                hpp=hpp+ts*2+" * \\brief Copy constructor"
                if p.post_modifier=='=delete':
                    hpp=hpp+" is deleted because \n"
                elif p.post_modifier=='=default':
                    hpp=hpp+" is default \n"
                else:
                    hpp=hpp+'\n'
                hpp=hpp+ts*2+" * \\return Copy of object\n"+2*ts+"**/\n"
            else:
                hpp=hpp+ts*2+" * \\brief Copy operator=\n"
                hpp=hpp+ts*2+" * \\return Copy of object\n"+2*ts+"**/\n"
                
        elif p.hint=='move':
            if p.return_type==None:
                hpp=hpp+ts*2+" * \\brief Move constructor"
                if p.post_modifier=='=delete':
                    hpp=hpp+" is deleted because \n"
                elif p.post_modifier=='=default':
                    hpp=hpp+" is default \n"
                else:
                    hpp=hpp+'\n'
                hpp=hpp+ts*2+" * \\return Rvalue-reference to the object\n"+2*ts+"**/\n"
            else:
                hpp=hpp+ts*2+" * \\brief Move operator=\n"
                hpp=hpp+ts*2+" * \\return Rvalue-reference to the object\n"+2*ts+"**/\n"
        else:
            hpp=hpp+ts*2+" * \\brief \n"
            hpp=hpp+ts*2+" * \\details \n"
            if p.template_args:
                for v in p.template_args:
                    hpp=hpp+ts*2+" * \\param [in] "+v+" is the type corresponding to \n"
            if p.args:
                for v in p.args:
                    hpp=hpp+ts*2+" * \\param [in] "+v.name+" - "+"."
                    if v.value:
                        hpp+=" Default value is "+v.value
                    hpp+="\n"
            if not p.return_type:
                hpp=hpp+ts*2+" **/\n"
            elif p.return_type=='void':
                hpp=hpp+ts*2+" * \\return None \n"+2*ts+"**/\n"
            else:
                hpp=hpp+ts*2+" * \\return  \n"+2*ts+"**/\n"
        # Create method
        hpp=hpp+ts*2
        if p.template_args:
            hpp=hpp+"template <class "+", class ".join(p.template_args)+'>\n'
        if p.pre_modifier:
            if p.pre_modifier in pre_method_modifiers:
                if p.name==class_name:
                    raise Exception("constructor cannot have pre-modifiers")
                else:
                    hpp=hpp+p.pre_modifier+' '
            else:
                raise Exception("Undefined pre-modifier: "+str(p.pre_modifier))
        if p.return_type:
            if p.name==class_name:
                raise Exception("constructor cannot have type")
            hpp=hpp+p.return_type+' '
        hpp=hpp+p.name+' ('
        if p.args:
            i=1
            for v in p.args:
                hpp=hpp+v.type+" "+v.name
                if v.value and v.value!='':
                    hpp=hpp+"="+v.value
                if i<len(p.args):
                    hpp=hpp+', '
        hpp=hpp+")"
        if p.post_modifier:
            if p.post_modifier in post_method_modifiers:
                if p.name==class_name and p.post_modifier not in constructor_post_mod:
                    raise Exception("constructor cannot be "+str(p.post_modifier))
                else:
                    hpp=hpp+" "+p.post_modifier
            else:
                raise Exception("Undefined post-modifier: "+str(p.post_modifier))
        hpp=hpp+";\n\n"
    # create src
    cpp=""
    cpp_template=""
    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()
    templated_class=class_name
    if template_types and  isinstance(template_types,list):
        templated_class=templated_class+'<'+', '.join(template_types)+'>'
    for p in methods:
        if (p.post_modifier and p.post_modifier not in not_cpp_post_mod) or not p.post_modifier:
            is_template=False
            if template_types and  isinstance(template_types,list):
                cpp_template=cpp_template+"template <class "+', class '.join(template_types)+'>\n'
            if p.template_args:
                is_template=True
                cpp_template=cpp_template+"template <class "+', class '.join(p.template_args)+'>\n'
            if not is_template:
                if p.pre_modifier=='static':
                    cpp=cpp+'static '
                if p.return_type:
                    cpp=cpp+p.return_type+' '
                cpp=cpp+templated_class+"::"+p.name+' ('
                if p.args:
                    i=1
                    for v in p.args:
                        if v.name:
                            cpp=cpp+v.type+" "+v.name
                        else:
                            cpp=cpp+v.type+" x"
                        if i<len(p.args):
                            cpp=cpp+', '
                        
                cpp=cpp+")"
                if p.post_modifier:
                    cpp=cpp+" "+p.post_modifier
                if p.return_type==None and p.name[0]!='~' and class_fields and p.hint!='move' and p.hint!='copy': # Custom constructor
                    cpp=cpp+': \n'+ts
                    init_list=[]
                    if p.args:
                        for constr_arg in p.args:
                            for var in class_fields:
                                if similar(constr_arg.name, var.name)>=0.8:
                                    init_list.append(var.name+'('+str(constr_arg.name)+')')
                    cpp=cpp+('\n'+ts).join(init_list)
                cpp=cpp+"\n{\n"+ts
                if p.body:
                    cpp=cpp+p.body
                elif p.return_type and p.hint!='move' and p.hint!='copy':
                    cpp=cpp+p.return_type+' ret;\n'+ts+'\n'+ts+'return ret;'
                elif p.return_type and p.hint=='copy':
                    if p.args[0].name!='':
                        cpp=cpp+'if (this != &'+p.args[0].name+')\n'+ts+'{\n'
                    else:
                        cpp=cpp+'if (this != &x)\n'+ts+'{\n'
                    cpp=cpp+ts*2+'\n'
                    cpp=cpp+ts+'}\n'
                    cpp=cpp+ts+'return *this;'
                cpp=cpp+"\n}\n\n"

            else:
                if p.return_type:
                    cpp_template=cpp_template+p.return_type+' '
                cpp_template=cpp_template+templated_class+"::"+p.name+' ('
                if p.args:
                    i=1
                    for v in p.args:
                        if v.name:
                            cpp_template=cpp_template+v.type+" "+v.name
                        else:
                            cpp_template=cpp_template+v.type+" x"
                        if i<len(p.args):
                            cpp_template=cpp_template+', '
                cpp_template=cpp_template+")"
                if p.post_modifier:
                    cpp_template=cpp_template+" "+p.post_modifier
                if p.body:
                    cpp_template=cpp_template+"\n{"+ts+p.body+"\n}\n"
                elif p.return_type:
                    cpp_template=cpp_template+'\n{'+ts+p.return_type+' ret;\n'+ts+'\n'+ts+'return ret;\n}\n'
        if template_types and  isinstance(template_types,list):
            cpp_template=cpp_template+cpp
            cpp=''
    return (hpp, cpp, cpp_template)

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
 * */\n"""
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
