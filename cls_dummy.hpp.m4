define(`cls_dummy',`/**
 * Description: Declaration of the $1 class
 * Todo: 
 * Author: $4
 * Date:   $3
 * */
#pragma once
/**
 * \brief
 * \details
 * */
class $1 $2
{
	public:
		$1();
		explicit $1(int _a);
		//Copy
		$1(const $1&);
		$1($1&);
		$1 operator=(const $1&);
		//Move
		$1($1&&);
		$1& operator=(const $1&&);
		//Destruct
		~$1();
		//pub functions
	protected:
		
	private:
		/*data*/
		int a;
};')

cls_dummy(cls,cls_parents, d, auth)
