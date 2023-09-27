from setuptools import setup, find_packages

setup(
    name = "RefractXAI",
    version = "1.0.0",
    packages = find_packages(),
    install_requires = [
        "pandas-profiling==3.6.6",
        "bs4==0.0.1"
    ],
    include_package_data=True
)