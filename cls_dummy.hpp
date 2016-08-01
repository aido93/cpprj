/**
 * Description: Declaration of the $cls class
 * Todo: 
 * Author: $auth
 * Date:   $d
 * */
#pragma once
/**
 * \brief
 * \details
 * */
class $cls $cls_parents
{
	public:
		$cls();
		explicit $cls(int _a);
		//Copy
		$cls(const $cls&);
		$cls($cls&);
		$cls operator=(const $cls&);
		//Move
		$cls($cls&&);
		$cls& operator=(const $cls&&);
		//Destruct
		~$cls();
		//pub functions
	protected:
		
	private:
		/*data*/
		int a;
};
