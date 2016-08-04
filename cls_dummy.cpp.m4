define(`do', `/* Description: Implementation of the $1 class
 * Todo: 
 * Author: $5
 * Date:   $6
 * */
#include "$1.hpp"
#include <utility>
ifelse($2,`0',`
$1::$1() cls_parents()
{

}
',`')
$1::$1(int _a):
cls_parents(), a(_a)
{
	
}
ifelse($3,`0',`
$1::$1(const $1& from)
{
	
}

$1::$1($1& from)
{
	
}

$1 $1::operator=(const $1& from)
{
	if (this != &from)
	{
		
	}
	return *this;
}
'
,`')
ifelse($4,`0',`$1::$1($1&& from)
{
	*this = std::move(from);
}

$1& $1::operator=(const $1&& from)
{
	if (this != &from)
	{
		
	}
	return *this;
}'
,`')
$1::~$1()
{
	
}
//methods
')
do(cls,dd,dc,dm,auth,d)
