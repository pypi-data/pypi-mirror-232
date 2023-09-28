from setuptools import setup, find_packages

setup(
    name="mamp-sql-import",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here
        'mysql-connector-python',
        # any other dependencies that your project requires
    ],
    entry_points={
        'console_scripts': [
            'mamp-sql-import = MAMPSQLImport.main:main_function',
        ],
    },
    author="AutomateAlley",
    author_email="automatealley@gmail.com",
    description="A tool to quickly import databases in MAMP SQL",
    long_description_content_type="text/markdown",
    license="MIT",
    # url="https://github.com/yourusername/MAMPSQLImport",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    include_package_data=True,  # This will include non-code files like databases
    package_data={
        'MAMPSQLImport': ['dbs/*'],
    },
)
