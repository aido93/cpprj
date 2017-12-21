from class_gen import class_, virtuals, parent
from decor import to_snake, to_camel, comment_print
from functions import funcs

def t_strat (name, strategies, use_name='void use_strategy()', strategy_use_name='void use()', snake_case=True):
    foo=funcs(use_name)
    bar=funcs(strategy_use_name)
    a=''
    i=1
    if bar[0].args:
        for r in bar[0].args:
            a+=r.name
            if i<len(bar[0].args):
                a+=', '
            i=i+1
    foo[0].body=bar[0].name+'('+a+');'
    c=class_(template_types='T', parents='T', name=name, public_methods=foo)
    c.parents[0].type='private'
    c.comment_methods()
    print(c.decl())
    print('\n'+c.impl()[2])
    for s in strategies:
        p=class_(name=s+'_strategy', protected_methods=funcs(strategy_use_name))
        p.basic_class_content(dd=2, dc=2, dm=2, vd=3)
        comment_print(25, p.name+'.hpp')
        print(p.decl())
        comment_print(25, p.name+'.cpp')
        impl=p.impl()
        im='#include "'+p.name+'.hpp"\n\n'
        im+=impl[0]
        im+=impl[1]
        print(im)
