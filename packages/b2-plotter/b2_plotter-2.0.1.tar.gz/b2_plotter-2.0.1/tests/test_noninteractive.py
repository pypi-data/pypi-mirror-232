import pytest 
from b2_plotter.Plotter import Plotter
import root_pandas as rp
import os

ccbar = '/belle2work/psgebeli/samples/gmc/mc15rib/xipipi/ccbar.root'
mycols= ['xic_M', 'xic_significanceOfDistance','xi_significanceOfDistance', 
         'lambda0_p_protonID', 'xi_M', 'xic_mcFlightTime', 'xic_chiProb', 'xic_isSignal']
xicmassrangeloose = '2.3 < xic_M < 2.65'
df_ccbar = rp.read_root(ccbar, key='xic_tree', columns = mycols)

plotter = Plotter(isSigvar='xic_isSignal', mcdfs={'ccbar': df_ccbar}, signaldf = df_ccbar, interactive = False)

def test_constructor():
    assert isinstance(plotter, Plotter)

def test_plot():
    for var in mycols[:-3]:
        plotter.plot(var, cuts = xicmassrangeloose)
        assert os.path.isfile(f'plot_{var}.png')

def test_plotFom():
    for var in mycols[:-3]:
        optimal, fommax = plotter.plotFom(var, massvar = 'xic_M', signalregion = (2.46, 2.475))
        assert os.path.isfile(f'fom_{var}.png')
        assert isinstance(optimal, float) and isinstance(fommax, float)

def test_plotStep():
    for var in mycols[:-3]:
        plotter.plotStep(var, cuts = xicmassrangeloose)
        assert os.path.isfile(f'step_{var}.png')

def test_getpurity():
    assert isinstance(plotter.get_purity(xicmassrangeloose, 'xic_M', (2.46, 2.475)), float)

def test_getsigeff():
    assert isinstance(plotter.get_sigeff(xicmassrangeloose, 'xic_M', (2.46, 2.475)), float)
