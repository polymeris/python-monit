from distutils.core import setup
setup(
    name='monit',
    description='Interface to the Monit system manager and monitor (http://mmonit.com/monit/)',
    version='0.4',
    author='Camilo Polymeris',
    author_email='cpolymeris@gmail.com',
    url='https://github.com/polymeris/python-monit',
    py_modules=['monit'],
    requires=['requests']
    )
