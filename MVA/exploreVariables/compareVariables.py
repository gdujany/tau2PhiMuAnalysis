#!/usr/bin/env python

import ROOT as r
from random import random

def getHisto(tree, var,region=None, expr=None, cut=''):
    if not expr: expr = var
    cuts = []
    if cut != '': cuts.append(cut)
    #cuts += ['Mu_ProbNNmu-1.33*Mu_ProbNNpi>0.6']
    cuts += ['(Tau_M<1800 || Tau_M>1890)']
    if region: cuts += [expr+'>'+str(region[0]), expr+'<'+str(region[1])]
    cut_string = ' && '.join(cuts)
    tree.Draw(expr+'>>'+var, cut_string)
    #raw_input('Press enter to continue')
    h = r.gDirectory.Get(var)
    r.gROOT.cd()
    return h.Clone(var+str(random))

colori=[r.kBlue, r.kRed, r.kGreen+2, r.kMagenta+1, r.kOrange-3, r.kYellow, r.kCyan]

def setPlotAttributes(graph, color = r.kBlue, markerStyle = 20):
    graph.SetMarkerStyle(markerStyle)
    graph.SetMarkerColor(color)
    graph.SetLineColor(color)

def drawMultiPlot(h_dict, title='', plot_name='',logy=False, squarePad=False, logx=False):
    if squarePad:
        c = r.TCanvas('c', 'c',700,700)
    else:
        c = r.TCanvas('c', 'c')
        
    c.hs = r.THStack('hs',title)
    c.leg = r.TLegend(.80, 0.83, .97, .96,"")
    
    
    for cont, (label, histo) in enumerate(h_dict.items()):
        setPlotAttributes(histo, colori[cont])
        c.hs.Add(histo.Clone())
        c.leg.AddEntry(histo,label,'l')

    if logy: c.SetLogy()
    if logx: c.SetLogx()
    c.hs.Draw('nostack')
    c.leg.Draw("same")
    c.leg.SetFillColor(0)
    c.Update()
    return c


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

    #variables = [i.GetName() for i in dataTree.GetListOfBranches()]
    variables = ['Tau_BPVDIRA', 'Tau_BPVIPCHI2', 'Tau_BPVLTFITCHI2', 'Tau_ENDVERTEX_CHI2', 'Tau_IP_OWNPV', 'Tau_IPCHI2_OWNPV', 'Tau_FD_OWNPV', 'Tau_FDCHI2_OWNPV', 'Tau_DIRA_OWNPV', 'Tau_P', 'Tau_PT', 'Tau_PE', 'Tau_PX', 'Tau_PY', 'Tau_PZ', 'Tau_TAU', 'Tau_TAUERR', 'Tau_TAUCHI2', 'Tau_DTF_CHI2', 'Tau_DTF_CHI2NDOF', 'Tau_DTF_PROB', 'Tau_ADOCA_12', 'Tau_BPVVDR', 'Tau_BPVVDZ']
    variables += ['Phi_BPVDIRA', 'Phi_BPVIPCHI2', 'Phi_BPVLTFITCHI2', 'Phi_ENDVERTEX_CHI2', 'Phi_IP_OWNPV', 'Phi_IPCHI2_OWNPV', 'Phi_FD_OWNPV', 'Phi_FDCHI2_OWNPV', 'Phi_DIRA_OWNPV', 'Phi_P', 'Phi_PT', 'Phi_PE', 'Phi_PX', 'Phi_PY', 'Phi_PZ', 'Phi_CosTheta', 'Phi_ADOCA_12']
    variables += ['KPlus_CosTheta', 'KPlus_P', 'KPlus_PT', 'KPlus_PE', 'KPlus_PZ', 'KPlus_TRCHI2DOF', 'KPlus_TRGHOSTPROB']
    variables += ['Mu_BPVIPCHI2', 'Mu_IP_OWNPV', 'Mu_IPCHI2_OWNPV', 'Mu_CosTheta', 'Mu_P', 'Mu_PT', 'Mu_PZ', 'Mu_PE', 'Mu_TRCHI2DOF', 'Mu_TRGHOSTPROB']
    variables += ['Tau_cp_0.50', 'Tau_cpt_0.50', 'Tau_cmult_0.50', 'Tau_cp_1.00', 'Tau_cpt_1.00', 'Tau_cmult_1.00']
    variables += ['Phi_cp_0.50', 'Phi_cpt_0.50', 'Phi_cmult_0.50', 'Phi_cp_1.00', 'Phi_cpt_1.00', 'Phi_cmult_1.00']
    variables += ['Mu_cp_0.50', 'Mu_cpt_0.50', 'Mu_cmult_0.50', 'Mu_cp_1.00', 'Mu_cpt_1.00', 'Mu_cmult_1.00']
    variables += ['KPlus_cp_0.50', 'KPlus_cpt_0.50', 'KPlus_cmult_0.50', 'KPlus_cp_1.00', 'KPlus_cpt_1.00', 'KPlus_cmult_1.00']
    variables += ['Tau_CTAU', 'Tau_CTAU_FITPV', 'Tau_CTAUERR_FITPV', 'Tau_CTAUSIGNIFICANCE_FITPV']

    variables = variables[:]
    
    region = {var: '' for var in variables}
    region['Tau_BPVDIRA'] = (0.9998, 1.)
    region['Tau_BPVLTFITCHI2'] = (0, 50)
    region['Tau_ENDVERTEX_COV_'] = (0, 4)
    region['Tau_IP_OWNPV'] = (0, 0.3)
    region['Tau_IPCHI2_OWNPV'] = (0, 50)
    region['Tau_FD_OWNPV'] = (0, 150)
    region['Tau_FDCHI2_OWNPV'] = (0, 2000)
    region['Tau_DIRA_OWNPV'] = (0.9998, 1)
    region['Tau_TAU'] = (0, 0.01)
    region['Tau_TAUERR'] = (0, 0.0005)
    region['Tau_TAUCHI2'] = (0, 50)
    region['Tau_DTF_CHI2'] = (0, 20)
    region['Tau_DTF_CHI2NDOF'] = (0, 6)
    region['Tau_ADOCA_12'] = (0, 2)
    region['Tau_BPVVDR'] = (0, 7)
    region['Tau_BPVVDZ'] = (0, 100)

    region['Phi_BPVDIRA'] = (0.9998, 1.)
    region['Phi_BPVIPCHI2'] = (0, 800)
    region['Phi_BPVLTFITCHI2'] = (0, 700)
    region['Phi_IP_OWNPV'] = (0, 50)
    region['Phi_IPCHI2_OWNPV'] = (0, 700) 
    region['Phi_FD_OWNPV'] = (0, 150)
    region['Phi_FDCHI2_OWNPV'] = (0, 2000)
    region['Phi_DIRA_OWNPV'] = (0.9998, 1)
    region['Phi_TAU'] = (0, 0.01)
    region['Phi_TAUERR'] = (0, 0.0005)
    region['Phi_TAUCHI2'] = (0, 100)
    region['Phi_ADOCA_12'] = (0, 0.3)

    region['Mu_IP_OWNPV'] = (0, 2)
    region['Mu_IPCHI2_OWNPV'] = (0, 700)

    region['Tau_cp_0.50'] = (0, 150000)
    region['Tau_cpt_0.50'] = (0, 15000)
    region['Tau_cmult_0.50'] = (0, 30)
    region['Tau_cp_1.00'] = (0, 300000)
    region['Tau_cpt_1.00'] = (0, 30000)
    region['Tau_cmult_1.00'] = (0, 50)

    region['Phi_cp_0.50'] = (0, 150000)
    region['Phi_cpt_0.50'] = (0, 15000)
    region['Phi_cmult_0.50'] = (0, 30)
    region['Phi_cp_1.00'] = (0, 300000)
    region['Phi_cpt_1.00'] = (0, 30000)
    region['Phi_cmult_1.00'] = (0, 50)

    region['Mu_cp_0.50'] = (0, 150000)
    region['Mu_cpt_0.50'] = (0, 15000)
    region['Mu_cmult_0.50'] = (0, 30)
    region['Mu_cp_1.00'] = (0, 300000)
    region['Mu_cpt_1.00'] = (0, 30000)
    region['Mu_cmult_1.00'] = (0, 50)

    region['KPlus_cp_0.50'] = (0, 150000)
    region['KPlus_cpt_0.50'] = (0, 15000)
    region['KPlus_cmult_0.50'] = (0, 30)
    region['KPlus_cp_1.00'] = (0, 300000)
    region['KPlus_cpt_1.00'] = (0, 30000)
    region['KPlus_cmult_1.00'] = (0, 50)

    region['Tau_CTAU'] = (0, 3)
    region['Tau_CTAU_FITPV'] = (0, 3)
    region['Tau_CTAUERR_FITPV'] = (0, 0.06)
    region['Tau_CTAUSIGNIFICANCE_FITPV'] = (0, 200)

        
    for var in variables:
        h_data = getHisto(dataTree, var, region[var])
        try: h_data.Scale(1./h_data.Integral())
        except ZeroDivisionError: pass
        h_MC = getHisto(MCTree, var, region[var])
        try: h_MC.Scale(1./h_MC.Integral())
        except ZeroDivisionError: pass
        c =  drawMultiPlot({'Signal':h_MC, 'Background':h_data}, title=var+';'+var+';A.U.', logy=False)
        
        c.Print(outFile_name)
        var = ''.join(var.split('.'))
        c.Print('plotsMVA/'+var+'.pdf')

    
    espressions = dict(Tau_sinDira = 'sqrt(1-Tau_DIRA_OWNPV*Tau_DIRA_OWNPV)',
                       Tau_thetaDira = 'TMath::ACos(Tau_DIRA_OWNPV)',
                       Tau_tanDira = 'sqrt(1-Tau_DIRA_OWNPV)/Tau_DIRA_OWNPV',
                       Mu_Theta = 'TMath::ACos(Mu_CosTheta)',
                       Phi_Theta = 'TMath::ACos(Phi_CosTheta)',
                       KPlus_Theta = 'TMath::ACos(KPlus_CosTheta)',
                       )
    region = {var: '' for var in espressions}
    region['Tau_sinDira'] = (0, 0.02)
    region['Tau_thetaDira'] = (0, 0.02)
    region['Tau_tanDira'] = (0, 0.02)

    for var, expr in espressions.items():
        h_data = getHisto(dataTree, var, region[var], expr = expr)
        try: h_data.Scale(1./h_data.Integral())
        except ZeroDivisionError: pass
        h_MC = getHisto(MCTree, var, region[var], expr = expr)
        try: h_MC.Scale(1./h_MC.Integral())
        except ZeroDivisionError: pass
        c =  drawMultiPlot({'Signal':h_MC, 'Background':h_data}, title=var+';'+var+';A.U.', logx=False, logy=False)
        
        c.Print(outFile_name)
        var = ''.join(var.split('.'))
        c.Print('plotsMVA/'+var+'.pdf')
    
    c.Print(outFile_name+']')
