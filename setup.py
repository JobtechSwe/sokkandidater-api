from setuptools import setup

setup(
    name='sokkandidater',
    packages=['sokkandidater'],
    include_package_data=True,
    install_requires=[
        'valuestore', 'flask', 'flask-restplus', 'flask-cors', 'elasticsearch'
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"]
)
