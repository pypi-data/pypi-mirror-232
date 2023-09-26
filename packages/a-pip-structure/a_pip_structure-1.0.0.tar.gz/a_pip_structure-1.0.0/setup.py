

from 	setuptools import setup, find_packages
import 	pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup (
    name 				= 	"a_pip_structure",
    version 			= 	"1.0.0",
	packages 			= 	find_packages (where = "STRUCTURE"),
	python_requires		=	">=3.7, <4",
	install_requires	=	[ "flask" ],
	
    description = "",
    long_description = "",
    long_description_content_type="text/markdown",
    # url="",
	
	
    #author = "", 
    #author_email = "",
    #classifiers = [],
    #keywords = "",
    #package_dir = {"": "src"}, 

    #extras_require={
    #    "dev": [ "check-manifest"],
    #    "test": [ "coverage" ],
    #},
	
	# package_data
	# entry_points

    project_urls = {}
)