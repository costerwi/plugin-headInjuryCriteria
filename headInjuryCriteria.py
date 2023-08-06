"""Abaqus CAE script to calculate Head Injury Criteria

see: https://en.wikipedia.org/wiki/Head_injury_criterion

Carl Osterwisch, February 2023
"""

from __future__ import print_function
import numpy as np

def calculate_HIC(time, g, tmax=0.036, tmin=0.003):
    integrated = np.array(zip(time, cumtrapz(y=g, x=time, initial = 0)))

    maxHIC = (0, 0, 0)
    window = np.arange(0.003, 0.037, 0.001)  # 3 to 36 ms in steps of 1 ms
    for t1, i1 in integrated:
        t2 = t1 + window  # array of t2 values according to window
        i2 = np.interp(x=t2, xp=time, fp=integrated[:,1])  # array of integrated values
        HIC = window*np.power( (i2 - i1)/window, 2.5 )  # array of HIC for t1
        amax = np.argmax(HIC)  # index of maximum within window range
        maxHIC = max(maxHIC, (HIC[amax], t1, t2[amax]))  # keep running maximum

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
