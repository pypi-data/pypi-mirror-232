import codecs

from setuptools import setup, find_packages

# Define project metadata
NAME = 'image-upsampler'
VERSION = '0.0.1'
DESCRIPTION = 'A Python library for image upsampling that uses a machine learning model.'
AUTHOR = 'Jose Solorzano'
EMAIL = 'jose.h.solorzano@gmail.com'
URL = 'https://github.com/jose-solorzano/image-upsampler'  # TODO make it public

REQUIRES = [
    'numpy>=1.24',
    'tqdm>=4.0.0',
    'torch>=2.0.0',
    'torchvision>=0.15.0',
    'opencv-python>=4.8.0',
]

# Long description comes from README
with codecs.open('README.md', 'r', 'utf-8') as f:
    LONG_DESCRIPTION = f.read()

# Setup configuration
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(),
    install_requires=REQUIRES,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
    python_requires='>=3.7',
)
