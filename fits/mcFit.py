#!/usr/bin/python

from ROOT import gSystem
gSystem.Load('My_double_CB/My_double_CB_cxx')
from ROOT import My_double_CB
from ROOT import RooDataSet, RooRealVar, RooArgSet, RooFormulaVar, RooGenericPdf, RooCmdArg, RooStats
from ROOT import RooCBShape, RooAddPdf, RooArgList, RooPlot, RooDataHist, RooFitResult, RooAbsPdf, RooGaussian, RooPolynomial, RooExponential, RooChebychev
from ROOT import RooFit, gROOT, TStyle, gStyle, gPad
from ROOT import TFile, TCanvas, TPad, TH1F, TGraphErrors, TPad, TLegend, TPaveText, TMultiGraph, TGraphErrors, TMath
from ROOT import TH1D, TH1F, TTree, RooHistPdf, TLine, TF1
import ROOT, sys, getopt
from array import array
from pyUtils import *

gROOT.SetBatch()
 
def doMCFit(dataSet):
    
    x_var = 'Tau_M' #'Tau_DTF_Tau_M'
    
    cuts_str = ''
    data = dataSet.reduce( RooFit.Cut(cuts_str) )

    x=RooRealVar(x_var, 'm_{#tau}',1757,1797,'MeV')
    numBins = 100 # define here so that if I change it also the ndof change accordingly
    x.setBins(numBins)

    ######################################################
    # DEFINE PDF
    ######################################################
    # Signal
    mean = RooRealVar('#mu','mean',1777, 1760,1790) 
    sigma = RooRealVar('#sigma','sigma',5,0,10)
    gamma = RooRealVar('#Gamma','gamma',5,0,10)
    alpha = RooRealVar('#alpha', 'alpha', 1.5)#, 0.1, 10)
    param_n = RooRealVar('n','param_n', 10, 0.1, 100)
    signal = ROOT.RooGaussian('signal','signal',x,mean,sigma)
    signal = ROOT.RooBreitWigner('signal','signal',x,mean,gamma)
    signal = ROOT.RooCBShape('CB','CB', x, mean, sigma, alpha, param_n)
    signal = ROOT.My_double_CB('DSCB','DSCB', x, mean, sigma, alpha, param_n, alpha, param_n)
    #signal = ROOT.RooGenericPdf('SuperGaus','TMath::Exp(-(@0-@1)^2/(2*@2) - (@0-@1)^4/(4*@3))', RooArgList(x,mean,sigma,gamma))
    #signal = ROOT.RooVoigtian('signal','signal',x,mean,sigma,gamma)

    # # Sum 2 Gaussians
    # gaus1 = ROOT.RooGaussian('gaus1','gaus1',x,mean,sigma)
    # gaus2 = ROOT.RooGaussian('gaus2','gaus2',x,mean,gamma)
    # ratio_12 = RooRealVar("ratio_12","ratio_12",0.5, 0, 1)
    # pdf_list = RooArgList(gaus1, gaus2)
    # ratio_list = RooArgList(ratio_12)
    # signal = RooAddPdf('ModelPdf', 'ModelPdf', pdf_list, ratio_list)
    

    # Fit
    fit_region = x.setRange('fit_region',1757,1797)
    result = signal.fitTo(dataSet, RooFit.Save(), RooFit.Range('fit_region'))

    # Frame
    frame = x.frame(RooFit.Title(' Combined mass KK#mu '))
    dataSet.plotOn(frame)
    signal_set = RooArgSet(signal)
    signal.plotOn(frame, RooFit.LineWidth(2))

    # Legends
    #parameters_on_legend = RooArgSet(n_bkg,n_sig,n_Dpeak,mean_D,sigma_D, alpha_D)
    signal.paramOn(frame, RooFit.Layout(0.6,0.9,0.9))#,RooFit.Parameters(parameters_on_legend))#(0.1,0.44,0.9))
    chi2 = round(frame.chiSquare(),2)
    leg = TLegend(0.3,0,.10,.10)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(0,'#chi^{2} ='+str(chi2),'')
    frame.addObject(leg)

    c1 = TCanvas('c1', 'c1')
    frame.Draw()
    c1.Update()  
    c1.Print('plotMCFit.pdf')


if __name__ == '__main__':

    # # Make Dataset
    # dataSet = makeRooDataset('/afs/cern.ch/work/g/gdujany/LHCb/LFV/store/tau2PhiMuFromPDs.root')
    # dataSet.SaveAs('rooDataSet_MC.root'); 

    # Make fit
    inFile = TFile('rooDataSet_MC.root')
    dataSet = inFile.Get('taus')
    doMCFit(dataSet)
