from setuptools import setup, find_packages

setup(
    name='hashcracker',
    version='0.0.01 Beta',
    description='A Python tool for analyzing and cracking hashes.',
    author='Md. Shaykhul Islam',
    author_email='shaykhul@2004.com',
    url='https://github.com/SHAYKHUL/hashcracker',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'bcrypt>=3.2.0', 
        'pyopencl>=2022.1.1', 
        'numpy>=1.21.0',  
    ],
    entry_points={
        'console_scripts': [
            'hashcracker = hashcracker.wrapper:main',
        ],
    },
)
