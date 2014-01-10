#!/usr/bin/python

from ROOT import gSystem
gSystem.Load('../PDFs/RooDSCBShape_cxx')
from ROOT import RooDataSet, RooRealVar, RooArgSet, RooFormulaVar, RooGenericPdf, RooCmdArg, RooStats
from ROOT import RooCBShape, RooAddPdf, RooArgList, RooPlot, RooDataHist, RooFitResult, RooAbsPdf, RooGaussian, RooPolynomial, RooExponential, RooChebychev, RooDSCBShape
from ROOT import RooFit, gROOT, TStyle, gStyle, gPad
from ROOT import TFile, TCanvas, TPad, TH1F, TGraphErrors, TPad, TLegend, TPaveText, TMultiGraph, TGraphErrors, TMath
from ROOT import TH1D, TH1F, TTree, RooHistPdf, TLine, TF1
import ROOT, sys, getopt, pickle
from array import array
from pyUtils import *

gROOT.SetBatch()

def doDataFit(dataSet):

    withD = True

    x_var = 'Tau_M' #'Tau_DTF_Tau_M'

    cuts_str = ''
    data = dataSet.reduce( RooFit.Cut(cuts_str) )
    #if withD:
    x=RooRealVar(x_var, 'm_{#tau}',1630,1900,'MeV')
    #else:
    #    x=RooRealVar(x_var, 'm_{#tau}',1600,1950,'MeV')
    numBins = 90#100 # define here so that if I change it also the ndof change accordingly
    x.setBins(numBins)

    ##########################################################
    # Linear fit
    gStyle.SetStatY(0.65) # Set y-position (fraction of pad size)
    gStyle.SetStatX(0.5) # Set x-position (fraction of pad size)
    gStyle.SetStatW(0.2) # Set width of stat-box (fraction of pad size)
    gStyle.SetStatH(0.2) # Set height of stat-box (fraction of pad size)
    
    # # make histogram
    # x_=RooRealVar(x_var, 'm_{#tau}',1630,1810,'MeV')
    # print 1
    # data_h = data.binnedClone()
    # print 2
    # histo = data_h.createHistogram(x_var+'_histo', x_)
    # print 3
    # histo.SaveAs('histo.root')

    c1 = TCanvas('c1', 'c1')
    c1.Print('plotDataFit_linear.pdf[')
    inFile = TFile('histo.root')
    histo = inFile.Get('Tau_M_histo__Tau_M')
    gStyle.SetOptFit(1111)
    histo.Fit('x++x^2++x^3+1')
    histo.Draw()
    c1.Update()  
    c1.Print('plotDataFit_linear.pdf')

    params = [histo.GetFunction('x++x^2++x^3+1').GetParameter(i) for i in range(3)]
    params[0:0] = [1]
    print params
    params2 = [params[i]/params[0] for i in range(len(params))]
    print params2

    fun_test = TF1('fun_test','{0}+{1}*x+{2}*x^2+{3}*x^3'.format(*params),1630,1810)
    fun_test.Draw()
    c1.Print('plotDataFit_linear.pdf')
    fun_norm = TF1('fun_test','{0}+{1}*x+{2}*x^2+{3}*x^3'.format(*params2),1630,1810)
    fun_norm.Draw()
    c1.Print('plotDataFit_linear.pdf')  

    # All fit linear
    lin_pdf = TF1('lin_pdf','1++x++x^2++x^3++TMath::Gaus(x,1777,5)',1630,1810)#1747,1807)
    lin_pdf.SetParName(4,'n_sig')
    histo.Fit('lin_pdf','R')
    histo.SetTitle('Linear fit: polynomial + Gaussian;m_{#tau} (MeV);')
    histo.Draw()
    c1.Update()  
    c1.Print('plotDataFit_linear.pdf')
    c1.Print('plotDataFitLinear.pdf')
    
    c1.Print('plotDataFit_linear.pdf]')
    
    
    ######################################################
    # DEFINE PDF
    ######################################################
    # Signal
    mean = RooRealVar('mean','mean',1777) 
    sigma = RooRealVar('sigma','sigma',5)
    signal = ROOT.RooGaussian('signal','signal',x,mean,sigma)
    #signal = pickle.load(open('pickles/pdf.pkl','rb'))

    # Background
    if withD:
        a1 = RooRealVar('a1','a1',-0.5,-1,1)#16.,0.,100.)# ,0.5,0.,1.)
        a2 = RooRealVar('a2','a2',-0.1,-1,1)#-0.0075,-10.,10.) #-0.2,0.,1.)
        a3 = RooRealVar('a3','a3',0.05,-1,1)
        background = RooChebychev('background','Background',x,RooArgList(a1,a2,a3))
    else:
        a1 = RooRealVar('a1','a1',params2[1],params2[1]*0.5,params2[1]*1.5)#16.,0.,100.)# ,0.5,0.,1.)
        a2 = RooRealVar('a2','a2',params2[2],params2[2]*0.5,params2[2]*1.5)#-0.0075,-10.,10.) #-0.2,0.,1.)
        a3 = RooRealVar('a3','a3',params2[3],params2[3]*0.5,params2[3]*1.5)#1,-10.,10.)
        esp = RooRealVar('esp','esp',0.,-0.5,0.5) #,0.5,0.,1.)
        background = RooPolynomial('background','Background',x,RooArgList(a1,a2,a3))
    
    #background = RooExponential('background','Background',x,esp)
   
    # Toghether
    pdf_list = RooArgList(signal, background)   
    ratio_SB = RooRealVar("ratio_SB","ratio_SB",0.1, 0, 1)
    n_sig = RooRealVar("n_sig","n_sig",5, 0, 100)
    n_bkg =  RooRealVar("n_bkg","n_bkg",10000000, 0, 10000000000)
    #ratio_list = RooArgList(ratio_SB)
    ratio_list = RooArgList(n_sig, n_bkg)
    
    #withD=False
    # With D peak
    if withD:
        mean_D = RooRealVar('mean_D','mean_D',1860,1830,1890) 
        sigma_D = RooRealVar('sigma_D','sigma_D',7,0,20)
        alpha_D = RooRealVar('alpha_D','alpha_D',1,0,10)
        n_D = RooRealVar('n_D','n_D',3)
        #Dpeak = ROOT.RooGaussian('Dpeak','Dpeak',x,mean_D,sigma_D)
        Dpeak = ROOT.RooCBShape('Dpeak','Dpeak',x,mean_D,sigma_D,alpha_D,n_D)
        n_Dpeak = RooRealVar("n_Dpeak","n_Dpeak",100000, 0, 100000000)
        ratio_list.add(n_Dpeak)
        pdf_list.add(Dpeak)

    modelPdf = RooAddPdf('ModelPdf', 'ModelPdf', pdf_list, ratio_list)
        
        

    # Fit
    if withD:
        fit_region = x.setRange('fit_region',1630,1900)#1747,1807)
    else:
        fit_region = x.setRange('fit_region',1630,1810)#1747,1807)
    result = modelPdf.fitTo(dataSet, RooFit.Save(), RooFit.Range('fit_region'))
   
    # Frame
    frame = x.frame(RooFit.Title(' Combined mass KK#mu '))
    dataSet.plotOn(frame)
    signal_set = RooArgSet(signal)
    modelPdf.plotOn(frame,RooFit.Components(signal_set), RooFit.LineColor(ROOT.kGreen+2), RooFit.LineStyle(2), RooFit.LineWidth(1))
    if withD:
        Dpeak_set = RooArgSet(Dpeak)
        modelPdf.plotOn(frame,RooFit.Components(Dpeak_set), RooFit.LineColor(ROOT.kRed), RooFit.LineStyle(2), RooFit.LineWidth(1))
    background_set = RooArgSet(background)
    modelPdf.plotOn(frame,RooFit.Components(background_set), RooFit.LineColor(ROOT.kBlack), RooFit.LineStyle(2), RooFit.LineWidth(1))
    modelPdf.plotOn(frame, RooFit.LineWidth(2))

    # Legends
    parameters_on_legend = RooArgSet(n_bkg,n_sig,n_Dpeak,mean_D,sigma_D, alpha_D)
    modelPdf.paramOn(frame, RooFit.Layout(0.1,0.44,0.5))#,RooFit.Parameters(parameters_on_legend))#(0.1,0.44,0.9))
    chi2 = round(frame.chiSquare(),2)
    leg = TLegend(0.3,0,.10,.10)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(0,'#chi^{2} ='+str(chi2),'')
    frame.addObject(leg)

    c1 = TCanvas('c1', 'c1')
    frame.Draw()
    c1.Update()  
    c1.Print('plotDataFit.pdf')


if __name__ == '__main__':

    # Make Dataset
    # dataSet = makeRooDataset('/afs/cern.ch/work/g/gdujany/LHCb/LFV/store/data2012.root')
    # dataSet.SaveAs('rooDataSet.root')

    # Make fit
    inFile = TFile('rooDataSet.root')
    dataSet = inFile.Get('taus')
    doDataFit(dataSet)
