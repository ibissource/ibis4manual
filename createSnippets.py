import os
import TutorialSteps
from fileUtils import makeDirectoryIfNotPresent

META_YML = "meta.yml"

def handlerAddOld(comparison, relPath, lines):
    if relPath != META_YML:
        comparison.addOld(TutorialSteps.RelPath(relPath.split("/")), lines)
def handlerAddNew(comparison, relPath, lines):
    if relPath != META_YML:
        comparison.addNew(TutorialSteps.RelPath(relPath.split("/")), lines)

def createStepSnippets(configName, stepName, oldDir, newDir, snippetsDir):
    print "Doing Frank config {0} step {1}".format(configName, stepName)
    hasErrors = False
    with newDir.openFile(META_YML) as f:
        diffs, error = expectedDifferences = TutorialSteps.createFileDifferences(f)
    if error is not None:
        raise Exception("Did not understand meta.yml for config {0} and step {1}".format(configName, stepName))
    compare = TutorialSteps.TreeComparison(diffs)
    if oldDir is not None:
        oldDir.browse(lambda relPath, lines: handlerAddOld(compare, relPath, lines))
    newDir.browse(lambda relPath, lines: handlerAddNew(compare, relPath, lines))
    snippets, errors = compare.run()
    if errors is not None:
        for error in errors:
            hasErrors = True
            print "ERROR: " + error
    for snippet in snippets:
        makeDirectoryIfNotPresent("/".join([configName, stepName]), os.path.abspath(snippetsDir))
        outputFileName = os.path.join(os.path.abspath(snippetsDir), configName, stepName, snippet.getName() + ".txt")
        with open(outputFileName, "w") as f:
            for line in snippet.getLines():
                f.write(line + "\n")
    return hasErrors

def createFrankConfigSnippets(configRoot, snippetsDir):
    name = configRoot.getLastComponent()
    stepDirs = configRoot.getSubdirs()
    hasErrors = False
    if len(stepDirs) >= 1:
        hasErrors = createStepSnippets(name, stepDirs[0].getLastComponent(), None, stepDirs[0], snippetsDir)
    for stepIdx in range(1, len(stepDirs)):
        stepName = stepDirs[stepIdx].getLastComponent()
        hasErrors = hasErrors or createStepSnippets(name, stepName, stepDirs[stepIdx-1], stepDirs[stepIdx], snippetsDir)
    return hasErrors

def createAllSnippets(tutorialStepsDir, snippetsDir):
    makeDirectoryIfNotPresent(snippetsDir)
    tutorialStepsRoot = TutorialSteps.GitDirectoryTree(tutorialStepsDir)
    hasErrors = False
    for frankConfigDir in tutorialStepsRoot.getSubdirs():
        hasErrors = hasErrors or createFrankConfigSnippets(frankConfigDir, snippetsDir)
    if hasErrors:
        print("*** ERRORS CHECKING srcSteps AND GENERATING SNIPPETS")