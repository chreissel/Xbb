#!/usr/bin/env python
from __future__ import print_function
import ROOT
import argparse
import os
import sys
import time

#------------------------------------------------------------------------------
# sample tree class
# 
# reads many .root files and chain them as a TChain and adds all the TH1D count
# histograms together. Provides an iterator which handles the updating of
# TTreeFormulas automatically when the tree number changes.
#
# create:  sampleTree = SampleTree('path/to/indexfile.txt')
#
# add formula: sampleTree.addFormula('ptCut','pt>100')
#
# loop over events:
#
# for event in sampleTree: 
#     print 'pt cut:', sampleTree.evaluate('ptCut')
#------------------------------------------------------------------------------
class SampleTree(object):

    def __init__(self, sampleTextFileName, treeName = 'tree'):
        
        self.verbose = True 
        self.status = 0
        self.treeName = treeName
        self.formulas = {}
        self.oldTreeNum = -1
        self.limitFiles = -1
        
        self.timeStart = time.time()
        self.timeETA = 0

        self.regionDict = {
            'default': {'file': 0}
        }

        # check existence of sample .txt file which contains list of .root files
        self.sampleTextFileName = '' 
        if os.path.isfile(sampleTextFileName):
            self.sampleTextFileName = sampleTextFileName
        else:
            print ("\x1b[31mERROR: file not found: %s \x1b[0m"%sampleTextFileName)
            status = 0
            return

        # add all .root files to chain and add count histograms
        self.chainedFiles = []
        self.brokenFiles = []
        self.histograms = {}
        self.tree = ROOT.TChain(self.treeName)
        if self.verbose:
            print ('open samples .txt file: %s'%self.sampleTextFileName)
        with open(self.sampleTextFileName, 'r') as sampleTextFile:

            # check all .root files listed in the sample .txt file
            for rootFileName in sampleTextFile:
                
                if self.verbose:
                    print ('--> tree: %s'%(rootFileName.split('/')[-1].strip()))
                # check root file existence
                if os.path.isfile(rootFileName.replace('root://t3dcachedb03.psi.ch:1094/','').strip()):
                    obj = None
                    rootFileName = 'root://t3dcachedb03.psi.ch:1094/' + rootFileName.replace('root://t3dcachedb03.psi.ch:1094/','').strip()
                    input = ROOT.TFile.Open(rootFileName,'read')
                    if input and not input.IsZombie():

                        # add count histograms, since they are not in the tchain
                        for key in input.GetListOfKeys():
                            obj = key.ReadObj()
                            if obj.GetName() == self.treeName:
                                continue
                            for region, regionInfo in self.regionDict.iteritems():
                                histogramName = obj.GetName()+region

                                if histogramName in self.histograms:
                                    if self.histograms[histogramName]:
                                        self.histograms[histogramName].Add(obj.Clone(obj.GetName()))
                                    else:
                                        print ("ERROR: histogram object was None!!!")
                                else:
                                    self.histograms[histogramName] = obj.Clone(obj.GetName())
                                    self.histograms[histogramName].SetDirectory(regionInfo['file'])
                        input.Close()

                        # add file to chain
                        chainTree = '%s/%s'%(rootFileName, self.treeName)
                        if self.verbose:
                            print ('chaining '+chainTree)
                        statusCode = self.tree.Add(chainTree)

                        # check for errors in chaining the file
                        if statusCode != 1:
                            print ('ERROR: failed to chain ' + chainTree + ', returned: ' + str(statusCode),'tree:',tree)
                            raise Exception("TChain method Add failure")
                        elif not self.tree:
                            print ('\x1b[31mERROR: tree died after adding %s.\x1b[0m'%rootFileName)
                        else:
                            self.treeEmpty = False
                            self.chainedFiles.append(rootFileName)
                            if self.limitFiles > 0 and len(self.chainedFiles) >= self.limitFiles:
                                print ('\x1b[35mDEBUG: limit reached! no more files will be chained!!!\x1b[0m')
                                break
                    else:
                        print ('ERROR: file is damaged: %s'%rootFileName)
                        self.brokenFiles.append(rootFileName)
                else:
                    print ('ERROR: file is missing: %s'%rootFileName)
        if self.verbose:
            print ('INFO: # files chained: %d'%len(self.chainedFiles))
            print ('INFO: # files broken : %d'%len(self.brokenFiles))

    def addFormula(self, formulaName, formula):
        self.formulas[formulaName] = ROOT.TTreeFormula(formulaName, formula, self.tree) 

    def next(self):
        self.treeIterator.next()
        treeNum = self.tree.GetTreeNumber()
        # TTreeFormulas have to be updated when the tree number changes in a TChain
        if treeNum != self.oldTreeNum:
            # update ETA estimates
            if treeNum == 0:
                self.timeStart = time.time()
            else:
                fraction = 1.0*treeNum/len(self.chainedFiles)
                passedTime = time.time() - self.timeStart
                self.timeETA = (1.0-fraction)/fraction * passedTime if fraction > 0 else 0
            # output status
            if self.verbose:
                percentage = 100.0*treeNum/len(self.chainedFiles)
                print ('INFO: switching trees --> %d (=%1.1f %%, ETA: %1.1f min)'%(treeNum, percentage, self.getETA()/60.0))
            self.oldTreeNum = treeNum
            # update TTreeFormula's
            for formulaName, treeFormula in self.formulas.iteritems():
                treeFormula.UpdateFormulaLeaves()

    def __iter__(self):
        self.treeIterator = self.tree.__iter__()
        return self

    def evaluate(self, formulaName):
        if formulaName in self.formulas:
            if self.formulas[formulaName].GetNdata() > 0:
                return self.formulas[formulaName].EvalInstance()
            else:
                return 0
        else:
            existingFormulas = [x for x,y in self.formulas.iteritems()]
            print ("existing formulas are: ", existingFormulas)
            raise Exception("SampleTree::evaluate: formula '%s' not found!"%formulaName)
    
    def getETA(self):
        # return ETA in seconds
        return self.timeETA

#------------------------------------------------------------------------------
# calculate efficiency of HLT
#------------------------------------------------------------------------------
class TriggerEfficiencies(object):

    def __init__(self, sampleTree = None):
        self.sampleTree = sampleTree

    def calculateEfficiency(self, variable, range=[0, 1000, 100], tightCut='1', looseCut='1', outputFileName='trigeff.root'):
       
        # add formulas for cuts
        self.sampleTree.addFormula('variable', variable)
        self.sampleTree.addFormula('tight', tightCut)
        self.sampleTree.addFormula('loose', looseCut)

        # prepare output file and histograms
        outputFile = ROOT.TFile(outputFileName,'recreate')
        histogramPassLoose = ROOT.TH1D('histogramPassLoose','passed cut: ' + looseCut, range[2], range[0], range[1])
        histogramPassTight = ROOT.TH1D('histogramPassTight','passed cut: ' + tightCut, range[2], range[0], range[1])
        histogramEfficiency = ROOT.TH1D('histogramEfficiency','Trigger efficiency', range[2], range[0], range[1])
        histogramPassLoose.Sumw2()
        histogramPassTight.Sumw2()

        if self.sampleTree:
            # count events passing the loose/tight cuts
            nEntry = 0
            for event in self.sampleTree:
                passLoose = self.sampleTree.evaluate('loose')
                passTight = self.sampleTree.evaluate('tight')
                var = self.sampleTree.evaluate('variable')
                if passLoose:
                    histogramPassLoose.Fill(var)
                if passTight:
                    histogramPassTight.Fill(var)
                nEntry += 1
            
            # calculate efficiency
            # divide histograms with binomial errors
            histogramEfficiency.Divide(histogramPassTight, histogramPassLoose, 1, 1, "B")

        outputFile.Write()
        outputFile.Close()

#------------------------------------------------------------------------------
# main
#------------------------------------------------------------------------------
# example how to call
# ./trigger_efficiencies.py -S ... -v '(nJet>0)*Max$(Jet_pt)' -r 300,800,100 -o trig_eff_500.root -l HLT_BIT_HLT_PFJet400_v -t HLT_BIT_HLT_PFJet500_v
#------------------------------------------------------------------------------
if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-S', action='store', dest='sample', help='sample textfile(s) with dataset names')
    parser.add_argument('-v', action='store', dest='variable', default='(nJet>0)*Max$(Jet_pt)', help='variable to computer the efficiency differentially of')
    parser.add_argument('-r', action='store', dest='range', default='0,1000,100', help='min,max,nbins of variable to create histogram')
    parser.add_argument('-o', action='store', dest='output', default='trigeff.root', help='output .root file')
    parser.add_argument('-l', action='store', dest='loose', default='HLT_BIT_HLT_PFJet400_v', help='loose cut')
    parser.add_argument('-t', action='store', dest='tight', default='HLT_BIT_HLT_PFJet500_v', help='loose cut')
    args = parser.parse_args()

    # read samples
    sampleTree = SampleTree(args.sample)
    if not sampleTree:
        print ('creating sample tree failed!')
        exit(0)

    # calculate efficiency
    triggerEfficienciesCalculator = TriggerEfficiencies(sampleTree)
    r = [x.strip() for x in args.range.split(',')]    
    histogramRange = [float(r[0]), float(r[1]), int(r[2])]
    triggerEfficienciesCalculator.calculateEfficiency(variable=args.variable, range=histogramRange, tightCut=args.tight, looseCut=args.loose, outputFileName=args.output)

    print ("done. Knowing the efficiency you triggered with fills you with determination.")
