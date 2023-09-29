from setuptools import setup, find_packages
import subprocess

setup(
    name='cardia',
    version=subprocess.check_output(['git', 'describe', '--tags']).decode('utf-8').strip().lstrip('v').split('-')[0],
    packages=find_packages(),
    install_requires=[
        # Add any required dependencies here
    ],
    entry_points={
        'console_scripts': [
            'cardia = cardia.__main__:main',
        ],
    },
    author='Kevin Jacobs',
    author_email='mail@kevinjacobs.nl',
    description='Python library for intelligent code card generation.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/kevin91nl/cardia',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
    ],
)
