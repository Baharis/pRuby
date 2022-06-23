# pRuby
Python library for pressure calculation based on ruby fluorescence spectrum.
Apart from standard capabilities includes a simple tkinter-based GUI.
Available for Python 3.6+ under the MIT License. 

### Dependencies
* [matplotlib](http://www.matplotlib.org/)
* [numpy, scipy](http://www.scipy.org)
* [uncertainties](http://pythonhosted.org/uncertainties/)
* [natsort](https://natsort.readthedocs.io/en/master/)

### Getting started

Since pRuby requires specific versions of python and some popular
packages such as `numpy`, it is recommended to use it in a virtual
environment in order to avoid version conflicts.
Virtual environment can be usually created using
[`virtualenvwrapper`](http://virtualenvwrapper.readthedocs.io) or
[`virtualenvwrapper-win`](https://github.com/davidmarble/virtualenvwrapper-win)
in the command line:

    $ mkvirtualenv -p /path/to/python3.6+ pRuby-venv

Afterwards, the package can bo either installed via PyPI,
where it is available under the name `pruby`.
In order to start working with pRuby, install it using:

    $ pip install pruby


### Usage

In order to evaluate pressure with pRuby, import and work with
the `PressureCalculator` object. A general routine might include:
    
* Importing the pressure calculator
* Preparing the pressure calculator
* Reading in a ruby fluorescence spectrum
* Calculating pressure based on the R1 position
* Printing the result
* Choosing a place to plot a spectrum
* Plotting the spectrum 

This routine can be performed in pRuby using the following commands:

    from pruby import PressureCalculator
    calc = PressureCalculator()
    calc.read('/path/to/ruby/spectrum.txt')
    calc.calculate_p_from_r1
    print(calc.p)
    calc.output_path = '/path/to/plotted/spectrum.png'
    calc.draw()

Of course, selected steps can be omitted, modified, or repeated at will.
Instead of readig an actual spectrum, position of r1 peak can be assigned
manually by setting the value of `calc.r1`. Pressure can be calculated
based on r1, but r1 can be calculated based on current pressure as well.
If `output_path` is not provided, calling `calc.draw()` will show a plot
in a pop-up `matplotlib` window instead. In particular, calling `draw()`
multiple times will overlay the spectra if output_path is not set.

The same capabilities can be accessed via simple tkinter GUI,
which is functional on all popular systems, although some of its capabilities
were proved to be limited on Microsoft Windows. In order to run the graphical
interface, execute the `pRuby_GUI.py` script (if you downloaded it from github)
or start the interface from the level of package using:

    from pruby import gui
    gui.run()

pRuby GUI provides a simple, minimalistic GUI with the following functionality:
* **Data** - import, draw and handle reference for ruby fluorescence data. 
    * **Import** - Import ruby fluorescence data from .txt file, fit the peaks
      according to selected peakhunt method and recalculate R1 and p values.
    * **Draw** - Draw imported data file as well as fitted curve and found peak 
      position. Multiple plots will be drawn on the same canvas if it stays open. 
    * **To reference** - Export current R1, t and p1 values as a new reference.
    * **From reference** - Import R1, r and p1 data from previously saved reference.
    * **Drow on import** - Toggle this option on in order to automatically draw
      every imported data on the active canvas.
* **Methods** - switch between the strategies to affect the engine
of underlaying calculator and change the behaviour of program.
  * Reading strategies
    * **Raw txt** - when reading the spectrum, expect a raw txt file
      with two columns containing a sequences of x and y values only.
    * **Meta txt** - same as above, but ignore every line which
      can not be interpreted (default).
  * Backfitting strategies
    * **Linear Huber** - estimate the background using linear function fitting
      with Huber sigmas (large deviations from the line - peaks - are ignored).
    * **Linear Satelite** - estimate the background using linear function
      fitting with unit sigmas to 1 nm ranges of edge-most data only.
  * Peakfitting strategies
    * **Gauss** - find the positions of R1 and R2 using two independent
      Gaussian function centered around each of them and fit to a very small
      amount of data. Very robust approach, but can be inaccurate (default).
    * **Pseudovoigt** - find the position of R1 and R2 using a sum of
      two Gaussian and two Lorentzian functions, centred pairwise on each of
      the peaks. Most precise method for handling sharp, good quality signals.
    * **Camel** - find the positions of R1 and R2 by fitting a sum of three
      Gaussian curves to data: one for R1, one for R1, one low between them.
      Intended fot bad quaility data with heavily overlapping peaks,
      which can not be determined correctly using other approaches.
  * Correcting strategies
    * **Vos R1** - correct for temperature difference accorging to the R1
      equation put forward by Vos et al. in
      [doi:10.1063/1.348903](http://aip.scitation.org/doi/10.1063/1.348903)
      (default).
    * **Ragan R1** - correct for temperature difference accorging to equation
      put forward by Ragan et al. in 
      [doi:10.1063/1.351951](http://aip.scitation.org/doi/10.1063/1.351951).
    * **No t correction** - don't correct for temperature difference.
  * Translating strategies
    * **Liu** - translate R1 position to pressure
      according to equation put forward by Liu et al. in 
      [doi:10.1088/1674-1056/22/5/056201](http://iopscience.iop.org/article/10.1088/1674-1056/22/5/056201/meta).
      (default).
    * **Mao** - translate R1 position to pressure
      according to equation put forward by Mao et al. in
      [doi:10.1029/JB091iB05p04673](http://onlinelibrary.wiley.com/doi/10.1029/JB091iB05p04673/abstract).
    * **Piermarini** - translate R1 position to pressure
      according to equation put forward by Piermarini et al. in 
      [10.1063/1.321957](http://aip.scitation.org/doi/10.1063/1.321957).
    * **Wei** - translate R1 position to pressure 
      according to equation put forward by Wei et al. in 
    [doi:10.1063/1.3624618](http://aip.scitation.org/doi/10.1063/1.3624618). 
  * Drawing strategies
    * **Simple** - draws spectrum with as little details as possible
      to increase clarity, e.g. when overlaying multiple spectra.
    * **Complex** - draw the same elements as **Simple**, but additionally
      plot background profile, fitting range, and determined R2 value as well.
* **?** - Show basic information about the program

Multiple behaviour options are available and can be selected from the package
leve as well, by modyfying the `engine` attribute of a `PressureCalculator`.
For example, the temperature correction can be turned off therein using:

    calc.engine.set_strategy(correcting='None')

Each of the six strategies (reading, backfitting, peakfitting, correcting,
translating, and drawing) can be changed independently or together by providing
its name, as listed in the table above.

## Author

This software is made by
[Daniel Tchoń](https://www.researchgate.net/profile/Daniel-Tchon),
and distributed under an MIT license. It is in development and all
tips, suggestions, or contributions are welcome and can be sent
[here](mailto:dtchon@chem.uw.edu.pl).
If you have utilised pRuby in academic work, please let me know!
If the tools find wider use, a dedicated paper will be published.
