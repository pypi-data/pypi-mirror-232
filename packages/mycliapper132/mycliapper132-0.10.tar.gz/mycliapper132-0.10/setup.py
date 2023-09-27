from setuptools import setup, find_packages

setup(
    name='mycliapper132',
    version='0.10',
    packages=find_packages(),
    install_requires=[
        'click',
        'databricks-sql-connector',
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
