
#
#	https://setuptools.pypa.io/en/latest/userguide/quickstart.html
#

from setuptools import setup, find_packages


print ("PACKAGES:", find_packages ())

setup(
    name = 'python-food-1',
    version = '1.0.0',
    install_requires = [
        'click'
    ],
	
	package_dir = {'src': 'src'},
	package_data = {
		'src': [ 'DATA/**/*' ]
	}
)