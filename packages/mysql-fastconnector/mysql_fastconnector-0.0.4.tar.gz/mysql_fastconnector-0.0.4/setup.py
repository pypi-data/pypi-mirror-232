import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "mysql_fastconnector",
    version = "0.0.4",
    author = "ilayaraja",
    author_email = "ilayaraja.python@gmail.com",
    description = "it helps to connect mysql and do CURD action easily ",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/ilayaraja1984/mysqleasyquery",
    project_urls = {
        "Bug Tracker": "https://github.com/ilayaraja1984/mysqleasyquery/issues",
    },
    install_requires=[
        'mysql-connector-python==8.1.0',
        'mysqlclient==2.0.3',
    ],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.6")


    