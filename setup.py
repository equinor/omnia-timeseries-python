import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="omnia-timeseries-api",
    version="1.0.0",
    author="Equinor Omnia Industrial IoT Team",
    description="Official Python SDK for the Omnia Timeseries API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/equinor/omnia-timeseries-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        "azure-identity==1.5.0"
    ]
)