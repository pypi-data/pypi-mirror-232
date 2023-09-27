from setuptools import setup, find_packages

setup(
    name='mycliapper132',
    version='0.8',
    packages=find_packages(),
    install_requires=[
        'click',
        'databricks-sql-connector',
        'json',
        'hmac',
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
