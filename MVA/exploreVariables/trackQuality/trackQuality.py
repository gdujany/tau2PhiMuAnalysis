#!/usr/bin/env python

import ROOT as r
from random import random
import sys
sys.path.append('/afs/cern.ch/user/g/gdujany/LHCb/LFV/tau2PhiMuAnalysis/MVA/exploreVariables')
from compareVariables import *


if __name__ == '__main__':

    r.gStyle.SetOptStat(0)
    r.gROOT.SetBatch(True)

    outFile_name = 'test.pdf' #'test_triggerNotApplied.pdf'

    # dataFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/data2012_triggerNotApplied.root'
    # MCFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/tau2PhiMu_triggerNotApplied.root'
    dataFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/data2012.root'
    MCFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/tau2PhiMu.root'
    dataFile = r.TFile(dataFile_name)
    MCFile = r.TFile(MCFile_name)
    dataTree = dataFile.Get('DecayTreeTuple/DecayTree')
    MCTree = MCFile.Get('DecayTreeTuple/DecayTree')

    c = r.TCanvas('c','c')
    c.Print(outFile_name+'[')

    variables = ['Mu_TRCHI2DOF', 'KPlus_TRCHI2DOF']
    variables = variables[:]
    
    region = {var: '' for var in variables}
    region['Tau_BPVDIRA'] = (0.9998, 1.)
    

        
    for var in variables:
        for cont, cut in enumerate(('', '(Phi_M<1015 || Phi_M>1025)'.format(var), '(Phi_M>1015 && Phi_M<1025)')):
        
            h_data = getHisto(dataTree, var, region[var], cut=cut)
            h_data.Scale(1./h_data.Integral())
            h_MC = getHisto(MCTree, var, region[var], cut=cut)
            h_MC.Scale(1./h_MC.Integral())
            c =  drawMultiPlot({'Signal':h_MC, 'Background':h_data}, title=var+' '+cut+';'+var+';A.U.', logy=False)      
            c.Print(outFile_name)
            c.Print('plotsTrackQuality/'+var+str(cont)+'.pdf')


    variables = ('nSPDHits', 'nTracks')
        
    for var in variables:
        h_data = getHisto(dataTree, var,  cut=cut)
        h_data.Scale(1./h_data.Integral())
        h_MC = getHisto(MCTree, var, cut=cut)
        h_MC.Scale(1./h_MC.Integral())
        c =  drawMultiPlot({'Signal':h_MC, 'Background':h_data}, title=var+';'+var+';A.U.', logy=False)      
        c.Print(outFile_name)
        c.Print('plotsTrackQuality/'+var+'.pdf')

    espressions = dict(KPlus_TRCHI2DOF_vs_nSPDHits = 'KPlus_TRCHI2DOF:nSPDHits',
                       KPlus_TRCHI2DOF_vs_nTracks = 'KPlus_TRCHI2DOF:nTracks',
                       KPlus_TRCHI2DOF_vs_PT = 'KPlus_TRCHI2DOF:KPlus_PT',
                       )
        
    for var, expr in espressions.items():
        h_data = getHisto(dataTree, var, expr = expr)
        h_data.SetTitle(';'+var.split('_')[-1]+';KPlus_TRCHI2DOF')
        h_data.Draw('colz')       
        c.Print(outFile_name)
        var = ''.join(var.split('.'))
        c.Print('plotsTrackQuality/'+var+'.pdf')
        profile = h_data.ProfileX()
        profile.Draw()
        c.Print(outFile_name)
        c.Print('plotsTrackQuality/'+var+'_profile.pdf')
    

    # histos = {}
    # histos[]

    
   
    
    c.Print(outFile_name+']')
