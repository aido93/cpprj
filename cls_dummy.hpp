/**
 * Description: Declaration of the $cls class
 * Todo: 
 * Author: $auth
 * Date:   $d
 * */
#ifndef CLS_HPP
#define CLS_HPP

/**
 * \brief
 * \details
 * */
class $cls $cls_parents
{
	public:
		$cls()=delete;
		explicit $cls(int _a);
		//Copy
		$cls(const $cls&);
		$cls($cls&);
		$cls  operator=(const $cls&);
		//Move
		$cls($cls&&);
		$cls& operator=(const $cls&&);
		//Destruct
		~$cls();
	protected:
		
	private:
		/*data*/
		int a;
};

#endif
