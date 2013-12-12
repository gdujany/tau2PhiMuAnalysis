#!/usr/bin/python

# sample = 'data2012'
# sample = 'tau2PhiMuFromPDs'

from __future__ import division
from ROOT import TFile, TH1, TH1D, TH2D, TGraphErrors, TMultiGraph
from ROOT import THStack, TLegend, TCanvas, TF1
from ROOT import gROOT, gStyle
import ROOT
from array import array
from math import sqrt

m_pi = 139.57018
gROOT.SetBatch()

def makeHistos():

    from ROOT import TTree
    
    histos = {}
    histos['background'] = TH2D('background', 'background;m_{#tau} [MeV];probNNmu',100,1600,1950,20,0,1)
    histos['signal'] = TH2D('signal', 'signal;m_{#tau} [MeV];probNNmu',100,1600,1950,20,0,1)

    inFile = {}
    for key, sample in zip(['background','signal'],['data2012', 'tau2PhiMuFromPDs']):
        inFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/'+sample+'.root'
        inFile[key] = TFile(inFile_name)
        tree = inFile[key].Get('DecayTreeTuple/DecayTree')

        tree.SetBranchStatus("*",0)
        branches = ['Tau_M', 'Mu_ProbNNmu']
        for var in branches:
            tree.SetBranchStatus(var,1)
            exec var+' = array("d",[0])'
            exec "tree.SetBranchAddress( '"+var+"', "+var+" )"

        nEvents = tree.GetEntries()
        #nEvents = 10000
        for cont, entrie in enumerate(tree):
            if cont == nEvents: break
            if cont % 20000 == 0:
                print 'processing entrie ', cont, ' / ', nEvents,' : ', (cont*100)/nEvents,'%'

            # Fill Histos
            histos[key].Fill(Tau_M[0], Mu_ProbNNmu[0])
                
    outFile = TFile('histos.root','RECREATE')
    for histo in histos.values():
        histo.Write()
    outFile.Close()
    for file in inFile.values():
        file.Close()


colori=[ROOT.kBlue, ROOT.kRed, ROOT.kGreen+2, ROOT.kMagenta+1, ROOT.kOrange-3, ROOT.kYellow, ROOT.kCyan]
markersA=[20,21,22,23,29,33,34]
markersC=[24,25,26,32,30,27,28]

def setPlotAttributes(graph, color = ROOT.kBlue, markerStyle = 20):
    graph.SetMarkerStyle(markerStyle)
    graph.SetMarkerColor(color)
    graph.SetLineColor(color)

def drawMultiPlot(outFile_name='plots.pdf',title='', plot_name='',logy=False, squarePad=False, **h_dict):
    #hs = THStack('hs',title)
    hs = TMultiGraph('hs',title)
    leg = TLegend(.80, 0.83, .97, .96,"")
    if squarePad:
        c2 = TCanvas('c2', 'c2',700,700)
    else:
        c2 = TCanvas('c2', 'c2')
    
    for cont, (label, histo) in enumerate(h_dict.items()):
        setPlotAttributes(histo, colori[cont], markersA[cont])
        hs.Add(histo.Clone())
        leg.AddEntry(histo,label,'p')

    if logy: c2.SetLogy()
    hs.Draw('ap')#('nostack')
    leg.Draw("same")
    leg.SetFillColor(0)
    c2.Update()  
    c2.Print(outFile_name)
    #c2.Print('plots/'+sample+'/'+plot_name+'.pdf')
    return c2


class SigBkg:
    def __init__(self, sig, bkg, s_sig=0, s_bkg=0):
        self.sig = sig
        self.bkg = bkg
        self.s_sig = s_sig
        self.s_bkg = s_bkg

    @property
    def SoverB(self):
        return self.sig/self.bkg

    @property
    def s_SoverB(self):
        return self.SoverB * sqrt( (self.s_sig/self.sig)**2 + (self.s_bkg/self.bkg)**2 )

    @property
    def SoverSqrtB(self):
        return self.sig/sqrt(self.bkg)

    @property
    def s_SoverSqrtB(self):
        return self.SoverSqrtB * sqrt( (self.s_sig/self.sig)**2 + 0.25*(self.s_bkg/self.bkg)**2 )


def makePlots():
    
    histoFile = TFile('histos.root')
    histos = {}
    for key in histoFile.GetListOfKeys():
        histos[key.GetName()] = histoFile.Get(key.GetName())

    SR_binXMin = histos['signal'].GetXaxis().FindBin(1747)
    SR_binXMax = histos['signal'].GetXaxis().FindBin(1807)

    integral = {}
    integral_SR = {}    
    TH1.SetDefaultSumw2(ROOT.kTRUE)
    for key, histo in histos.items():
        integral[key] = histo.Integral()
        integral_SR[key] = histo.Integral(SR_binXMin, SR_binXMax,1,histo.GetNbinsY())
        #histo.Scale(1./integral[key])

    
    merit = {}
    merit_SR = {}
    
    cuts = [i/100. for i in range(0,100,5)]
    for cut in cuts:

        binYMin = histos['signal'].GetYaxis().FindBin(cut)

        # Evaluate sig and bkg for all interval
        tmp = histos['signal'].Integral(1, histos['signal'].GetNbinsX(), binYMin, histos['signal'].GetNbinsY())
        sig = tmp/integral['signal']
        s_sig = sqrt(tmp)/integral['signal']
        tmp = histos['background'].Integral(1, histos['background'].GetNbinsX(), binYMin, histos['background'].GetNbinsY())
        bkg = tmp/integral['background']
        s_bkg = sqrt(tmp)/integral['background']
        merit[cut] = SigBkg(sig, bkg, s_sig, s_bkg)
        #print cut, sig, s_sig, bkg, s_bkg

        # Evaluate sig and bkg for signal region        
        tmp = histos['signal'].Integral(SR_binXMin, SR_binXMax, binYMin, histos['signal'].GetNbinsY())
        sig = tmp/integral_SR['signal']
        s_sig = sqrt(tmp)/integral_SR['signal']
        tmp = histos['background'].Integral(SR_binXMin, SR_binXMax, binYMin, histos['background'].GetNbinsY())
        bkg = tmp/integral_SR['background']
        s_bkg = sqrt(tmp)/integral_SR['background']
        merit_SR[cut] = SigBkg(sig, bkg, s_sig, s_bkg)
        #print cut, sig, s_sig, bkg, s_bkg, '\n'

    def graph_labels(func, region):
        func_label = dict(
            SoverB = '(S/B) / (S_{0}/B_{0})',
            SoverSqrtB = '(S/#sqrt{B}) / (S_{0}/#sqrt{B_{0}})',
            sig = 'S/S_{0}',
            bkg = 'B/B_{0}',
            )
        region_label = '' if region=='' else ' SR'
        return func_label[func]+region_label
            
    # Make TGraphs
    graphs = {}
    x = array('d',cuts)
    s_x = array('d',[0 for i in cuts])
    for region, dd in zip(('','_SR'),(merit, merit_SR)):
        for func in ('SoverB', 'SoverSqrtB','sig','bkg'):
            y = array('d', [getattr(dd[cut],func) for cut in cuts])
            s_y = array('d', [getattr(dd[cut],'s_'+func) for cut in cuts])
            graphs[graph_labels(func, region)] = TGraphErrors(len(x),x,y,s_x,s_y)

    

    outFile_name = 'plots.pdf'
    c1 = TCanvas('c1', 'c1')
    c1.Print(outFile_name+'[')

    print len(graphs)
    drawMultiPlot(outFile_name,'title', 'plotName',logy=False, squarePad=False, **graphs)
    
    c1.Print(outFile_name+']')




if __name__ == '__main__':
    
    #makeHistos()
    makePlots()
    
