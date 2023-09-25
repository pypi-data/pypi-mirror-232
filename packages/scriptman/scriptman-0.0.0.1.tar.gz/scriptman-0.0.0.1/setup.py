import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

VERSION = "0.0.0.1"
DESCRIPTION = "Script Manager assists with managing python scripts."

setup(
    name="scriptman",
    version=VERSION,
    author="Nelson Ombuya",
    description=DESCRIPTION,
    packages=find_packages(),
    author_email="nelson.ombuya@zohomail.com",
    long_description_content_type="text/markdown",
    keywords=["python", "scripts", "etl", "selenium"],
    install_requires=[
        "attrs",
        "certifi",
        "cffi",
        "charset-normalizer",
        "colorama",
        "exception-group",
        "greenlet",
        "h11",
        "idna",
        "numpy",
        "outcome",
        "packaging",
        "pandas",
        "pycparser",
        "pyodbc",
        "PySocks",
        "python-dateutil",
        "python-dotenv",
        "pytz",
        "requests",
        "selenium",
        "six",
        "sniffio",
        "sortedcontainers",
        "tqdm",
        "trio",
        "trio-websocket",
        "typing-extensions",
        "tzdata",
        "urllib3",
        "webdriver-manager",
        "wsproto",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
