#!/usr/bin/env python

#from ROOT import TFile, TTree, RooRealVar, RooArgSet, RooDataSet
import ROOT as r

def makeRooDataset(inputFile_name):
    inputFile = r.TFile(inputFile_name)
    tree = inputFile.Get('DecayTreeTuple/DecayTree')

    vars = dict(
    Tau_M = (1600, 1950),
    Tau_DTF_Tau_M = (1600, 1950),
    Phi_M = (1008,1032),
    )

    rooVars = {}
    for var, spread in vars.items():
        rooVars[var] = r.RooRealVar(var, var, spread[0], spread[1])

    helpingVars = ['Mu_ProbNNmu', 'Mu_ProbNNpi']
    for var in helpingVars:
        rooVars[var] = r.RooRealVar(var, var, 0)
        rooVars[var].setConstant(False)

    def chunks(l, n):
        return [l[i:i+n] for i in range(0, len(l), n)]
    vars_slices = chunks(rooVars.values(), 6)
    dataArgSet = r.RooArgSet(*vars_slices[0])
    for var_slice in vars_slices[1:]:
        dataArgSet.add(r.RooArgSet(*var_slice))
        
    # Tau_M = RooRealVar('Tau_M', 'Tau_M', 1600, 1950)
    # Tau_DTF_Tau_M = RooRealVar('Tau_DTF_Tau_M', 'Tau_DTF_Tau_M', 1600, 1950)

    # Phi_M = RooRealVar('Phi_M', 'Phi_M', 1008,1032)
    # Tau_DTF_Phi_M = RooRealVar('Tau_DTF_Phi_M', 'Tau_DTF_Phi_M', 1008,1032)    
    #dataArgSet = RooArgSet(Tau_M, Tau_DTF_Tau_M, Phi_M, Tau_DTF_Phi_M)
    
    
    dataSet = r.RooDataSet("taus","taus RooDataSet", tree, dataArgSet)
    return dataSet
