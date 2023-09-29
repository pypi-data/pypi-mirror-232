from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.5'
DESCRIPTION = 'A basic package to turn plots into gifs'
LONG_DESCRIPTION = """# gify_plot
A simple Python package to turn your plots into gifs (Matplotlib, Seabron, Plotly)

# How to install it
`pip install gify_plot`

# Args
  ### Mandatory
  - **X**:list ==> [ [x of type 1],[x of type 2],[x of type 3], ...]
  - **Y**:list ==> Same as X but for y elements. If only one Y el is given, then the array is updated to have the same length of X
  - **plot_type**:str ==> The plot_type changes according to plot_library
  - **plot_library**:str ==> plt | sns | px  (short forms for matplotlib.pyplot, seaborn and plotly.express)
  - **name**:str ==> The name of pngs and gif given as output,
  - **plot_title**:str
  - **xaxis_title**:str
  - **yaxis_title**:str
  ### Optional
  - **legend_labels** = [] ==> If empty then progressive numbers are used for the elements in the legend. If inserted, be sure to put names in the same order of provided data
  - **colors** = ["blue","red","green","orange","violet","yellow","black","brown","cyan"] ==> it must have at least the same length of groups provided in the provided data
  - **sort_by_x** = True ==> Sorts value by xaxis (e.g. date)
  - **sort_by_y** = False ==> If set to True, it overrides sort_by_x

# How to use it
```
#A random df as a showcase

from gify_plot import *  (or, alternatively, "from gify_plot import gify_plot")
import numpy as np
import pandas as pd

df = pd.DataFrame({"G1_X" : np.random.randint(low=1, high=100, size=100),
                    "G2_X"  : np.random.randint(low=1,high=100, size=100),
                   "G1_Y" : np.random.randint(low=1, high=100, size=100),
                    "G2_Y"  : np.random.randint(low=1, high=100, size=100),
                     })

gify_plot(X=[df["G1_X"],df["G2_X"]],
           Y=[df["G1_Y"],df["G2_Y"]],
           plot_type="line", plot_library="plt", name="test_gif",
           plot_title="Test gif", xaxis_title="year", yaxis_title="time"
          )
```

It ouputs a list of PNG in the dedicated folder, along with the resulting GIF.

#Supported libraries and plots:
- plt:
  - line
  - bar
  - scatter
  - stackplot (no legend)
- sns:
  - lineplot
  - scatterplot
  - barplot
- px:
  - line
  - scatter
  - area
  - bar
"""

# Setting up
setup(
    name="gify_plot",
    version=VERSION,
    author="Francesco Di Cursi",
    author_email="f.dicursi@studenti.unipi.it",
    license="MIT",
    url="https://github.com/FrancescoDiCursi/gify_plot",
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