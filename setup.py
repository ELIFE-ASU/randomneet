from setuptools import setup

with open("README.md") as f:
    README = f.read()

with open("LICENSE") as f:
    LICENSE = f.read()

setup(
    name='neet',
    version='0.1.0',
    description='Randomizing Neet networks',
    maintainer='Douglas G. Moore',
    maintainer_email='doug@dglmoore.com',
    url='https://github.com/elife-asu/randomneet',
    license=LICENSE,
    install_requires=['neet', 'networkx', 'numpy'],
    setup_requires=['green'],
    packages=['randomneet'],
    test_suite='test',
    platforms=['Windows', 'OS X', 'Linux']
)
