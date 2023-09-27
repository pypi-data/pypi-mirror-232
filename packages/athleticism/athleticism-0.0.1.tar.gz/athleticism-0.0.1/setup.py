


#
#	https://setuptools.pypa.io/en/latest/userguide/quickstart.html
#

from setuptools import setup, find_packages

#print ("PACKAGES:", find_packages ())

NAME = 'athleticism'

setup (
    name = NAME,
    version = '0.0.1',
    install_requires = [],
	
	package_dir = { NAME: 'src'},
	#package_data = {
	#	NAME: [ 'DATA/**/*' ]
	#}
)