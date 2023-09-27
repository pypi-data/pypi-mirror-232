from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="aws_assume_role_otp",
    version="0.1",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "aws-assume-role-otp=aws_assume_role_otp.main:app",
        ],
    },
)
