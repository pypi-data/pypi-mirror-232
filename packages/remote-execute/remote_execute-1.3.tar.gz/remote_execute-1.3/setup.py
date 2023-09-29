from setuptools import setup, find_packages

setup(
    name='remote_execute',
    version='1.3',
    description='Execute remote code fetched from a URL',
    author='WavaDev',
    author_email='admin@wavadev.xyz',
    packages=find_packages(),
    install_requires=[
        'requests',
        'python-dotenv',
    ],
)