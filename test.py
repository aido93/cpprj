from class_gen import class_, consts, virtuals, parent
from functions import method, funcs, statics, create_comments, add_methods
from enums import enum, switch, get_all_enums

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
bar=funcs("std::vector<uint32_t> get_all<T>(const T&); static std::map<uint32_t,std::vector<int>> get_list();")
foo.extend(bar)

print('declaration:')
for f in foo:
    print(f.decl())

print('implementation:')
for f in foo:
    print(f.impl())

s=statics('void log(const std::string& msg); std::list<logger> get_loggers() const')
bar_comments=create_comments(bar)

hpp, cpp, cppt=add_methods('', [], foo, [])
print ('-------------------------------func hpp-----------------------------------')
print(hpp)
print ('-------------------------------func cpp-----------------------------------')
print(cpp)
print ('-------------------------------func cppt-----------------------------------')
print(cppt)
print ('----------------------------------class--------------------------------------')

c=class_(template_types='U V T', parents='par1, par2', name='example', 
        public_methods=bar, protected_methods=s, 
        private_fields='int a;static std::string name;View<int> v;Sing<U, T> sss;',
        protected_fields='char x;std::vector<std::string> s;', 
        set=['private', 'protected'], get=['private', 'protected'])
c.basic_class_content(dd=0, dc=1, dm=2, vd=3)
c.comment_methods()

print(c.decl())
