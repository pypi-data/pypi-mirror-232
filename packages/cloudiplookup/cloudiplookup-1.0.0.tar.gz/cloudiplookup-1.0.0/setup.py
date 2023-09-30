import os, sys, shutil
from setuptools import setup
from setuptools.command.install import install
from distutils.sysconfig import get_python_lib
import shutil

try:
    with open("README.md",'r') as f:
        var_longDescription = f.readlines()
    var_longDescription = "".join(var_longDescription)         
except Exception as ERR:
    print("Erro ao ler o arquivo README.md %s"%(str(ERR)))
    sys.exit(1)

try:
    shutil.copy2("cloudiplookup/cloudiplookup.py", "./scripts/cloudiplookup")  
except Exception as ERR:
    print("Erro ao copiar arquivos para o diretório scripts. %s"%(str(ERR)))
    sys.exit(1)
    
target_directory = '/var/lib/cloudiplookup/'

class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        os.makedirs(os.path.dirname(target_directory), exist_ok=True)
        shutil.move('cloudiplookup/cloudiplookup.dat.gz', target_directory)
        shutil.move('cloudiplookup/cloudiplookup.json', target_directory)
        

setup(
    name='cloudiplookup',
    version='1.0.0',
    description='Cloud IP Lookup is a Pure Python application and library for Python 3 to verify which cloud platform a given IP address belongs to.',
    url='https://github.com/rabuchaim/cloudiplookup',
    author='Ricardo Abuchaim',
    author_email='ricardoabuchaim@gmail.com',
    maintainer='Ricardo Abuchaim',
    maintainer_email='ricardoabuchaim@gmail.com',
    bugtrack_url='https://github.com/rabuchaim/cloudiplookup/issues',
    license='MIT',
    packages=['cloudiplookup'],
    cmdclass={'install': CustomInstallCommand},    
    keywords=['cloudiplookup','cloud ip lookup','geoip','aws','azure','gcp','pure-python','purepython','pure python'],
    package_dir = {'cloudiplookup': 'cloudiplookup'},
    package_data={
        'cloudiplookup': ['cloudiplookup.py','cloudiplookup.dat.gz','cloudiplookup.json'],
    },
    scripts=['scripts/cloudiplookup'],
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Internet',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',  
        'Programming Language :: Python :: 3.11',          
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    include_package_data=True,
    long_description=f"""{var_longDescription}""",
    long_description_content_type='text/markdown',    
)
''