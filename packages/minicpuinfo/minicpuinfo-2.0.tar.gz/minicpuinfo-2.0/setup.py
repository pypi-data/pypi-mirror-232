import os
from setuptools import setup, find_packages

# with open('requirements.txt', 'r') as f:
#     requers = f.read().splitlines()
# reqs=os.popen('pipreqs cpuinfo').read().splitlines()

reqs=['pyfiglet','psutils','OptionParser','setuptools']

setup(
    name="minicpuinfo",
    version="2.0",
    author='sahayavalan',
    author_email='sahayavalanj1@gmail.com',
    description='minicpu is cpuinfo mini version tool',
    packages=find_packages(),
    long_description='',
    install_requires=reqs,

    entry_points={
        'console_scripts': [
            'minicpuinfo=cpuinfo.minicpuinfo:main',
        ],
    },
)