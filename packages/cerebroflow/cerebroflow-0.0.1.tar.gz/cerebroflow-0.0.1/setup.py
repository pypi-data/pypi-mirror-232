from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Cerebroflow python package'
LONG_DESCRIPTION = 'A package to generate csf flow profiles from time lapses '

# Setting up
setup(
        name="cerebroflow", 
        version=VERSION,
        author="Quillan Favey",
        author_email="<quillan.favey@uzh.ch>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['matplotlib', 'PySimpleGUI', 'opencv-python', 'scipy', 'scikit-image', 'TiffCapture', 'pandas'], 
        
        keywords=['python', 'csf', 'kymograph'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)