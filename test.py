from class_gen import class_, consts, virtuals, parent
from functions import method, funcs, statics, create_comments
from enums import enum, switch, get_all_enums
from structs import struct, flags
from decor import header, includes, namespace, comment_print

class_name='example'
foo=funcs("int main(void);void main(void);int main(int argc, char**argv);char* memset(void* begin, uint32_t count, char symbol);")
bar=funcs("std::vector<uint32_t> get_all<T>(const T&); static std::map<uint32_t,std::vector<int>> get_list(const std::string&str);")
c=class_(template_types=None, parents='par1, par2', name=class_name, 
        public_methods=foo, protected_methods=bar, 
        private_fields='int a;static std::string name;View<int> v;Sing<U, T> sss;',
        protected_fields='char x;std::vector<std::string> s;', 
        set=['private', 'protected'], get=['private', 'protected'])
c.parents[1].type='private'
c.basic_class_content(dd=0, dc=1, dm=2, vd=3)
c.comment_methods()
# Pre-code definitions
e0=enum('my_enum4', '   o p u k l ',  upper=False, is_class=False)
b=e0+'\n'
b+=flags('flags', 'a b c d e')+'\n'
b+=c.decl()
impl=c.impl()
if c.template_types:
	b+=('\n#include "'+class_name+'_impl.hpp"')
elif impl[2]:
	b+=('\n'+impl[2])
a=namespace('my_namespace', b)
a=includes(None, c.autodetect(), None)+a
a=header(class_name, 'tester', 'test@test.com')+a

comment_print(25, c.name+'.hpp')
print(a)

if c.template_types:
	comment_print(25, c.name+'_impl.hpp')
	im=impl[2]
else:
	comment_print(25, c.name+'.cpp')
	im='#include "'+class_name+'.hpp"\n\n'
	im+=impl[0]
	im+=impl[1]

print(im)
