define(`do', `/* Description: Implementation of the $1 class
 * Todo: 
 * Author: $5
 * Date:   $6
 * */
#include "$1.hpp"
#include <utility>
ifelse($2,`0',`
$7 
$1$8::$1() cls_parents()
{

}
',`')
$7
$1$8::$1(uint32_t _a):
cls_parents(), a(_a)
{
	
}
ifelse($3,`0',`
$7
$1$8::$1(const $1$8& from) : 
cls_parents()
{
	
}

$7
$1$8::$1($1$8& from) : 
cls_parents()
{
	
}

$7
$1 $1$8::operator=(const $1$8& from)
{
	if (this != &from)
	{
		
	}
	return *this;
}
'
,`')
ifelse($4,`0',`$7
$1$8::$1($1$8&& from)
{
	*this = std::move(from);
}
$7
$1& $1$8::operator=(const $1$8&& from)
{
	if (this != &from)
	{
		
	}
	return *this;
}'
,`')
$7
$1$8::~$1()
{
	
}
//methods
')
do(cls,dd,dc,dm,auth,d,temp1,temp2)
