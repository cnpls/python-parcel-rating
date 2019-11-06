from parcel_rating import __version__
from setuptools import setup

long_description = ''
with open('./README.md') as f:
    long_description = f.read()

setup(name='parcel_rating',
    version=__version__,
    description='Package for rating parcel shipments.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/christopherpryer/python-parcel-rating',
    author='Chris Pryer',
    author_email='christophpryer@gmail.com',
    license='PUBLIC',
    packages=['parcel_rating'],
    zip_safe=False)
