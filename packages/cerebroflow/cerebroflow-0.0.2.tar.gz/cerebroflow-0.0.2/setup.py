from setuptools import setup, find_packages
# pypi-AgEIcHlwaS5vcmcCJDM5ODdjNzdmLWRjM2QtNGJmYS04MDkzLTBiOTg1NjQ2MmJkYgACKlszLCJjMjU0Y2JkMy04Y2RlLTQ2M2YtYjMwNS0wMDhjZGExNDY3YzMiXQAABiBH0l-WaLw--Qp3Gvk6PFrDIMr8WssN3OvzaC0trG7ouQ
VERSION = '0.0.2' 
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
            "Operating System :: Microsoft :: Windows",
        ]
)