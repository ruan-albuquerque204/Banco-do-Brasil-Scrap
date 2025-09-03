from setuptools import setup, find_packages

setup(
    name='brasil',
    version='0.1.0',
    description='realiza procedimentos no website do banco do brasil',
    author='Ruan de Albuquerque Santos',
    author_email='ruanalbuquerque204@gmail.com',
    packages=find_packages(exclude=('examples*', 'tests*', 'venv')),
    install_requires=['playwright', 'playwright-stealth'],
    include_package_data=True,
    zip_safe=False
)