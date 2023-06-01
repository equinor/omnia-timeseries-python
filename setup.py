from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="omnia-timeseries-api",
    version="1.1.6",

    author="Equinor Omnia Industrial IoT Team",
    description="Official Python SDK for the Omnia Timeseries API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/equinor/omnia-timeseries-python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        "azure-identity>=1.10.0",
        "pytest",
        "requests_mock",
        "cryptography>=3.2",
        "pyjwt>=2.4.0", 
        "opentelemetry-instrumentation-requests>=0.31b0"
    ]
)
