"""Abaqus CAE plugin to calculate Head Injury Criteria

Begin by plotting acceleration (mm/s2) vs time (s) in the current viewport.
This plug-in will calculate and plot the Head Injury Criteria (HIC)
described in https://en.wikipedia.org/wiki/Head_injury_criterion
"""

__version__ = '1.1.0'
__url__ = 'https://github.com/costerwi/plugin-headInjuryCriteria',

from abaqusGui import *

class optionsDB(AFXDataDialog):

    def __init__(self, owner, title):
        AFXDataDialog.__init__(self,
                mode=owner,
                title=title,
                actionButtonIds=self.OK|self.CANCEL,
                opts=DIALOG_NORMAL)

        group = AFXVerticalAligner(self, opts=LAYOUT_FILL_X)
        c = AFXComboBox(p=group, ncols=5, nvis=4,
                text="Length unit in model", tgt=owner.lengthKw, opts=LAYOUT_FILL_X)
        for t in 'm', 'mm', 'in', 'ft':
            c.appendItem(t)

        c = AFXComboBox(p=group, ncols=5, nvis=2,
                text="Time unit in model", tgt=owner.timeKw, opts=LAYOUT_FILL_X)
        for t in 's', 'ms':
            c.appendItem(t)

        c = AFXTextField(p=group, ncols=5, labelText="Min duration time (s)",
                tgt=owner.tminKw, opts=LAYOUT_FILL_X|AFXTEXTFIELD_FLOAT)

        c = AFXTextField(p=group, ncols=5, labelText="Max duration time (s)",
                tgt=owner.tmaxKw, opts=LAYOUT_FILL_X|AFXTEXTFIELD_FLOAT)


class HICProcedure(AFXProcedure):
    def __init__(self, owner):
        AFXProcedure.__init__(self, owner) # Construct the base class.

        # Command
        plotHIC = AFXGuiCommand(mode=self,
                method='plotHIC',
                objectName='headInjuryCriteria',
                registerQuery=FALSE)

        # Keywords
        self.lengthKw = AFXStringKeyword(
                command=plotHIC,
                name='lengthUnit',
                isRequired=TRUE,
                defaultValue='mm')

        self.timeKw = AFXStringKeyword(
                command=plotHIC,
                name='timeUnit',
                isRequired=TRUE,
                defaultValue='s')

        self.tminKw = AFXFloatKeyword(
                command=plotHIC,
                name='tmin',
                isRequired=TRUE,
                defaultValue=0.003)

        self.tmaxKw = AFXFloatKeyword(
                command=plotHIC,
                name='tmax',
                isRequired=TRUE,
                defaultValue=0.036)

        plotHIC.setKeywordValuesToDefaults()

    def activate(self):
        "Activate the procedure if possible"
        viewport = session.viewports[session.currentViewportName]
        if hasattr(viewport.displayedObject, 'charts'):
            return AFXProcedure.activate(self)
        else:
            showAFXErrorDialog(getAFXApp().getAFXMainWindow(),
                    'You must first display an XY Plot of acceleration.')

    def getFirstStep(self):
        return AFXDialogStep(self,
                optionsDB(owner=self, title="HIC " + __version__))


toolset = getAFXApp().getAFXMainWindow().getPluginToolset()

toolset.registerGuiMenuButton(
        object=HICProcedure(toolset),
        kernelInitString='import headInjuryCriteria',
        buttonText='Head Injury Criteria HIC',
        author='Carl Osterwisch',
        description=__doc__,
        version=__version__,
        helpUrl=__url__,
        applicableModules=['Visualization'],
        )
