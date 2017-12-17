import re

pre_func_modifiers     = [  'static', 'inline', 'extern']
post_func_modifiers    = []
pre_method_modifiers   = [  'static', 'virtual', 'friend']
post_method_modifiers  = [  '=0', '=delete', '=default', 'const', 'const =0', 'const =delete', 'volatile', 
                            'const volatile', 'noexcept', 'override', 'final', '&', '&&']
class arg:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    pre_modifier=None
    type=None
    name=''
    value=None
    def __str__(self):
        a=''
        if self.pre_modifier:
            a+=self.pre_modifier+' '
        a+=(self.type+' '+self.name)
        if self.value:
            a+=('='+self.value)
        return a

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
    def __str__(self):
        a=''
        i=1
        for x in self.args:
            a+=str(x)
            if i<len(self.args):
                a+=', '
            i=i+1
        ret=''
        if self.template_args:
            ret+='template <class '+', class '.join(self.template_args)+'>'
        if self.return_type:
            ret+=self.return_type
        ret+=self.name+' ('+a+')'
        if self.post_modifier:
            ret+=self.post_modifier
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
        a=re.match('((?:.*)\s)+(\w+)\s*(?:<(.*?)>)?\s*\((.*?)\)(.*?)', f)
        return_type=re.sub('\s+',' ',a.group(1))
        pre=return_type.split(' ')
        if pre[0] in pre_method_modifiers:
            return_type=pre[1:]
            pre=pre[0]
        else:
            pre=None
        return_type=return_type.rstrip()
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
                    *type_f, var_name=type_name.split(' ')
                    new_args.append(arg(type=' '.join(type_f), name=var_name, value=value))
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

def statics(line):
    l=funcs(line)
    for func in l:
        func.pre_modifier='static'
    return l

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
                hpp=hpp+ts*2+" * \\return Copy of object\n"+2*ts+" **/\n"
            else:
                hpp=hpp+ts*2+" * \\brief Copy operator=\n"
                hpp=hpp+ts*2+" * \\return Copy of object\n"+2*ts+" **/\n"
                
        elif p.hint=='move':
            if p.return_type==None:
                hpp=hpp+ts*2+" * \\brief Move constructor"
                if p.post_modifier=='=delete':
                    hpp=hpp+" is deleted because \n"
                elif p.post_modifier=='=default':
                    hpp=hpp+" is default \n"
                else:
                    hpp=hpp+'\n'
                hpp=hpp+ts*2+" * \\return Rvalue-reference to the object\n"+2*ts+" **/\n"
            else:
                hpp=hpp+ts*2+" * \\brief Move operator=\n"
                hpp=hpp+ts*2+" * \\return Rvalue-reference to the object\n"+2*ts+" **/\n"
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
                hpp=hpp+ts*2+" * \\return None \n"+2*ts+" **/\n"
            else:
                hpp=hpp+ts*2+" * \\return  \n"+2*ts+" **/\n"
        # Create method
        hpp=hpp+ts*2
        if p.template_args:
            hpp=hpp+"template <class "+", class ".join(p.template_args)+'>\n'+ts*2
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
                i=i+1
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
                        i=i+1
                        
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
                elif p.return_type and p.return_type!='void' and p.hint!='move' and p.hint!='copy':
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
                        i=i+1
                cpp_template+=")"
                if p.post_modifier:
                    cpp_template=cpp_template+" "+p.post_modifier
                cpp_template+="\n{\n"+ts
                if p.body:
                    cpp_template+=p.body
                elif p.return_type and p.return_type!='void':
                    cpp_template+=p.return_type+' ret;\n'+ts+'\n'+ts+'return ret;'
                cpp_template+='\n}\n'
        if template_types and  isinstance(template_types,list):
            cpp_template=cpp_template+cpp
            cpp=''
    return (hpp, cpp, cpp_template)


