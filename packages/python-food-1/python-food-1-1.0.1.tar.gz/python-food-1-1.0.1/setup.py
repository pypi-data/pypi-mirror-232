
#
#	https://setuptools.pypa.io/en/latest/userguide/quickstart.html
#

from setuptools import setup, find_packages


print ("PACKAGES:", find_packages ())

NAME = 'python-food-1'

setup (
    name = NAME,
    version = '1.0.1',
    install_requires = [
        'click'
    ],
	
	package_dir = { NAME: 'src'},
	package_data = {
		NAME: [ 'DATA/**/*' ]
	}
)