#! /usr/bin/env python
from __future__ import print_function
import ROOT
ROOT.gROOT.SetBatch(True)
import os
import sys
import time
import glob

class DatacardReader(object):
    histoCounter = 0
    subfolder = 'dc_comparison'

    def __init__(self, fileName):
        self.fileName = fileName
        with open(self.fileName, 'r') as inputFile:
            self.lines = inputFile.readlines()
            self.shapes = {}

            #shapes *                 ch1_Zmm_SIG_low   vhbb_TH_BDT_Zuu_LowPt.root ZuuLowPt_13TeV/$PROCESS
            for line in self.lines:
                lineParts = [x.strip() for x in line.split(' ') if len(x.strip()) > 0]
                if lineParts[0] == 'shapes':
                    self.shapes[ self.translate([lineParts[2]])[0] ] = {'file': lineParts[3], 'histogram': lineParts[4], 'channel': self.translate([lineParts[2]])[0]}

    
    def find(self, key, start=-1):
        for i in range(start+1, len(self.lines)):
            if self.lines[i].split(' ')[0].strip() == key:
                return i

    def get(self, row):
        return [x.strip() for x in self.lines[row].split(' ') if len(x.strip()) > 0]

    def translate(self, names):
        translationDict = {
                    'ch1_Zmm_TT_low': 'Zuu_CRttbar_lowpt',
                    'ch1_Zmm_Zhf_low': 'Zuu_CRZb_lowpt',
                    'ch1_Zmm_Zlf_low': 'Zuu_CRZlight_lowpt',
                    'ch1_Zmm_SIG_low': 'Zuu_BDT_lowpt',
                    'ch2_Zee_TT_low': 'Zee_CRttbar_lowpt',
                    'ch2_Zee_Zhf_low': 'Zee_CRZb_lowpt',
                    'ch2_Zee_Zlf_low': 'Zee_CRZlight_lowpt',
                    'ch2_Zee_SIG_low': 'Zee_BDT_lowpt',
                    'ch3_Zmm_TT_high': 'Zuu_CRttbar_highpt',
                    'ch3_Zmm_Zhf_high': 'Zuu_CRZb_highpt',
                    'ch3_Zmm_Zlf_high' : 'Zuu_CRZlight_highpt',
                    'ch3_Zmm_SIG_high': 'Zuu_BDT_highpt',
                    'ch4_Zee_TT_high': 'Zee_CRttbar_highpt',
                    'ch4_Zee_Zhf_high': 'Zee_CRZb_highpt',
                    'ch4_Zee_Zlf_high': 'Zee_CRZlight_highpt',
                    'ch4_Zee_SIG_high': 'Zee_BDT_highpt'
                }
        namesTranslated = []
        for name in names:
            nameTranslated = name
            for k,v in translationDict.iteritems():
                nameTranslatedNew = nameTranslated.replace(k,v)
                if nameTranslatedNew != nameTranslated:
                    nameTranslated = nameTranslatedNew
                    break
            namesTranslated.append(nameTranslated)
        return namesTranslated

    def getObservation(self):
        binRow = self.find('bin')
        observationRow = self.find('observation', start=binRow)
        bins = self.translate(self.get(binRow))
        observations = self.get(observationRow)
        return {bins[i]: observations[i] for i in range(len(bins))}

    def getRates(self):
        binRow = self.find('bin')
        observationRow = self.find('observation', start=binRow)
        binRow = self.find('bin', start=observationRow)
        processRow = self.find('process', start=binRow)
        ratesRow = self.find('rate', start=processRow)
        print(binRow, processRow, ratesRow)

        bins = self.translate(self.get(binRow))
        processes = self.translate(self.get(processRow))
        rates = self.get(ratesRow)
        
        return {bins[i] + ':' + processes[i]: rates[i] for i in range(len(bins))}
   
    def getHisto(self, fileName, histoName):
        f1 = ROOT.TFile.Open('/'.join(self.fileName.split('/')[:-1]) + '/' + fileName)
        print("GET:", fileName, histoName)
        h1 = f1.Get(histoName).Clone(histoName)
        h1.SetDirectory(0)
        f1.Close()
        return h1

    def getShapes(self):
        binRow = self.find('bin')
        observationRow = self.find('observation', start=binRow)
        binRow = self.find('bin', start=observationRow)
        processRow = self.find('process', start=binRow)
        ratesRow = self.find('rate', start=processRow)
        print(binRow, processRow, ratesRow)

        # MC
        bins = self.translate(self.get(binRow))
        processes = self.translate(self.get(processRow))
        rates = self.get(ratesRow)
        histograms = ['-']
        histos = [self.getHisto(self.shapes[bins[i]]['file'], self.shapes[bins[i]]['histogram'].replace('$PROCESS', processes[i])) for i in range(1, len(bins))]
        histograms += histos
       
        # DATA
        binsUnique = list(set(bins))
        for binU in binsUnique:
            if binU != 'bin':
                bins.append(binU)
                processes.append('data_obs')
                histograms.append(self.getHisto(self.shapes[binU]['file'], self.shapes[binU]['histogram'].replace('$PROCESS', 'data_obs')))
        
        return {bins[i] + ':' + processes[i]: histograms[i] for i in range(len(bins))}

    @staticmethod
    def display(table):
        observations = table
        bins = sorted(observations[0].keys())
        headerRow = ['-'] + [x.split('/')[-2] for x in fileNames]
        maxWidth = max([len(x) for x in headerRow])
        print('  '.join([x.ljust(maxWidth) for x in headerRow]))
        for binName in bins: 
            dataRow = [binName.ljust(maxWidth)] + [('%s'%x[binName]).ljust(maxWidth) for x in observations]
            print('  '.join(dataRow))

    @staticmethod
    def getHTML(table, index1, index2):
        if type(table) == dict:
            observations = table.observations
        else:
            observations = table
        bins = sorted(observations[0].keys())
        headerRow = ['-'] + [x.split('/')[-2] for x in fileNames]
        html = '<table>'
        rows = []
        rows.append('<tr><td><b>'+ '</b></td><td><b>'.join(headerRow) + '</b></td></tr>')
        
        subHeader  = ['']*(len(headerRow)) 
        subHeader[index1] = '<b>compare this<b>'
        subHeader[index2] = '<b>reference<b>'
        rows.append('<tr><td>'+ '</td><td>'.join(subHeader) + '</td></tr>')

        for binName in bins:
            dataRow = [binName]
            maximum = 0
            for x in observations:
                if isinstance(x[binName], ROOT.TH1):
                    hmax = x[binName].GetBinContent(x[binName].GetMaximumBin())
                    if hmax > maximum:
                        maximum = hmax

            for x in observations:
                if isinstance(x[binName], ROOT.TH1):
                    c1 = ROOT.TCanvas("c1","c1",500,500)
                    first = True
                    for y in observations:
                        y[binName].SetStats(0)
                        y[binName].GetYaxis().SetRangeUser(0, maximum*1.1)
                        if x==y:
                            pass
                        else:
                            y[binName].SetLineColor(ROOT.kBlue)
                            y[binName].Draw("same;hist" if not first else "hist")
                            first = False
                    x[binName].SetLineColor(ROOT.kRed)
                    x[binName].Draw("same;E" if not first else "E")

                    outFile = 'histo%d.png'%DatacardReader.histoCounter
                    c1.SaveAs(DatacardReader.subfolder + '/' + outFile)
                    DatacardReader.histoCounter += 1
                    dataRow.append('<div style="text-align:center;"><img src="%s" width=300 height=300><br>&#8747; = %f<br>n = %d</div>'%(outFile, x[binName].Integral(), x[binName].GetEntries()))
                
                else:
                    dataRow.append('%s'%x[binName])
            style = ''
            try:
                if abs((float(dataRow[index1])-float(dataRow[index2]))/float(dataRow[index2])) > 0.1:
                    style = 'background-color:#f99;font-weight:bold;'
                elif abs((float(dataRow[index1])-float(dataRow[index2]))/float(dataRow[index2])) > 0.05:
                    style = 'background-color:#fc8;font-weight:bold;'
                elif abs((float(dataRow[index1])-float(dataRow[index2]))/float(dataRow[index2])) > 0.01:
                    style = 'background-color:#ef9;font-weight:bold;'
            except:
                style = 'background-color:#ddd;font-weight:bold;'
            rows.append('<tr style="{style}"><td>'.format(style=style) + '</td><td>'.join(dataRow) + '</td></tr>')
        rows.append('<tr><td><b>'+ '</b></td><td><b>'.join(headerRow) + '</b></td></tr>')
        html += '\n'.join(rows)
        html += '\n</table>\n'
        return html 

subfolderName = 'dc_comparison_180116'
fileNames = [
                #'/mnt/t3nfs01/data01/shome/berger_p2/VHbb/CMSSW_7_4_7/src/HiggsAnalysis/CombinedLimit/V25/180111_TEST13_newdc_with_old_samples/vhbb_DC_TH_M125_Zll_CRnSR.txt', 
                #'/mnt/t3nfs01/data01/shome/berger_p2/VHbb/CMSSW_7_4_7/src/HiggsAnalysis/CombinedLimit/V25/180114_TEST15_modified_CRZlight_loosebtag/vhbb_DC_TH_M125_Zll_CRnSR.txt',   
                #'/mnt/t3nfs01/data01/shome/berger_p2//VHbb/CMSSW_7_4_7/src/HiggsAnalysis/CombinedLimit/V25/180115_TEST19_stweight_fix/vhbb_DC_TH_M125_Zll_CRnSR.txt',
                '/mnt/t3nfs01/data01/shome/berger_p2//VHbb/CMSSW_7_4_7/src/HiggsAnalysis/CombinedLimit/V25/180116_TEST20_stweight_fix_retraining/vhbb_DC_TH_M125_Zll_CRnSR.txt',
                '/mnt/t3nfs01/data01/shome/berger_p2/VHbb/CMSSW_7_4_7/src/HiggsAnalysis/CombinedLimit/V25/180116_TEST22_stweight_fix_retraining_bbb_dy50/vhbb_DC_TH_M125_Zll_CRnSR.txt',
                '/mnt/t3nfs01/data01/shome/berger_p2/VHbb/CMSSW_7_4_7/src/HiggsAnalysis/CombinedLimit/V25/180111_TEST_DAVID/vhbb_Zll.txt',
            ]
datacardReaders = [DatacardReader(fileName) for fileName in fileNames]
observations = [datacardReader.getObservation() for datacardReader in datacardReaders]
rates = [datacardReader.getRates() for datacardReader in datacardReaders]
shapes = [datacardReader.getShapes() for datacardReader in datacardReaders]

#DatacardReader.display(observations)
#DatacardReader.display(rates)
DatacardReader.subfolder = subfolderName
try:
    os.makedirs(DatacardReader.subfolder)
except:
    pass
with open(subfolderName + '/index.html', 'w') as outputFile:
    outputFile.write('<html><head><title>Datacard comparison</title></head><body>')
    outputFile.write('<h3>DATA</h3>')
    outputFile.write(DatacardReader.getHTML(observations, 2, 3))
    outputFile.write('<h3>MC</h3>')
    outputFile.write(DatacardReader.getHTML(rates, 2, 3))
    outputFile.write(DatacardReader.getHTML(shapes, 2, 3))



