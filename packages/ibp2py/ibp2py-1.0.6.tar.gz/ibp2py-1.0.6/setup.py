from setuptools import setup, find_packages

with open ('README.md', 'r') as arq:
    readme = arq.read()

setup(
    name='ibp2py',
    version='1.0.6',
    author='Pedro Rastha',
    author_email='pedrorastha@gmail.com',
    description='SAP Data Retrieval and Processing Library for IBP',
    long_description= readme,
    long_description_content_type='text/markdown',
    url='https://github.com/pedrorastha/ibp2py',
    keywords='SAP IBP API ODATA',
    packages=['ibp2py'],
    install_requires=[
        'requests>=2.20.0',
        'pandas>=1.2.0',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        ],
)