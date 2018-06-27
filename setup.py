from setuptools import setup

setup(
    name='OxygenRM', 
    version='0.1', 
    description='''
        A simple ORM library, for doing database manipulations without too much complication. Its goal is to be lightweight
        and very simple to use, so it reduces any cognitive overhead. It's inspired by Laravel's Eloquent ORM.
        At first, it should support SQLite, MariaDB and Posgresql, but support for other databases may be added with time.
    ''', 
    install_requires=[], 
    packages=['OxygenRM'], 
)