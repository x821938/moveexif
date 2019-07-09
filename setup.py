'''
Created on 9. jul. 2019

@author: Alex
'''
from setuptools import setup

setup(
    name='exifmove',
    version='0.1',
    py_modules=['exifmove'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        exifmove=exifmove:exifmove
    ''',
)