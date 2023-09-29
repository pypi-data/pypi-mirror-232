from setuptools import setup, find_packages

setup(
    name='Subdominator',
    version='1.0.2',
    author='D.Sanjai Kumar',
    author_email='bughunterz0047@gmail.com',
    description='Subdominator an ultimate subdomain enumeration tool',
    packages=find_packages(),
    install_requires=[
        'censys==2.2.5',
        'colorama==0.4.4',
        'httpx==0.24.1',
        'pywebio==1.8.2',
        'PyYAML==6.0.1',
        'requests==2.31.0',
        'argparse==1.4.0',
    ],
    entry_points={
        'console_scripts': [
            'subdominator = subdominator.subdominator:main'
        ]
    },
    package_data={
        'subdominator': ['config_keys.yaml'],
    }
)
