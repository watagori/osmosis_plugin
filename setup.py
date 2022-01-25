from setuptools import setup, find_packages

setup(
    name='osmosis_plugin',
    version='0.0.1',
    license='mit',
    description='plugin for osmosis',

    author='watagori',
    url='https://github.com/ca3-caaip/ca3-caaip',

    extras_require={
        "test": ["pytest", "pytest-cov", "senkalib"]
    },

    packages=find_packages('src'),
    package_dir={'': 'src'}
)
