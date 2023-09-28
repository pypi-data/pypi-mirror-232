from setuptools import setup, find_packages

setup(
    name='mycliapper2',
    version='0.12',
    packages=find_packages(),
    install_requires=[
        'click',
        'databricks-sql-connector',
        'requests',
        'pytz',
        'typing',
        'datetime'
    ],
    entry_points={
        'console_scripts': [
            'mycliapp = mycliapp.main:hello',
        ],
    },
)
