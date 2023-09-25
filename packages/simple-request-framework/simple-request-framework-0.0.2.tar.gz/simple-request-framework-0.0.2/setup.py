from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='simple-request-framework',
    version='0.0.2',
    author='0chencc',
    author_email='admin@hi-ourlife.com',
    url='https://github.com/0Chencc/',
    description=u'Encapsulates a framework for requests to request json corresponding package api, while saving the results locally',
    packages=['SimpleRequestFramework'],
    keywords=['requests', 'framework', 'api', 'json', 'save'],
    license='GNU GPLv3 License',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    install_requires=[
        'requests[socks]',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
