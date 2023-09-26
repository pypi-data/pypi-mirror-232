

from 	setuptools import setup, find_packages


setup (
    name = "a_pip_structure",
    version = "1.0.3",
	
	packages = find_packages (
		where = "src"
	),
	
	
	python_requires	= ">=3.7, <4",
	install_requires = [ "flask" ],
	
    description = "",
    long_description = "",
    long_description_content_type = "text/markdown",
    # url="",
		
	keywords = "structure",
	package_dir = { "": "src" }, 
	
    #author = "", 
    #author_email = "",
    #classifiers = [],
    
	

    #extras_require={
    #    "dev": [ "check-manifest"],
    #    "test": [ "coverage" ],
    #},
	
	# package_data
	# entry_points

    project_urls = {}
)