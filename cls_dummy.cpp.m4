define(`do', `/* Description: Implementation of the $cls class
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
a(_a), cls_parents()
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
	
}')
do(cls,dd,dc,dm,auth,d)
