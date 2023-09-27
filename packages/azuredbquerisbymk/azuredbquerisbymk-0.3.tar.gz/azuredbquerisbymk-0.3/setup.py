from setuptools import setup, find_packages

setup(
    name='azuredbquerisbymk',
    version='0.3',
    packages=find_packages(),
    install_requires=[

    'pyodbc>=4.0.39',
    'pandas>=2.1.0',
    'streamlit>=1.26.0',
    'datetime>=5.2'
        
    ],
)
