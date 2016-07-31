/**
 * Description: Implementation of the $cls class
 * Todo: 
 * Author: $auth
 * Date:   $d
 * */
#include "$cls.hpp"
#include <utility>

$cls::$cls():
	$cls_parents()
{

}

$cls::$cls(int _a):
a(_a), $cls_parents()
{
	
}

$cls::$cls(const $cls& from)
{
	
}

$cls::$cls($cls& from)
{
	
}

$cls::$cls($cls&& from)
{
	*this = std::move(from);
}

$cls $cls::operator=(const $cls& from)
{
	if (this != &from)
	{
		
	}
	return *this;
}

$cls& $cls::operator=(const $cls&& from)
{
	if (this != &from)
	{
		
	}
	return *this;
}

$cls::~$cls()
{
	
}
