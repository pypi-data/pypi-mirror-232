import setuptools

# PRODUCTION setup.py: name, version, install_requires, packages only
setuptools.setup(
    name='github-repos-json',
    version='0.0.0',
    install_requires=open('requirements.txt').read().splitlines(),
    packages=setuptools.find_packages()
)