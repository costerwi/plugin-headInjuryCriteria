"""Abaqus CAE plugin to calculate Head Injury Criteria

Begin by plotting acceleration (mm/s2) vs time (s) in the current viewport.
This plug-in will calculate and plot the Head Injury Criteria (HIC)
described in https://en.wikipedia.org/wiki/Head_injury_criterion
"""

__VERSION__ = '1.0.1'

from abaqusGui import getAFXApp

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()

toolset.registerKernelMenuButton(
        moduleName='headInjuryCriteria',
        functionName='plotHIC()',
        buttonText='Head Injury Criteria HIC',
        author='Carl Osterwisch',
        description=__doc__,
        version=__VERSION__,
        helpUrl='https://github.com/costerwi/plugin-headInjuryCriteria',
        applicableModules=['Visualization'],
    )
