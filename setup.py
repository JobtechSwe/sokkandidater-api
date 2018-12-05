from setuptools import setup, find_packages

setup(
    name='sokkandidater',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'valuestore', 'flask', 'flask-restplus', 'flask-cors', 'elasticsearch'
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"]
)
