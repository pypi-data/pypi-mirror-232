from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.3'
DESCRIPTION = 'A basic package to turn plots into gifs'
LONG_DESCRIPTION = 'A package to turn plots into gifs (matplotlib.pyplot, seaborn, plotly.express)'

# Setting up
setup(
    name="gify_plot",
    version=VERSION,
    author="Francesco Di Cursi",
    author_email="<f.dicursi@studenti.unipi.it>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['pandas', 'tqdm', 'Pillow', 'matplotlib','seaborn','plotly'],
    keywords=['gif', 'plot', 'seaborn', 'matplotlib', 'plotly'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)