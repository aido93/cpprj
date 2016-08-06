# cpprj
Simple CLI UML analog for C++

**Dependencies**

bash

sed

m4

cmake

doxygen

dot (for diagrams in Doxygen)

**Install**

git clone https://github.com/aido93/cpprj

cd cpprj && chmod +x cclass cpprj rmclass install.sh && ./install.sh

How to use:

**1) create project**

  cp ~/projects/dummy ~/projects/[project name]
  
  vim ~/projects/[project name] #edit configuration
  
  cpprj ~/projects/[project name]
  
**2) create class architecture using script like**


/bin/bash

cclass par1 -dm -vo -as -ag "int* index;const char* name;std::string s;" -vi -as -ag "boost::string bs;uint32_t loop;"

cclass par2 -dm -vo -as -ag "int* index;const char* name;std::string s;" -vi -as -ag "boost::string bs;uint32_t loop;"

cclass child par1 par2 -dm -vo -as -ag "int* index;const char* name;std::string s;" -vi -as -ag "boost::string bs;uint32_t
loop;"

cclass class_name [parents_name] [[-t] templates_names] [-d options] [-vo [-as] [-ag]] [-vi [-as] [-ag]]:

-t  - template class [with list of template names]

-dd - delete (D)efault constructor

-dc - delete (C)opy constructor

-dm - delete (M)ove constructor



-vo - (V)ariables in the pr(O)tected section

-vi - (V)ariables in the pr(I)vate section

-as - (A)dd (S)etters

-ag - (A)dd (G)etters

**3) If you wanna delete some class in the project, use:**

rmclass [class_name]

**4) If you wanna add some method to the class, use:**

ccam [class_name] -[iou] name return type -a arguments [-t template types]

-i - pr(I)vate
-o - pr(O)tected
-u - p(U)blic

if return type is empty then uses 'void' type

template types - templates of the class

**Note:** 

list of variables must be created using some rules:

1) references and pointers: only 'int* x' or 'char& y' type. Not 'int *x' or 'char & y'

2) Semicolon must have no spaces before and after itself.
