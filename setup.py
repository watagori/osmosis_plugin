from setuptools import find_packages, setup

setup(
    name="osmosis_plugin",
    version="0.0.1",
    license="mit",
    description="plugin for osmosis",
    author="watagori",
    url="https://github.com/ca3-caaip/ca3-caaip",
    extras_require={
        "test": [
            "pytest",
            "pytest-cov",
            "black",
            "pre-commit",
            "flake8",
            "isort",
            "pytest-mock",
            "senkalib",
        ],
        "main": ["senkalib", "pandas"],
    },
    packages=find_packages("src"),
    package_dir={"": "src"},
)
