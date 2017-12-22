#!/usr/bin/env python3
from class_gen import class_, consts, virtuals, parent
from functions import arg, method, funcs, statics, create_comments
from enums import enum, switch, get_all_enums
from structs import struct, flags
from decor import header, includes, namespace, comment_print
from os.path import join, split

def make_arch(directory, developers, tabstop, snake_case, type):
    class_name='test_class'
    bar=funcs("void hello()")
    bar[0].body='std::cout<<"Hello! My name is"<<name<<std::endl;'
    c=class_(name=class_name, 
            public_methods=bar, 
            private_fields='const std::string name;',
            get=['private'], constructors=[arg(name='_name', pre_modifier='const', type='std::string&'), ],
            test=True)
    c.basic_class_content(dd=0, dc=1, dm=1, vd=1)
    c.comment_methods()
    # Pre-code definitions
    e0=enum('my_enum4', '   o p u k l ',  upper=False, is_class=False)
    b=e0+'\n'
    b+=flags('flags', 'a b c d e')+'\n'
    b+=c.decl()
    impl=c.impl()
    c.pre_class=b
    c.save('my_example', directory, developers[0]['name'], developers[0]['email'])
    global_funcs=funcs("int main(int argc, char**argv);")
    global_funcs[0].body=class_name+' test("Dummy");'
    ret=global_funcs[0].impl()
    with open(join(directory, 'main.cpp'), 'w') as f:
        f.write(ret)
