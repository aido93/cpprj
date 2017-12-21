from class_gen import class_, virtuals, parent
from decor import change, normalize, comment_print
from functions import funcs

def decorator(name, decorators, virt_oper, namespace, directory, user, email, snake_case=False):

    ds=normalize(decorators)
    vs=virtuals(virt_oper)
    for v in vs:
        v.post_modifier='=0'
    c=class_(name=name, public_methods=vs)
    c.basic_class_content(dd=2, dc=2, dm=2, vd=1)
    for d in decorators:
        for v in vs:
            v.post_modifier='override'
        d1=class_(name=d, parents=name, public_methods=vs)
        c.post_class_hpp+=d1.decl()
        c.post_class_cpp+=d1.impl()
    c.save(namespace, directory, user, email)
