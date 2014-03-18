#!/usr/bin/env python

##########################
###   Options parser   ###
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description = 'dataFit.py')
    parser.add_argument('-f','--DTF',help='Use DTF variables',action='store_true')
    parser.add_argument('-d','--dataset',help='make also dataset',action='store_true')
    args = parser.parse_args()
##########################

from ROOT import gSystem
gSystem.Load('../PDFs/RooDSCBShape_cxx')
from ROOT import RooDataSet, RooRealVar, RooArgSet, RooFormulaVar, RooGenericPdf, RooCmdArg, RooStats
from ROOT import RooCBShape, RooAddPdf, RooArgList, RooPlot, RooDataHist, RooFitResult, RooAbsPdf, RooGaussian, RooPolynomial, RooExponential, RooChebychev, RooDSCBShape, RooWorkspace
from ROOT import RooFit, gROOT, TStyle, gStyle, gPad
from ROOT import TFile, TCanvas, TPad, TH1F, TGraphErrors, TPad, TLegend, TPaveText, TMultiGraph, TGraphErrors, TMath
from ROOT import TH1D, TH1F, TTree, RooHistPdf, TLine, TF1
import ROOT, sys, getopt, pickle
from array import array
import sys
sys.path.append('..')
from fits import makeRooDataset


gROOT.SetBatch()

def doDataFit(dataSet, w, x_var, addTitlePlot=''):

    withD = True

    cuts_str = ''
    data = dataSet.reduce( RooFit.Cut(cuts_str) )

    x = w.var(x_var)
    x.setRange(1630,1900)
    
    #x=RooRealVar(x_var, 'm_{#tau}',1630,1900,'MeV')
    
    numBins = 90#100 # define here so that if I change it also the ndof change accordingly
    x.setBins(numBins)

    ##########################################################
    # Linear fit
    # gStyle.SetStatY(0.65) # Set y-position (fraction of pad size)
    # gStyle.SetStatX(0.5) # Set x-position (fraction of pad size)
    # gStyle.SetStatW(0.2) # Set width of stat-box (fraction of pad size)
    # gStyle.SetStatH(0.2) # Set height of stat-box (fraction of pad size)
    

    # c1 = TCanvas('c1', 'c1')
    # c1.Print('plots/plotDataFit_linear.pdf[')
    # inFile = TFile('histo.root')
    # histo = inFile.Get('Tau_M_histo__Tau_M')
    # gStyle.SetOptFit(1111)
    # histo.Fit('x++x^2++x^3+1')
    # histo.Draw()
    # c1.Update()  
    # c1.Print('plots/plotDataFit_linear.pdf')

    # params = [histo.GetFunction('x++x^2++x^3+1').GetParameter(i) for i in range(3)]
    # params[0:0] = [1]
    # print params
    # params2 = [params[i]/params[0] for i in range(len(params))]
    # print params2

    # fun_test = TF1('fun_test','{0}+{1}*x+{2}*x^2+{3}*x^3'.format(*params),1630,1810)
    # fun_test.Draw()
    # c1.Print('plots/plotDataFit_linear.pdf')
    # fun_norm = TF1('fun_test','{0}+{1}*x+{2}*x^2+{3}*x^3'.format(*params2),1630,1810)
    # fun_norm.Draw()
    # c1.Print('plots/plotDataFit_linear.pdf')  

    # # All fit linear
    # lin_pdf = TF1('lin_pdf','1++x++x^2++x^3++TMath::Gaus(x,1777,5)',1630,1810)#1747,1807)
    # lin_pdf.SetParName(4,'n_sig')
    # histo.Fit('lin_pdf','R')
    # histo.SetTitle('Linear fit: polynomial + Gaussian;m_{#tau} (MeV);')
    # histo.Draw()
    # c1.Update()  
    # c1.Print('plots/plotDataFit_linear.pdf')
    # c1.Print('plots/plotDataFitLinear.pdf')
    
    # c1.Print('plots/plotDataFit_linear.pdf]')
    
    
    ######################################################
    # DEFINE PDF
    ######################################################
    
    # Signal
    sgn_name = 'DSCB'
    signal = w.pdf(sgn_name)

    # Combinatorial Background
    if withD:
        w.factory('''RooChebychev::background('''+x_var+''',
        {a1[-0.5,-1,1],
        a2[-0.1,-1,1],
        a3[0.05,-1,1]}
        )''')
    else:
        w.factory('''RooPolynomial::background('''+x_var+''',
        {a1[params2[1],params2[1]*0.5,params2[1]*1.5],
        a2[params2[2],params2[2]*0.5,params2[2]*1.5],
        a3[params2[3]],params2[3]*0.5,params2[3]*1.5]}
        )''')
        

    # D peak
    if withD:
        w.factory('''RooCBShape::Dpeak({0},
        mean_D[1860,1830,1890],
        sigma_D[7,0,15],
        alpha_D[0.5,0,5],
        n_D[3]
        )'''.format(x_var))# Combinatorial Background
    

    # Toghether
    w.factory('''SUM::modelPdf(
    n_sig[5, -100, 100] * {0},
    n_bkg[10000000, 0, 10000000000] * background
    {1})'''.format(sgn_name,
                ',n_Dpeak[100000, 0, 100000000] * Dpeak' if withD else ''))
    modelPdf = w.pdf('modelPdf')

    # parameters = ['a1', 'a2', 'a3', 'n_sig', 'n_bkg']
    # if withD:
    #     parameters.extend(['mean_D', 'sigma_D', 'alpha_D', 'n_Dpeak'])
    # for prm in parameters:
    #     w.var(prm).setConstant(False)


    for prm in ['n_sig', 'n_bkg', 'n_Dpeak']:
        w.var(prm).setConstant(False)
    

    # ## Backup
    # # Background
    # if withD:
    #     w.factory('''RooChebychev::background('''+x_var+''',
    #     {a1[-0.5,-1,1],
    #     a2[-0.1,-1,1],
    #     a3[0.05,-1,1]}
    #     )''')
    # else:
    #     w.factory('''RooPolynomial::background('''+x_var+''',
    #     {a1[params2[1],params2[1]*0.5,params2[1]*1.5],
    #     a2[params2[2],params2[2]*0.5,params2[2]*1.5],
    #     a3[params2[3],params2[3]*0.5,params2[3]*1.5]}
    #     )''')
        
    # # Toghether
    # if withD:
    #     w.factory('''RooCBShape::Dpeak({0},
    #     mean_D[1860,1830,1890],
    #     sigma_D[7,0,15],
    #     alpha_D[0.5,0,5],
    #     n_D[3]
    #     )'''.format(x_var))

    # w.factory('''SUM::modelPdf(
    # n_sig[5, 0, 100] * {0},
    # n_bkg[10000000, 0, 10000000000] * background
    # {1})'''.format(sgn_name,
    #             ',n_Dpeak[100000, 0, 100000000] * Dpeak' if withD else ''))
    # modelPdf = w.pdf('modelPdf')
        

    # Fit
    if withD:
        fit_region = x.setRange('fit_region',1630,1900)#1747,1807)
    else:
        fit_region = x.setRange('fit_region',1630,1810)#1747,1807)
    result = modelPdf.fitTo(dataSet, RooFit.Save(), RooFit.Range('fit_region'))
   
    # Frame
    frame = x.frame(RooFit.Title(' Combined mass KK#mu '+addTitlePlot))
    dataSet.plotOn(frame)
    modelPdf.plotOn(frame,RooFit.Components(sgn_name), RooFit.LineColor(ROOT.kGreen+2), RooFit.LineStyle(2), RooFit.LineWidth(1))
    if withD:
        modelPdf.plotOn(frame,RooFit.Components('Dpeak'), RooFit.LineColor(ROOT.kRed), RooFit.LineStyle(2), RooFit.LineWidth(1))
    modelPdf.plotOn(frame,RooFit.Components('background'), RooFit.LineColor(ROOT.kBlack), RooFit.LineStyle(2), RooFit.LineWidth(1))
    modelPdf.plotOn(frame, RooFit.LineWidth(2))

    # Legends
    #w.defineSet('parameters_on_legend', 'n_bkg, n_sig, n_Dpeak, mean_D, sigma_D, alpha_D')
    parameters_on_legend = RooArgSet(w.var('n_bkg'), w.var('n_sig'), w.var('n_Dpeak'), w.var('mean_D'), w.var('sigma_D'), w.var('alpha_D'))
    modelPdf.paramOn(frame, RooFit.Layout(0.1,0.44,0.5),RooFit.Parameters(parameters_on_legend))#(0.1,0.44,0.9))
    chi2 = round(frame.chiSquare(),2)
    leg = TLegend(0.3,0,.10,.10)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(0,'#chi^{2} ='+str(chi2),'')
    frame.addObject(leg)

    c1 = TCanvas('c1', 'c1')
    frame.Draw()
    c1.Update()  
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
        dataSet = makeRooDataset('/afs/cern.ch/work/g/gdujany/LHCb/LFV/store/data2012.root')
        dataSet.SaveAs('RooDataSets/rooDataSet.root')

    # Make fit
    w = TFile('pickles/signalShape'+DTF_label+'.root').Get('w')
    dataSet = TFile('RooDataSets/rooDataSet.root').Get('taus')
    w, c1 = doDataFit(dataSet, w, x_var, addTitlePlot)
    c1.Print('plots/plotDataFit'+DTF_label+'.pdf')
