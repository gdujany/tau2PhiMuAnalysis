#!/usr/bin/python

from __future__ import division
import pickle
from math import sqrt, log10, floor
from ROOT import TFile, TTree, RooRealVar, RooArgSet, RooDataSet

def roundPair(val, err, sig=2):
    try:
        cfr = sig-int(floor(log10(err)))-1
    except ValueError:
        cfr = 2
    #return round(val, cfr), round(err, cfr)
    try:
        return ('{:.'+str(cfr)+'f}').format(val), ('{:.'+str(cfr)+'f}').format(err)
    except ValueError:
        if cfr > 0:
            return str(round(val, cfr)), str(round(err, cfr))
        else:
            return str(int(round(val, cfr))), str(int(round(err, cfr)))
    #     return ('{:.2f}').format(val), ('{:.2f}').format(err)

def roundList(ll, sig=1, cfr_fixed=None):
    cfr_list = sorted([sig-int(floor(log10(abs(err))))-1 for err in ll if err !=0.])
    cfr = cfr_list[-1]
    if cfr_fixed: cfr = cfr_fixed
    return [('{:.'+str(cfr)+'f}').format(val) for val in ll]

def roundDict(dd, sig=1, cfr_fixed=None):
    cfr_list = sorted([sig-int(floor(log10(abs(err))))-1 for err in dd.values() if err !=0.])
    cfr = cfr_list[-1]
    if cfr_fixed: cfr = cfr_fixed
    return dict([(key,('{:.'+str(cfr)+'f}').format(val)) for key,val in dd.items()])


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
