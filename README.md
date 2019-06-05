This document outlines important package dependencies for LogicSim.

Certain functionality in the GUI require a sufficiently updated 
wxPython version that some computers in the DPO do not have natively.

Please ensure that wx.version() within a Python console returns at least
'4.0.4 gtk2 (phoenix) wxWidgets 3.0.5'.

If this is not the case for your particular machine, kindly update
wxPython. Running 

conda install -c anaconda wxpython 

should work.

In case there are issues with admin rights, this needs to be run 
from within a virtual environment.
