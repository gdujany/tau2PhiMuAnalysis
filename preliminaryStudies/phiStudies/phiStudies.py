#!/usr/bin/python

# sample = 'data2012'
# sample = 'tau2PhiMuFromPDs'

from ROOT import gSystem
gSystem.Load('../../PDFs/RooRelBreitWigner_cxx')
from ROOT import TFile, TH1D
from ROOT import THStack, TLegend, TCanvas, TF1
from ROOT import gROOT, gStyle
import ROOT
from array import array

m_K = 493.667
gROOT.SetBatch()

colori=[ROOT.kBlue, ROOT.kRed, ROOT.kGreen+2, ROOT.kMagenta+1, ROOT.kOrange-3, ROOT.kYellow, ROOT.kCyan]

from ROOT import RooFit, RooRealVar, RooDataHist, RooArgList, RooDataSet, RooArgSet, RooChebychev, RooAddPdf, RooPolynomial, RooExponential

def makeRooDataset():
    inFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/data2012.root'
    inFile = TFile(inFile_name)
    tree = inFile.Get('DecayTreeTuple/DecayTree')
   
    Phi_M = RooRealVar('Phi_M', 'Phi_M', 1008,1032)
    Tau_DTF_Phi_M = RooRealVar('Tau_DTF_Phi_M', 'Tau_DTF_Phi_M', 1008,1032)

    dataArgSet = RooArgSet(Phi_M, Tau_DTF_Phi_M)
    print 'Making a dataset from file', inFile_name
    dataSet = RooDataSet("phi_mass_dataset","phi_mass_dataset", tree, dataArgSet)
    dataSet.SaveAs('rooDataSet.root')
    return dataSet



    
def makeFit():

    inFile = TFile('rooDataSet.root')
    dataSet = inFile.Get('phi_mass_dataset')
    
    # Fit m_DTF_Phi
    gStyle.SetOptFit(1111)
    #histo = histos['m_DTF_Phi']
    x_var = 'Tau_DTF_Phi_M' #'Phi_M'
    #x_var = 'Phi_M'
    x = RooRealVar(x_var, 'm_{#Phi}', 1008,1032, 'MeV')
    #x = RooRealVar(x_var, 'm_{#Phi}', 1010,1027, 'MeV')
    x.setBins(200)
    #ral = RooArgList(x)
    #dh = RooDataHist ("dh","dh",ral,RooFit.Import(histo))
    
    
    # Signal
    mean = RooRealVar("#mu","#mu",1020,1010,1025) 
    gamma = RooRealVar("#Gamma_{0}","#Gamma",3,0.1,10)
    spin = RooRealVar("J","J",1)
    radius = RooRealVar("radius","radius",0.003)
    m_K = 493.677
    m_a = RooRealVar("m_a","m_a",m_K)
    m_b = RooRealVar("m_b","m_b",m_K)
    #signal = ROOT.RooBreitWigner('BW','BW',x,mean, gamma)
    signal = ROOT.RooRelBreitWigner('BW','BW',x,mean, gamma,spin,radius,m_a,m_b)
    

    # Background
    a1 = RooRealVar('a0','a0',0.,-0.0000001,0.0000001) #,0.5,0.,1.)
    #a2 = RooRealVar('a1','a1',0.1,-1.,1.) #-0.2,0.,1.)
    #a3 = RooRealVar('a2','a2',-0.1,1.,-1.)
    esp = RooRealVar('esp','esp',0.,-0.5,0.5) #,0.5,0.,1.)
    #background = RooChebychev('background','Background',x,RooArgList(a1))
    #background = RooPolynomial('background','Background',x,RooArgList(a1))
    background = RooExponential('background','Background',x,esp)
   
    # Toghether
    pdf_list = RooArgList(signal, background)   
    ratio_SB = RooRealVar("ratio_SB","ratio_SB",0.7, 0, 1)
    ratio_list = RooArgList(ratio_SB)
    modelPdf = RooAddPdf('ModelPdf', 'ModelPdf', pdf_list, ratio_list)

    # Fit
    fit_region = x.setRange("fit_region",1011,1027)
    result = modelPdf.fitTo(dataSet, RooFit.Save(), RooFit.Range("fit_region"))

    # Frame
    title = ' #Phi mass '+('DTF' if x_var=='Tau_DTF_Phi_M' else '')
    frame = x.frame(RooFit.Title(title))
    dataSet.plotOn(frame)
    modelPdf.paramOn(frame, RooFit.Layout(0.1,0.44,0.9))
    signal_set = RooArgSet(signal)
    modelPdf.plotOn(frame,RooFit.Components(signal_set), RooFit.LineColor(ROOT.kGreen+2), RooFit.LineStyle(2), RooFit.LineWidth(1))
    background_set = RooArgSet(background)
    modelPdf.plotOn(frame,RooFit.Components(background_set), RooFit.LineColor(ROOT.kBlack), RooFit.LineStyle(2), RooFit.LineWidth(1))
    modelPdf.plotOn(frame, RooFit.LineWidth(2))
    
    chi2 = round(frame.chiSquare(),2)
    leg = TLegend(0.3,0,.10,.10)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(0,'#chi^{2} ='+str(chi2),'')
    frame.addObject(leg)

    c1 = TCanvas('c1', 'c1')
    frame.Draw()
    c1.Update()  
    if x_var == 'Phi_M': 
        c1.Print('plotPhi.pdf')
    else:
        c1.Print('plotPhi_DTF.pdf')
    


   #  # Traditional Root way to fit
#     func = TF1('myBW', '[0]*TMath::BreitWigner(x,[1],[2])', 1010,1025)
# #    func = TF1('myfunc', '[0]*TMath::Gaus(x,[1],[2])', 1010,1025)
#     func = TF1('myfunc', '[0]*TMath::Voigt(x-[1],[2],[3])', 1010,1025)
#     func.SetParameter(0,1048)
#     func.SetParName(0,'Norm')
#     func.SetParameter(1,1020)
#     func.SetParName(1,'mean')
#     func.SetParameter(2,4)
#     func.SetParName(2,'gamma')

#     func = TF1('myfunc', '[0]*TMath::Voigt(x-[1],[2],[3])', 1010,1025)
#     func.SetParameter(0,1048)
#     func.SetParName(0,'Norm')
#     func.SetParameter(1,1020)
#     func.SetParName(1,'mean')
#     func.SetParameter(2,4)
#     func.SetParName(2,'sigma')
#     func.SetParameter(3,4)
#     func.SetParName(2,'gamma')
    
#     histo.Fit('myfunc')
#     #histo.Fit('gaus')
#     histo.Draw()
#     c1.Update()  
#     c1.Print(outFile_name)
 

  #  c1.Print(outFile_name+']')






if __name__ == '__main__':
    
    #makeRooDataset()
    makeFit()
   
