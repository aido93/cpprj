import re

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

pre_field_modifiers    = ['static', 'const', 'mutable']
pre_var_modifiers      = ['static', 'const', 'extern']

def subtypes_autodetection(typ, deps_includes=[]):
    autodetected=[]
    # Cleaning
    if not typ:
        return autodetected
    typ1 = [v for v in typ if v]
    for t1 in typ1:
        for pre in pre_field_modifiers:
            if t1:
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


