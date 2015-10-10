from setuptools import setup
from setuptools import find_packages

import time
_version = '0.1.0.%s' % int(time.time())
_packages = find_packages(where='.')

install_requires = [
    'Django>=1.8,<1.9',
    'dj-database-url==0.3.0',
    'psycopg2==2.5.2',
    'celery[redis]',
    'raven',
    'requests==2.7.0',
    'geopy'
]

setup(
    name='roundtwo',
    version=_version,
    description="A simple airplane router. For ground delays' sake.",
    author='Joao Figueiredo',
    author_email='me@j1fig.com',
    url='https://j1fig.com',
    install_requires=install_requires,
    packages=_packages,
    include_package_data=True,
)
