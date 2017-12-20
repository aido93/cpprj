from class_gen import class_, virtuals, parent
from decor import change, normalize, comment_print
from functions import funcs

def factory(name, factories, products, namespace, directory, user, email, snake_case=False):

    factories=normalize(factories)
    products=normalize(products)
    
    s=''
    for p in products:
        n  = change('create_'+p, snake_case)
        ap = change('abstract_'+p, snake_case)
        s+=(ap+' '+n+'();')
    vs=virtuals(s)
    for v in vs:
        v.post_modifier='=0'
    c=class_(name=name, public_methods=vs)
    c.basic_class_content(dd=2, dc=1, dm=2, vd=2)
    c.save(namespace, directory, user, email)
    for v in vs:
        v.post_modifier='override'
    for f in factories:
        factory=class_(name=f, parents=name, public_methods=vs)
        factory.save(namespace, directory, user, email)

    for p in products:
        ap = change('abstract_'+p, snake_case)
        abstract_product=class_(name=ap, parents=name, public_methods=vs)
        abstract_product.save(namespace, directory, user, email)
        for f in factories:
            n=change(p+'_'+f, snake_case)
            product=class_(name=n, parents=ap)
            product.save(namespace, directory, user, email)
