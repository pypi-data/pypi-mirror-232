from setuptools import setup, find_packages

setup(
    name = "RefractXAI",
    version = "1.0.3",
    packages = find_packages(),
    install_requires = [
        "bs4==0.0.1"
    ],
    include_package_data=True
)