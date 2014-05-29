#!/usr/bin/env python

##########################
###   Options parser   ###
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description = 'mcFit.py')
    parser.add_argument('-f','--DTF',help='Use DTF variables',action='store_true')
    parser.add_argument('-d','--dataset',help='make also dataset',action='store_true')
    args = parser.parse_args()
##########################

from ROOT import gSystem
gSystem.Load('../PDFs/RooDSCBShape_cxx')
from ROOT import RooDataSet, RooRealVar, RooArgSet, RooFormulaVar, RooGenericPdf, RooCmdArg, RooStats, RooWorkspace
from ROOT import RooCBShape, RooAddPdf, RooArgList, RooPlot, RooDataHist, RooFitResult, RooAbsPdf, RooGaussian, RooPolynomial, RooExponential, RooChebychev, RooDSCBShape
from ROOT import RooFit, gROOT, TStyle, gStyle, gPad
from ROOT import TFile, TCanvas, TPad, TH1F, TGraphErrors, TPad, TLegend, TPaveText, TMultiGraph, TGraphErrors, TMath
from ROOT import TH1D, TH1F, TTree, RooHistPdf, TLine, TF1
import ROOT, sys, getopt, pickle 
from array import array
import sys
sys.path.append('..')
from fits import makeRooDataset

gROOT.SetBatch()

def doMCFit(dataSet, x_var, addTitlePlot=''):  
    
    cuts_str = ''
    data = dataSet.reduce( RooFit.Cut(cuts_str) )

    x=RooRealVar(x_var, 'm_{#tau}',1757,1797,'MeV')
    numBins = 100 # define here so that if I change it also the ndof change accordingly
    x.setBins(numBins)

    ######################################################
    # DEFINE PDF
    ######################################################
    
    w = RooWorkspace('w')
    getattr(w,'import')(x)
    w.factory('''RooDSCBShape::DSCB({0},
    #mu[1777, 1760,1790],
    #sigma[5,0,10],
    #alpha[1.2], n[50, 1, 150],
    #alpha, n
    )'''.format(x_var))
    #w.var('n').setConstant(False)
    signal = w.pdf('DSCB')
    # w.factory('''RooGaussian::GG({0},
    # #mu, #sigma
    # )'''.format(x_var))
    # signal = w.pdf('GG')
  
    # Fit
    fit_region = x.setRange('fit_region',1757,1797)
    result = signal.fitTo(dataSet, RooFit.Save(), RooFit.Range('fit_region'))

    # Frame
    frame = x.frame(RooFit.Title(' Combined mass KK#mu '+addTitlePlot))
    dataSet.plotOn(frame)
    signal.plotOn(frame, RooFit.LineWidth(2))

    # Legends
    signal.paramOn(frame, RooFit.Layout(0.6,0.9,0.9))
    chi2 = round(frame.chiSquare(),2)
    leg = TLegend(0.3,0,.10,.10)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(0,'#chi^{2} ='+str(chi2),'')
    frame.addObject(leg)

    c1 = TCanvas('c1', 'c1')
    frame.Draw()
    c1.Update()

    for prm in ('#mu', '#sigma', '#alpha', 'n'): # TODO: automatize finding of variables from the function
        w.var(prm).setConstant()
    
    return w, c1
    


if __name__ == '__main__':
    
    ##########################
    if args.DTF:
        DTF_label = '_DTF'
        x_var = 'Tau_DTF_Tau_M'
        addTitlePlot = 'DTF'
    else:
        DTF_label = ''
        x_var = 'Tau_M'
        addTitlePlot = ''
    ##########################
        
    # Make Dataset
    if args.dataset:
        print 'Making RooDataSet'
        dataSet = makeRooDataset('/afs/cern.ch/work/g/gdujany/LHCb/LFV/store/tau2PhiMu.root')#_triggerNotApplied.root')
        dataSet.SaveAs('RooDataSets/rooDataSet_MC.root')
    
    # Make fit
    inFile = TFile('RooDataSets/rooDataSet_MC.root')
    dataSet = inFile.Get('taus')
    w, c1 = doMCFit(dataSet, x_var, addTitlePlot)
    c1.Print('plots/plotMCFit'+DTF_label+'.pdf')
    w.SaveAs('pickles/signalShape'+DTF_label+'.root')
    
