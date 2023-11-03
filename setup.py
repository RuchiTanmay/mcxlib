import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='mcxlib',
    packages=setuptools.find_packages(),
    version='0.1',
    include_package_data=True,
    description='python library to get MCX India data',
    long_description=long_description,
    long_description_content_type="text/markdown", author='RuchiTanmay',
    author_email='ruchitanmay@gmail.com',
    url='https://github.com/RuchiTanmay/mcxlib',
    install_requires=['requests', 'pandas'],
    keywords=['mcx', 'mcx india', 'python', 'mcx data', 'mcx history data', 'commodity', 'mcx python',
              'mcx python library', 'mcx library'],
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
