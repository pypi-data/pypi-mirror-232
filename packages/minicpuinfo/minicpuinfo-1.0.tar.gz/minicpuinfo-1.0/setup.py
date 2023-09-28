from setuptools import setup, find_packages
with open('requirements.txt','r') as f:
    requers = f.read().splitlines()

setup(
    name="minicpuinfo",
    version="1.0",
    author='sahayavalan',
    author_email='sahayavalanj1@gmail.com',
    description='minicpu is cpuinfo mini version tool',
    packages=find_packages(),
    install_requires=requers,

    entry_points={
        'console_scripts': [
            'minicpuinfo = cpuinfo.minicpuinfo:main',
        ],
    },
)
