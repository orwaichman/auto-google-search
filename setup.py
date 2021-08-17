from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()
with open('README.md') as f:
    readme = f.read()

setup(
    name="google-search",
    version="0.1.0",
    description="Get Google search results programmatically",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/orwaichman/auto-google-search",
    author="Or Waichman",
    author_email="",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["google_search"],
    include_package_data=True,
    install_requires=required
)
