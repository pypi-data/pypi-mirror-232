import setuptools 
setuptools.setup( 
    name='Test1_CRMA',
    version='0.2',
    author="Srinivasan Ravindran",
    author_email="r.srinivasan3@gmail.com",
    description="Extract CRMA Metadata",
    packages=setuptools.find_packages(),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[ "Programming Language :: Python :: 3", "License :: OSI Approved :: MIT License", "Operating System :: OS Independent", ],)