import date
import argparse
# move to cpp for finding private or protected vars
from difflib import SequenceMatcher

std={
	'containers' 			: [ "vector","list","map","queue","deque","string","array","set","stack","forward_list","unordered_set","unordered_map"],
	'memory'				: [ "auto_ptr","shared_ptr","weak_ptr","unique_ptr","auto_ptr_ref","default_delete",
								"allocator","allocator_arg","allocator_arg_t","allocator_traits",
								"enable_shared_from_this","owner_less","raw_storage_iterator","pointer_traits","pointer_safety"],
	'chrono'				: [ "duration","time_point","system_clock","steady_clock","high_resolution_clock","treat_as_floating_point",
								"duration_values","hours","minutes","seconds","milliseconds"],
	'functional'			: [ "function",],
	'initializer_list'		: [ "initializer_list",],
	'random'				: [ "random_device",],
	'string'				: [ "string","wstring","basic_string","u16string","u32string"],
	'valarray'				: [ "valarray","slice","gslice","slice_array","gslice_array","mask_array","indirect_array"],
	'utility'				: [ "pair",],
	'mutex'					: [ "mutex","recursive_mutex","timed_mutex","recursive_timed_mutex","unique_lock","lock_guard","once_flag"],
	'thread'				: [ "thread",],
	'future'				: [ "future","promise","packaged_task","shared_future","future_status","future_error","future_errc"],
	'condition_variable'	: [ "condition_variable","condition_variable_any","cv_status"],
	'atomic'				: [ "atomic","atomic_flag"],
	'tuple'					: [ "tuple","tuple_size","tuple_element"],
	'complex'				: [ "complex",]
}

def header(class_name, author, email):
	return """/**
 * Description: Interface to the """+class_name+"""-class
 * Todo: 
 * Author: """+author+"<"+email+">"+"""
 * Date:   """+date.date()+"""
 * */
#pragma once\n"""

def includes(quinch, autodetected, binch):
	ret=""
	for name in quinch:
		ret=ret+'#include "'+name+'"\n'
	for name in autodetected:
		ret=ret+'#include <'+name+'>\n'
	for name in binch:
		ret=ret+'#include <'+name+'>\n'
	ret=ret+"// Common used types - uint32_t, etc.\n"
	ret=ret+"#include <stdint.h>\n"
	return ret

def namespace(namespace_name, body, tabstop):
	ts='\n'+' '*tabstop
	return """/**
 * \\brief """+namespace_name+""" - 
 */
namespace """+namespace_name+"""
{
"""+ts+body.replace('\n',ts)+"\n}; //"+namespace.upper()+" namespace\n"

def add_methods(methods, ts):
	ret=""
	for p in methods:
		ret=ret+ts*2+"/**\n"
		ret=ret+ts*2+" * \\brief \n"
		ret=ret+ts*2+" * \\details \n"
		for v in p["vars"]:
			ret=ret+ts*2+" * \\param [in] "+v["name"]+" - \n"
		if not p['type']:
			ret=ret+ts*2+" **/\n"
		elif p['type']=='void':
			ret=ret+ts*2+" * \\return None \n */\n"
		else
			ret=ret+ts*2+" * \\return - \n */\n"
		
		ret=ret+ts*2
		if p['type']:
			ret=ret+p['type']+' '
		ret=ret+p['name']+" ("
		i=1
		for v in p["vars"]:
			ret=ret+v['type']+" "+v['name']
			if i<len(p["vars"]):
				ret=ret+', '
		ret=ret+")"
		if p["modifier"]:
			ret=ret+" "+p["modifier"]
		ret=ret+";\n"
	return ret

def create_class(class_name,template_types=None, class_parents=None,
				 private_vars=None,protected_vars=None, 
				 private_setters=False, private_getters=False, protected_setters=False, protected_getters=False,
				 public_methods=None,protected_methods=None,private_methods=None,
				 tabstop=4):
	autodetected=[]
	for v in private_vars:
		for inc, t in stl:
			if any("std::"+substring in v['type'] for substring in t):
				if inc not in autodetected:
					autodetected.append(inc)
		else:
			if v['type'][0]=='Q':
				autodetected.append(v['type'])
	for v in protected_vars:
		for inc, t in stl:
			if any("std::"+substring in v['type'] for substring in t):
				if inc not in autodetected:
					autodetected.append(inc)
		else:
			if v['type'][0]=='Q':
				autodetected.append(v['type'])
	for func in public_methods:
		for v in func["vars"]:
			for inc, t in stl:
				if any("std::"+substring in v['type'] for substring in t):
					if inc not in autodetected:
						autodetected.append(inc)
			else:
				if v['type'][0]=='Q':
					autodetected.append(v['type'])
	ts=' '*tabstop
	ret="""/**
 * \\brief
 * \\details
 * */\n"""
	if template_types:
		ret=ret+"template <"
		i=1
		for t in template_types:
			ret=ret+t
			if i<len(template_types):
				ret=ret+', '
		ret=ret+">\nclass"+class_name;
	if class_parents:
		ret=ret+': '
		i=1
		for c in class_parents:
			ret=ret+c
			if i<len(class_parents):
				ret=ret+', '
			i=i+1
	ret=ret+"\n{\n"+ts+'public:\n';
	if public_methods:
		ret=ret+add_methods(public_methods, ts)
	sgetters=[]
	if protected_vars:
		for v in protected_vars:
			if protected_getters:
				sgetters.append({ 	"type" : v['type'],
									"name" : "get_"+v['name'],
									"vars" : None,
									"modifier": "const"})
			if protected_setters:
				sgetters.append({ 	"type" : 'void',
									"name" : "set_"+v['name'],
									"vars" : {
												'type': "const "+v['type']+'&',
												'name': '_'+var['name']
											 },
									"modifier": None})
	if private_vars:
		for v in private_vars:
			if private_getters:
				sgetters.append({ 	"type" : v['type'],
									"name" : "get_"+v['name'],
									"vars" : None,
									"modifier": "const"})
			if private_setters:
				sgetters.append({ 	"type" : 'void',
									"name" : "set_"+v['name'],
									"vars" : {
												'type': "const "+v['type']+'&',
												'name': '_'+var['name']
											 },
									"modifier": None})
	ret=ret+add_methods(sgetters, ts)
	ret=ret+'\n'+ts*2
	if protected_vars or protected_methods:
		ret=ret+'\n'+ts+'protected:'
	if protected_vars:
		for v in protected_vars:
			ret=ret+ts*2+v['type']+' '+v['name']+'; //!< \n'
	if protected_methods:
		ret=ret+add_methods(protected_methods, ts)
		ret=ret+'\n'+ts*2
	ret=ret+'\n'+ts+'private:\n'
	if private_vars:
		for v in private_vars:
			ret=ret+ts*2+v['type']+' '+v['name']+'; //!< \n'
	if private_methods:
		ret=ret+add_methods(private_methods, ts)
		ret=ret+'\n'+ts*2
	ret=ret+"\n};"
	return (autodetected, ret)

# vd=0 - not virtual
# vd=1 - virtual
# vd=2 - pure virtual
def basic_class_content(class_name, dd=0, dc=0, dm=0, vd=0, custom=None):
	ret=[]
	dummy={ "type" : None,
			"name" : class_name,
			"vars" : None,
			"modifier": None}
	if dd==0:
		ret.append(dummy)
	else:
		d1=dummy
		d1["modifier"]="= delete"
		ret.append(d1)
	if dc==0:
		ret.append({"type" : class_name,
					"name" : "operator=",
					"vars" : {
						"type" : "const "+class_name+"&",
						"name" : None
						},
					"modifier": None
					})
		d1=dummy
		d1["vars"]={"type" : "const "+class_name+"&",
					"name" : None}
		ret.append(d1)
	else:
		d1=dummy
		d1["vars"]={"type" : "const "+class_name+"&",
					"name" : None}
		d1["modifier"]="=delete"
		ret.append(d1)
	if dm==0:
		ret.append({"type" : class_name+"&",
					"name" : "operator=",
					"vars" : {
						"type" : "const "+class_name+"&&",
						"name" : None
						},
					"modifier": None
					})
		d1=dummy
		d1["vars"]={"type" : "const "+class_name+"&&",
					"name" : None}
		ret.append(d1)
	else:
		d1=dummy
		d1["vars"]={"type" : "const "+class_name+"&&",
					"name" : None}
		d1["modifier"]="=delete"
		ret.append(d1)
	if custom:
		for constructor_params in custom:
			d1=dummy
			d1["vars"]=constructor_params
			ret.append(d1)
	if vd==0:
		d1=dummy
		d1["name"]="~"+class_name
		ret.append(d1)
	elif vd==1:
		d1=dummy
		d1["name"]="~"+class_name
		ret.append(d1)
	elif vd==2:
		d1=dummy
		d1["name"]="~"+class_name
		d1["type"]="virtual"
		d1["modifier"]="=0"
		ret.append(d1)
	return ret

def bundle( class_name, author, email,
			namespaces_name=None,
			template_types=None, class_parents=None,
			dd=0, dc=0, dm=0, vd=0, custom=None,
			private_vars=None,protected_vars=None, 
			private_setters=False, private_getters=False, protected_setters=False, protected_getters=False,
			public_methods=None,protected_methods=None,private_methods=None,
			quinch=None, binch=None,
			tabstop=4):
	publics=basic_class_content(class_name, dd, dc,dm, vd, custom)
	publics.extend(public_methods)
	autodetected, blank=create_class(class_name,template_types, class_parents,
				 private_vars,protected_vars, 
				 private_setters, private_getters, protected_setters, protected_getters,
				 publics,protected_methods,private_methods,
				 tabstop)
	out=header(class_name, author, email)+includes(quinch,autodetected,binch)+namespace(namespace_name, blank, tabstop)
	return out
