import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "postgresql_fastquery",
    version = "0.0.3",
    author = "ilayaraja",
    author_email = "ilayaraja.python@gmail.com",
    description = "it helps to connect postgresql and do CURD action easily ",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/ilayaraja1984/posgresql_fastquery",
    project_urls = {
        "Bug Tracker": "https://github.com/ilayaraja1984/posgresql_fastquery/issues",
    },
    install_requires=[
        'psycopg2',
    ],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.6")


    