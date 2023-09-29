from setuptools import setup, find_packages

setup(
    name='dbtlogs-prebuilt',
    version='0.6',
    packages=find_packages(),
    install_requires=[
        'click',
        'databricks-sql-connector',
        'requests',
        'pytz',
        'typing',
        'datetime',
        'apache-airflow'
    ],
    entry_points={
        'console_scripts': [
            'dbtlog = dbtlogs.main:dbtlog',
        ],
    },
)
