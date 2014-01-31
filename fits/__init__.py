#!/usr/bin/env python

from ROOT import TFile, TTree, RooRealVar, RooArgSet, RooDataSet

def makeRooDataset(inputfile_name):
    chibTree_name = 'DecayTreeTuple/DecayTree'
    inputfile = TFile.Open(inputfile_name,"READ")
    tree = inputfile.Get('DecayTreeTuple/DecayTree')
        
    Tau_M = RooRealVar('Tau_M', 'Tau_M', 1600, 1950)
    Tau_DTF_Tau_M = RooRealVar('Tau_DTF_Tau_M', 'Tau_DTF_Tau_M', 1600, 1950)

    Phi_M = RooRealVar('Phi_M', 'Phi_M', 1008,1032)
    Tau_DTF_Phi_M = RooRealVar('Tau_DTF_Phi_M', 'Tau_DTF_Phi_M', 1008,1032)

    
    dataArgSet = RooArgSet(Tau_M, Tau_DTF_Tau_M, Phi_M, Tau_DTF_Phi_M)
    #dataArgSet.add(RooArgSet(chib_mass, chib_pt, chib_eta, chib_phi))
    
    dataSet = RooDataSet("taus","taus RooDataSet", tree, dataArgSet)
    return dataSet
