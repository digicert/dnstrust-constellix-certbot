from setuptools import setup
from setuptools import find_packages

version = "0.3.1"

install_requires = [
    "acme>=0.29.0",
    "certbot>=2.12.0,<4.0",
    "setuptools",
    "requests",
    "mock",
    "requests-mock",
]

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md")) as f:
    long_description = f.read()

setup(
    name="certbot-dns-constellix",
    version=version,
    description="Constellix DNS Authenticator plugin for Certbot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/digicert/dnstrust-constellix-certbot",
    author="Jessica Smith",
    author_email="jessica.smith@digicert.com",
    license="Apache License 2.0",
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        "certbot.plugins": [
            "dns-constellix = certbot_dns_constellix.dns_constellix:Authenticator"
        ]
    },
    test_suite="certbot_dns_constellix",
)
