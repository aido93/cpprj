# cpprj
Simple CLI UML analog for C++

How to use:

1) create project

  cp ~/projects/dummy ~/projects/[project name]
  
  vim ~/projects/[project name] #edit configuration
  
  cpprj ~/projects/[project name]
  
2) create class architecture using script like

#!/bin/bash

cclass -dm par1 -vo -as -ag "int* index;const char* name;std::string s;" -vi -as -ag "boost::string bs;uint32_t loop;"

cclass -dm par2 -vo -as -ag "int* index;const char* name;std::string s;" -vi -as -ag "boost::string bs;uint32_t loop;"

cclass -dm child par1 par2 -vo -as -ag "int* index;const char* name;std::string s;" -vi -as -ag "boost::string bs;uint32_t
loop;"

cclass [-d options] class_name [parents_name] [-vo [-as] [-ag]] [-vi [-as] [-ag]]:

-dd - delete (D)efault constructor

-dc - delete (C)opy constructor

-dm - delete (M)ove constructor



-vo - (V)ariables in the pr(O)tected section

-vi - (V)ariables in the pr(I)vate section

-as - (A)dd (S)etters

-ag - (A)dd (G)etters
