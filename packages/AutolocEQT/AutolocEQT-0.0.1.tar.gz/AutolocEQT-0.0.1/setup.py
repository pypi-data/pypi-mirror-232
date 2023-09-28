from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Automatic Earthquake Detection'
LONG_DESCRIPTION = 'Python Package for Automatic Earthquake Detection Based on Attentive Deep Learning Model of EQTransformer'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="AutolocEQT", 
        version=VERSION,
        author="Muhajir Anshori",
        author_email="<muhajir.bmkg@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'earthquake_detection', 'attentive_deep_learning'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: POSIX :: Linux",
        ]
)
