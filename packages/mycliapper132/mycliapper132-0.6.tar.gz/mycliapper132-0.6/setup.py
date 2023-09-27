from setuptools import setup, find_packages

setup(
    name='mycliapper132',
    version='0.6',
    packages=find_packages(),
    install_requires=[
        'click',
        'databricks-sql-connector',
        'json',
        'hashlib',
        'hmac',
        'base64',
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
