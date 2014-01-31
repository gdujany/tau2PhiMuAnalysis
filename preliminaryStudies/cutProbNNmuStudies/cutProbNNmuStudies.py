#!/usr/bin/env python

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


colori=[ROOT.kBlue, ROOT.kRed, ROOT.kGreen+2, ROOT.kMagenta+1, ROOT.kOrange-3, ROOT.kYellow, ROOT.kCyan, ROOT.kBlack]
markersA=[20,21,22,23,29,33,34,8]
markersC=[24,25,26,32,30,27,28,4]

def setPlotAttributes(graph, color = ROOT.kBlue, markerStyle = 20):
    graph.SetMarkerStyle(markerStyle)
    graph.SetMarkerColor(color)
    graph.SetLineColor(color)

def drawMultiPlot(outFile_name='plots.pdf',title='', plot_name='',logy=False, squarePad=False, **h_dict):
    #hs = THStack('hs',title)
    hs = TMultiGraph('hs',title)
    leg = TLegend(.80, 0.80, .99, .99,"")
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
    c2.Print('plotsCutProbNNmu/'+plot_name+'.pdf')
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

    @property
    def Punzi(self):
        return self.sig/(1+sqrt(self.bkg))

    @property
    def s_Punzi(self):
        return self.Punzi * sqrt( (self.s_sig/self.sig)**2 + (1/(4*self.bkg)*(self.s_bkg/(1+self.bkg))**2 ) )


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
            Punzi = '(S/S_{0})/(1+#sqrt{B}/#sqrt{B_{0}})', 
            sig = 'S/S_{0}',
            bkg = 'B/B_{0}',
            sqrtB = '#sqrt{B}/#sqrt{B_{0}}',
            )
        region_label = '' if region=='' else ' SR'
        return func_label[func]+region_label


    formula = ' p0 e^{p2 x^{p3}} - x^{p4}'
    # Make TGraphs
    graphs = {}
    cuts = cuts[1:]
    x = array('d',cuts)
    s_x = array('d',[0 for i in cuts])
    for region, dd in zip(('','_SR'),(merit, merit_SR)):
        for func in ('SoverB', 'SoverSqrtB', 'Punzi', 'sig','bkg'):
            y = array('d', [getattr(dd[cut],func) for cut in cuts])
            s_y = array('d', [getattr(dd[cut],'s_'+func) for cut in cuts])
            graphs[func+region] = TGraphErrors(len(x),x,y,s_x,s_y)
            graphs[func+region].SetNameTitle(func+region,graph_labels(func, region)+formula+';probNNmu > X;'+graph_labels(func, region).split('SR')[0])
        # sqrt(B)
        func = 'sqrtB'
        y = array('d', [sqrt(dd[cut].bkg) for cut in cuts])
        s_y = array('d', [dd[cut].s_bkg/(2 * sqrt(dd[cut].bkg)) for cut in cuts])
        graphs['sqrtB'+region] = TGraphErrors(len(x),x,y,s_x,s_y) 
        graphs['sqrtB'+region].SetNameTitle(func+region,graph_labels(func, region)+formula+';probNNmu > X;'+graph_labels(func, region).split('SR')[0])
    

    outFile_name = 'plots.pdf'
    c1 = TCanvas('c1', 'c1')
    c1.Print(outFile_name+'[')

    drawMultiPlot(outFile_name,'Figures of merit;probNNmu > X;', 'figOfMerit',logy=False, squarePad=False,
                       **{graph_labels(func,region):graphs[func+region] for func in ('SoverB', 'SoverSqrtB', 'Punzi') for region in ('','_SR')})
    #print c2
    #c2.SaveAs('a.pdf')
    drawMultiPlot(outFile_name,'Signal or background yields normalized;probNNmu > X;', 'yields',logy=False, squarePad=False,
                       **{graph_labels(func,region):graphs[func+region] for func in ('sig', 'bkg','sqrtB') for region in ('','_SR')})

    # fit
    gStyle.SetOptFit(1111)
    
    myfun = TF1('myfun', '[0]*TMath::Exp(-[2]*x^[3])-[1]*x^[4]', 0,1)
    myfun.SetParameters(1,1,1,1,1)

    
    graphs_fitParams = {}
    x = array('d', range(5))
    s_x = array('d', [0 for i in range(5)])
    for key in ('sig', 'sig_SR', 'bkg', 'bkg_SR', 'sqrtB', 'sqrtB_SR'):
        graphs[key].Fit('myfun')
        graphs[key].Draw('ap')
        c1.Update()
        c1.Print(outFile_name)
        c1.Print('plotsCutProbNNmu/'+key+'.pdf')

        y = graphs[key].GetFunction('myfun').GetParameters()
        s_y = graphs[key].GetFunction('myfun').GetParErrors()
        #y = array('d',graphs[key].GetFunction('myfun').GetParameters())
        #s_y = array('d',graphs[key].GetFunction('myfun').GetParErrors())
        graphs_fitParams[key] = TGraphErrors(len(x),x,y,s_x,s_y)

    drawMultiPlot(outFile_name,'Fit parameters;parameter number;', 'fitParams',logy=False, squarePad=False,
                  **{graph_labels(key.split('_')[0],'SR' if 'SR' in key else ''):graphs_fitParams[key] for key in graphs_fitParams.keys()})

    # Fit parameters difference wrt sig (S/S_0)
    graphs_fitParams2 = {}
    fitParams = {}
    s_fitParams = {}
    for key in ('sig', 'sig_SR', 'bkg', 'bkg_SR', 'sqrtB', 'sqrtB_SR'):
        fitParams[key] = [graphs_fitParams[key].GetY()[i] for i in range(graphs_fitParams['sig'].GetN())]
        s_fitParams[key] = [graphs_fitParams[key].GetErrorY(i) for i in range(graphs_fitParams['sig'].GetN())]
           
    for key in ('sig', 'sig_SR', 'bkg', 'bkg_SR', 'sqrtB', 'sqrtB_SR'):
    
    
        y = array('d',[(i-j) for i, j in zip(fitParams[key],fitParams['sig'])])
        s_y = array('d',[s_i for s_i, j in zip(s_fitParams[key],fitParams['sig'])])
        graphs_fitParams2[key] = TGraphErrors(len(x),x,y,s_x,s_y)

    drawMultiPlot(outFile_name,'Fit parameters difference wrt S/S_{0};parameter number;', 'firParamsNorm',logy=False, squarePad=False,
                  **{graph_labels(key.split('_')[0],'SR' if 'SR' in key else ''):graphs_fitParams2[key] for key in graphs_fitParams2.keys()})
    
    c1.Print(outFile_name+']')




if __name__ == '__main__':
    
    #makeHistos()
    makePlots()
    
