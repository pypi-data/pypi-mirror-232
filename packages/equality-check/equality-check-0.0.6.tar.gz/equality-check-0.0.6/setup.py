
#
#	https://setuptools.pypa.io/en/latest/userguide/quickstart.html
#
#	https://github.com/pypa/sampleproject/blob/db5806e0a3204034c51b1c00dde7d5eb3fa2532e/setup.py
#

from setuptools import setup, find_packages

#print ("PACKAGES:", find_packages ())

NAME = 'equality-check'

DESCRIPTION = ''
try:
	with open ('src/README.rst') as f:
		DESCRIPTION = f.read ()
	print (DESCRIPTION)
except Exception as E:
	pass;

setup (
    name = NAME,
    version = '0.0.6',
    install_requires = [],
	
	license = "pscl",
	long_description = DESCRIPTION,
	long_description_content_type = "text/markdown",
	
	package_dir = { NAME: 'src'},
	#package_data = {
	#	NAME: [ 'DATA/**/*' ]
	#}
)