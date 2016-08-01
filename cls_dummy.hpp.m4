define(`cls_dummy',`/**
 * Description: Declaration of the $1 class
 * Todo: 
 * Author: $2
 * Date:   $3
 * */
#pragma once
/**
 * \brief
 * \details
 * */
class $1 $4
{
	public:')

define(`constructors',`
		ifelse($2,`0',`$1()';,`$1() = delete;')
		explicit $1(int _a);
		//Copy
		ifelse($3,`0',`$1 operator=(const $1&);',`')
		ifelse($3,`0',`$1(const $1&);',`$1(const $1&) = delete;')
		ifelse($3,`0',`$1($1&);',`$1($1&) = delete;')
		//Move
		ifelse($4,`0',`$1& operator=(const $1&&);',`')
		ifelse($4,`0',`$1($1&&)',`$1($1&&) = delete;')
		//Destruct
		~$1();
		//pub functions
	protected:
		
	private:
		/*data*/
		int a;
};')
cls_dummy(cls,d,auth,cls_parents)
constructors(cls,dd,dc,dm)
