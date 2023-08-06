"""Abaqus CAE script to calculate Head Injury Criteria

see: https://en.wikipedia.org/wiki/Head_injury_criterion

Carl Osterwisch, February 2023
"""

from __future__ import print_function
import numpy as np

def calculate_HIC(time, g, tmax=0.036, tmin=0.003):
    """Calculate HIC and range of time when it occurs

    Keyword arguments:
    time -- list of sample times in seconds
    g -- list of acceleration corresponding to each time in g's
    tmax -- max size of calculation window in seconds (default 0.036)
    tmin -- min size of calculation window in seconds (default 0.003)

    >>> tmax = 0.036  # seconds
    >>> time = np.linspace(0.0, 4.0, 10000)  # seconds
    >>> maxg = 10  # g's
    >>> g = maxg*np.sin(time)  # sinusoidal acceleration profile
    >>> HIC, t1, t2 = calculate_HIC(time, g, tmax)

    Calculate exact HIC for this simple acceleration profile
    >>> integ = 2*maxg*np.cos(np.pi/2 - tmax/2)
    >>> exactHIC = tmax*(integ/tmax)**2.5
    >>> abs((HIC - exactHIC)/exactHIC) < 1e-6
    True

    Maximum HIC should occur near pi/2 seconds in this example
    >>> abs((t1 + t2)/2 - np.pi/2) < 1e-3
    True
    >>> abs(t2 - t1 - tmax) < 1e-6
    True

    Should give same HIC for a negative acceleration
    >>> abs(calculate_HIC(time, -1*g, tmax)[0] - HIC) < 1e-6
    True
    """

    from scipy import integrate
    cumintegral = integrate.cumtrapz(y=g, x=time, initial=0)

    assert tmin > 0
    assert tmax > tmin
    assert max(np.diff(time)) <= 0.2*tmin, "Time steps are too coarse"

    dt = np.linspace(tmin, tmax, 100)  # time steps in window

    maxHIC = (0, 0, 0)  # initialize
    for t1, i1 in zip(time, cumintegral):
        t2 = t1 + dt  # array of t2 values
        integ = np.interp(x=t2, xp=time, fp=cumintegral) - i1  # array of integrated values
        for direction in 1, -1:
            valid = integ > 0  # must be positive to apply 2.5 power
            if np.any(valid):
                HIC = dt[valid]*np.power(integ[valid]/dt[valid], 2.5)  # array of HIC for t1 to t2
                amax = np.argmax(HIC)  # index of maximum within window range
                maxHIC = max(maxHIC, (HIC[amax], t1, t2[amax]))  # running maximum
            integ *= -1  # check opposite sign
    return maxHIC


def plotHIC():
    """Called by Abaqus CAE to estimate critical damping in current xyPlot
    """

    from abaqus import session, getWarningReply, CANCEL
    from abaqusConstants import TIME, ACCELERATION, NONE
    from visualization import QuantityType
    hicType = QuantityType(type=NONE, label='Head Injury Criteria')
    vp = session.viewports[session.currentViewportName]
    xyPlot = vp.displayedObject
    if not hasattr(xyPlot, 'charts'):
        return getWarningReply(
                'You must first display an XY Plot of acceleration',
                (CANCEL, )
                )
    chart = xyPlot.charts.values()[0]
    for curve in chart.curves.values():
        if TIME != curve.data.axis1QuantityType.type:
            continue # not vs frequency
        if ACCELERATION != curve.data.axis2QuantityType.type:
            continue # not acceleration
        time, accel = np.asarray(curve.data.data).T

        HIC, t1, t2 = calculate_HIC(time, accel/9810.)
        print('HIC={}, t1={}, t2={}'.format(HIC, t1, t2))
        HICxy = [[t1, 0],
                 [t1, HIC],
                 [t2, HIC],
                 [t2, 0]]

        n = 0
        while not n or session.xyDataObjects.has_key(name): # find unique name
            n -= 1
            name = curve.data.name + ' HIC' + str(n)

        curve = session.Curve(
            xyData = session.XYData(
                name = name,
                legendLabel = curve.data.legendLabel + ' HIC',
                sourceDescription = 'HIC estimated from ' + curve.data.description,
                data = HICxy,
                axis1QuantityType = curve.data.axis1QuantityType,
                axis2QuantityType = hicType,
                )
            )
        chart.setValues(curvesToPlot=chart.curves.values() + [curve])


if __name__ == '__main__':
    plotHIC()
