import re
import time

def to_camel(snake_str):
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
            ret+=('#include "'+name+'"\n')
    if isinstance(autodetected, list):
        for name in autodetected:
            ret+=('#include <'+name+'>\n')
    if isinstance(binc, list):
        for name in binc:
            ret+=('#include <'+name+'>\n')
    ret+="// Common used types - uint32_t, etc.\n"
    ret+="#include <stdint.h>\n"
    return ret

def namespace(ns, body, ts=' '*4):
    ns1=''
    if isinstance(ns, list):
        ns1="::".join(ns)
    if isinstance(ns, str):
        ns1=ns
    if ns1=='':
        return body
    return '\n/**\n * \\brief '+ns1+' - \n **/\nnamespace '+ns1+'{\n'+ts+body.replace('\n','\n'+ts)+"\n}; //"+ns1.upper()+" namespace\n"
