from setuptools import setup, find_packages

setup(
    name='metabeaver',
    version='0.2.0', # Major, minor, patch
    packages=find_packages(exclude=['Testing', '*.xlsx', '*.xls']),
    install_requires=[
        'numpy',
        'pandas',
        'google-cloud-core',
        'google-cloud-bigquery',
    ],
    description='Beaverish about data.',
    author='Luke Anthony Pollen',
    author_email='luke@pollenanalytics.com',
    url='https://github.com/rainbowpusheenthe3rd/dataBeaver',
)


##### ERRATA #####

"""
   ______
  //    \\__
(||      `--`)
  \\_/||\_/`

"""

### Create the wheel and the tar in dist folder
#python setup.py sdist bdist_wheel

### Upload to PyPi, using twine
#twine upload dist/*
#twine upload *

### Where does Twine live?
#pip show twine
#dir /s twine.exe

##### ERRATA #####