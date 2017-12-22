from setuptools import setup, find_packages 

setup(	name='cpprj', version='0.1', 
		description='C++ project creator', long_description='C++ code generation', 
		classifiers=[ 	'Development Status :: 3 - Alpha', 
						'License :: OSI Approved :: MIT License', 
						'Programming Language :: Python :: 3.5', 
						'Topic :: Text Processing :: Linguistic', ], 
		keywords='c++ codegen bigredbutton', 
		url='http://github.com/aido93/cpprj', author='aido', 
		author_email='aidos.tanatos@gmail.com', 
		license='GPLv2', 
		packages=find_packages(), 
		install_requires=[ 'python-magic', ], 
		include_package_data=True, 
		zip_safe=False)
