from setuptools import setup, find_packages

VERSION = '0.0.7' 
DESCRIPTION = 'Package for parsing a PDF file and extracting data from it'
LONG_DESCRIPTION = 'Package for parsing a PDF file and extracting data from it'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="PDFPro", 
        version=VERSION,
        author="Maaz Musa",
        author_email="maazbin-musa@uiowa.edu",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'PDF'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)