import setuptools

# PRODUCTION setup.py: name, version, install_requires, packages only
setuptools.setup(
    name='github-gists-json',
    version='1.0.2',
    install_requires=open('requirements.txt').read().splitlines(),
    packages=setuptools.find_packages()
)