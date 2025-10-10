#!/usr/bin/env python
from setuptools import setup
import re
import os


def get_version():
    fn = os.path.join(os.path.dirname(__file__), "autopager", "__init__.py")
    with open(fn) as f:
        return re.findall(r"__version__ = '([\d\.\w]+)'", f.read())[0]


setup(
    name='autopager',
    version=get_version(),
    author='Mikhail Korobov',
    author_email='kmike84@gmail.com',
    license='MIT license',
    long_description=open('README.rst').read() + "\n\n" + open('CHANGES.rst').read(),
    description="Detect and classify pagination links on web pages",
    url='https://github.com/TeamHG-Memex/autopager',
    zip_safe=False,
    packages=['autopager'],
    python_requires='>=3.8',
    install_requires=[
        "w3lib >= 1.13.0",
        "parsel >= 1.0.1",
        "tldextract",
        "docopt",
        "sklearn-crfsuite >= 0.3.3",
    ],
    package_data={
        'autopager': [
            'autopager.crf',
            # 'data/*.csv',
            # 'data/html/*.html'
        ],
    },
    # extras_require={
    #     'with-deps': [
    #         # 'scikit-learn >= 0.17',
    #         # 'scipy',
    #         'sklearn-crfsuite >= 0.3.1',
    #     ],
    # },
    entry_points={
        'console_scripts': ['autopager = autopager.__main__:main']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
