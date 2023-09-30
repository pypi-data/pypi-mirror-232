from setuptools import setup, find_packages

setup(
    name='NexaWatch',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'watchdog',
        'click',
        'rich',
    ],
    entry_points={
        'console_scripts': [
            'pywatcher=pywatcher.core:pywatcher',
        ],
    },
    author='Andrew Wade',
    author_email='awade75009@gmail.com',
    description='A nodemon alternative for Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/pywatcher',
)
