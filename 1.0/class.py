import date
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
"""+ts+"\n};\n"

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
				 public_methods=None,protected_methods=None,private_methods=None,
				 tabstop=4):
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
	return ret

# vd=0 - not virtual
# vd=1 - virtual
# vd=2 - pure virtual
def constructors(class_name, dd=0, dc=0, dm=0, vd=0, custom=None):
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
		d1["modifier"]=" =0"
		ret.append(d1)
	return ret
