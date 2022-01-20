from setuptools import setup, find_packages

setup(
    name='pancake_plugin',
    version='0.0.1',
    license='mit',
    description='plugin for osmosis',

    author='watagori',
    url='https://github.com/ca3-caaip/ca3-caaip',

    install_requires=[
        # Github Private Repository - needs entry in `dependency_links`
        'senkalib'
    ],

    packages=find_packages('src'),
    package_dir={'': 'src'}
)
