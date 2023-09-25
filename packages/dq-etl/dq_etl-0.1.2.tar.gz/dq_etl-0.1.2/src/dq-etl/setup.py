from setuptools import setup, find_packages

setup(
    name='dq-etl',
    version='0.1.0',
    description='ETL framework',
    author='bavid lynx',
    author_email='shivakharbanda11@gmail.com',
    packages=find_packages(),
    install_requires=[
        'psycopg2>=2.9.7,<3.0.0',
        'pyarrow>=13.0.0,<14.0.0',
        'pandas==1.3.3',
        'mysql-connector-python>=8.1.0,<9.0.0',
        'python-dotenv>=1.0.0,<2.0.0',
        'tqdm>=4.66.1,<5.0.0',
        'tenacity>=8.2.3,<9.0.0',
    ],
    python_requires='>=3.9,<4.0',
    classifiers=[
        'Programming Language :: Python :: 3.9',
    ],
)
