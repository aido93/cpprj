from class_gen import class_, consts, virtuals, parent
from functions import method, funcs, statics, create_comments
from enums import enum, switch, get_all_enums
from structs import struct, flags
from decor import header, includes, namespace
e0=enum('my_enum', 'q w e r=10 t y ')
e1=enum('', 'q w e r=10 t y ')
e2=enum('my_enum2', 'a s d f=15 g h', upper=True)
e3=enum('my_enum3', 'z x c v b',      upper=True,  is_class=False)
e4=enum('my_enum4', '   o p u k l ',  upper=False, is_class=False)

enums=e0+'\n'+e1+'\n'+e2+'\n'+e3+'\n'+e4

w=get_all_enums(enums)
print(enums)
print(switch(w, 'my_enum',  'a'))
print(switch(w, 'my_enum2', 'b'))
print(switch(w, 'my_enum3', 'c'))
print(switch(w, 'my_enum4', 'd'))
print ('-------------------------------functions-------------------------------------')

foo=funcs("int main(void);void main(void);int main(int argc, char**argv);char* memset(void* begin, uint32_t count, char symbol);")
foo_comments=create_comments(foo)
bar=funcs("std::vector<uint32_t> get_all<T>(const T&); static std::map<uint32_t,std::vector<int>> get_list(const std::string&str);")
foo.extend(bar)

print('\ndeclaration:')
for f in foo:
    print(f.decl())

print('\nimplementation:')
for f in foo:
    print(f.impl())

s=statics('void log(const std::string& msg); std::list<logger> get_loggers() const')
bar_comments=create_comments(bar)

print ('-------------------------------struct-------------------------------------')
st=flags('flags', 'a b c d e')
print (st)

print ('-------------------------------class-------------------------------------')
class_name='example'
c=class_(template_types='U V T', parents='par1, par2', name=class_name, 
        public_methods=bar, protected_methods=s, 
        private_fields='int a;static std::string name;View<int> v;Sing<U, T> sss;',
        protected_fields='char x;std::vector<std::string> s;', 
        set=['private', 'protected'], get=['private', 'protected'])
c.parents[1].type='private'
c.basic_class_content(dd=0, dc=1, dm=2, vd=3)
c.comment_methods()
print(header(class_name, 'tester', 'test@test.com'))
print(includes(None, c.autodetect(), None))
print(c.decl())

impl=c.impl()

print ('-----------------------------static impl----------------------------------')
print(impl[0])
print ('-----------------------------cpp impl----------------------------------')
print(impl[1])
print ('-----------------------------cpp template impl----------------------------------')
print(impl[2])

