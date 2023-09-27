
#
#	https://setuptools.pypa.io/en/latest/userguide/quickstart.html
#

from setuptools import setup, find_packages

#print ("PACKAGES:", find_packages ())

NAME = 'EDUCATOR'

DESCRIPTION = ''
try:
	with open ('src/README.rst') as f:
		DESCRIPTION = f.read ()
		print (DESCRIPTION)
except Exception as E:
	pass;

setup (
    name = NAME,
    version = '0.0.2',
    install_requires = [],
	package_dir = { NAME: 'src'},
	
	#
	#	PASSPORT
	#
	license = "pscl",
	long_description = DESCRIPTION,
	long_description_content_type = "text/markdown",
)