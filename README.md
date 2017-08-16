# pRuby
Pressure calculation based on Ruby fluorescence spectrum. Available for 
Python 3.5+ under the MIT License. 

### Dependencies
* [matplotlib](http://www.matplotlib.org/)
* [numpy, scipy](http://www.scipy.org)
* [tkinter](http://www.tkdocs.com/index.html)
* [uncertainties](http://pythonhosted.org/uncertainties/)

### Installation

It is recommended to instal and run pRuby inside a Python virtual environment
(like [virtualenvwrapper](http://virtualenvwrapper.readthedocs.io) or
[virtualenvwrapper-win](https://github.com/davidmarble/virtualenvwrapper-win)) 
to avoid version conflicts of its dependencies with system installed packages.
In order to create virtual environment run in the command line:

    $ mkvirtualenv -p /path/to/python3.5+ pRuby   

Download or clone the repository on your local disc and install dependencies using:

    $ pip install -r requirements.txt

In order to run program, enter the virtual environment and run pRuby with:

    $ workon pRuby
    $ python3 /path/to/program/pRuby.py


### Usage

pRuby provides a simple, minimalistic GUI with the following functionality:
* **Data** - import, draw and handle reference for ruby fluorescence data. 
    * **Import** - Import ruby fluorescence data from .txt file, fit the peaks
    according to selected peakhunt method and recalculate R1 and p values.
    * **Draw** - Draw imported data file as well as fitted curve and found peak 
    position. Multiple plots may be drawn on the same canvas. 
    * **To reference** - Export provided R1, t and p1 data as a new reference.
    * **From reference** - Import R1, r and p1 data from previously saved reference.
    * **Drow on import** - Toggle this option on in order to automatically draw
    imported data on the active canvas.
* **Methods** - switch between active peak hunting, 
pressure calculation and temperature collection methods.
Default settings are: Labspec peak fitting / Vos temperature correction
/ Liu pressure calculation. All presented methods rely solely on R1 position.
    * **Camel fit** - original fit utilising three independent Gaussian functions
    for modelling R1 and R2 (and random noise around/between them) simultaneously.
    Intended for bad quaility data with heavily overlapping peaks,
    unfit for the other procedures. 
    * **Gauss fit** - basic fit using a Gaussian function to independently model
    R1 and R2 position based on a small amount of data around them.
    Safe bet in majority of cases.
    * **Labspec fit** - semi-original method inspired by Labspec approach, 
    independently models R1 and R2 positions using larger amount of data than 
    Gauss fit as a linear combination of Gauss and Cauchy functions.
    Intended for handling sharp, good quality signals.
    * **Ragan (1992)** - temperature correction method according to equation
    put forward by Ragan et al. in 
    [doi:10.1063/1.351951](http://aip.scitation.org/doi/10.1063/1.351951).
    This method is for relative pressure calculation 
    and therefore requires a reference.
    * **Vos (1991)** - temperature correction method according to the R1
    equation put forward by Vos et al. in 
    [doi:10.1063/1.348903](http://aip.scitation.org/doi/10.1063/1.348903).
    This method is for absolute pressure calculation 
    and therefore does not use a reference.
    * **No t correction** - no temperature correction will be applied to data.
    * **Piermarini (1970)** - pressure calculation method according to equation
    put forward by Piermarini et al. in 
    [10.1063/1.321957](http://aip.scitation.org/doi/10.1063/1.321957).
    This method is for relative pressure calculation 
    and therefore requires a reference.
    * **Mao (1986)** - pressure calculation method according to equation
    put forward by Mao et al. in 
    [doi:10.1029/JB091iB05p04673](http://onlinelibrary.wiley.com/doi/10.1029/JB091iB05p04673/abstract).
    This method is for absolute pressure calculation 
    and therefore does not use a reference.
    * **Wei (2011)** - pressure calculation method according to equation
    put forward by Wei et al. in 
    [doi:10.1063/1.3624618](http://aip.scitation.org/doi/10.1063/1.3624618). 
    This method is for absolute pressure calculation 
    and therefore does not use a reference.
    It has built-in temperature dependency and 
    ignores other temperature correction procedures.
    * **Liu (2013)** - pressure calculation method according to equation
    put forward by Liu et al. in 
    [doi:10.1088/1674-1056/22/5/056201](http://iopscience.iop.org/article/10.1088/1674-1056/22/5/056201/meta).
    This method is for absolute pressure calculation 
    and therefore does not use a reference.
