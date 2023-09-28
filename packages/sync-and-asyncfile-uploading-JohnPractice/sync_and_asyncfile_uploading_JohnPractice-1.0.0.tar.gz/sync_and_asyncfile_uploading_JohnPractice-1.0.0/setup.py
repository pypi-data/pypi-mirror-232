from setuptools import setup, find_packages

VERSION = "1.0.0"
DESCRIPTION = "Useful functions for uploading file "
LONG_DESCRIPTION = (
    "Useful functions for uploading file with supporting `sync` and `async`"
)

# Setting up
setup(
    # the name must match the folder name
    name="sync_and_asyncfile_uploading_JohnPractice",
    version=VERSION,
    author="John Practice",
    author_email="rezamosavian1014@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["aiohttp"],  # add any additional packages that
    keywords=["python", "first package"],
    classifiers=[
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
)
