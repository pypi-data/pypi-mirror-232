from setuptools import setup, find_packages

setup(
    name='mycliapper132',
    version='0.7',
    packages=find_packages(),
    install_requires=[
        'click',
        'databricks-sql-connector',
        'json',
        'hashlib',
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
