#!/usr/bin/env python

from __future__ import division
import pickle
import numpy as np
import ROOT as r

sigma = dict(
    tau2PhiMuFromPDs = 0.702,
    tau2PhiMuFromBDs = 0.0933,
    tau2PhiMuFromPD  = 0.041,
    tau2PhiMuFromBD  = 0.0019,
    tau2PhiMuFromB   = 0.162,
    )

eff_gen = dict(
    tau2PhiMuFromPDs = 0.63111,
    tau2PhiMuFromBDs = 0.10063,
    tau2PhiMuFromPD  = 0.65202,
    tau2PhiMuFromBD  = 0.07948,
    tau2PhiMuFromB   = 0.29691,
    )

eff_genCut = dict(
    tau2PhiMuFromPDs = 0.10293,
    tau2PhiMuFromBDs = 0.01567,
    tau2PhiMuFromPD  = 0.106425,
    tau2PhiMuFromBD  = 0.0121635,
    tau2PhiMuFromB   = 0.045795,
    )

# N_prod = dict(
#     tau2PhiMuFromPDs = 
#     tau2PhiMuFromBDs = 
#     tau2PhiMuFromPD  = 
#     tau2PhiMuFromBD  = 
#     tau2PhiMuFromB   = 
#     )

N_gen = {}
N_sel = {}
store_dir = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/'
ch_gen = 'MCDecayTreeTuple/MCDecayTree'
ch_sel = 'DecayTreeTuple/DecayTree'
for key in sigma:
    file_mu = r.TFile(store_dir+key+'_mu.root')
    file_md = r.TFile(store_dir+key+'_md.root')
    n_sel_mu = file_mu.Get(ch_sel).GetEntries()
    n_gen_mu = file_mu.Get(ch_gen).GetEntries()
    n_sel_md = file_md.Get(ch_sel).GetEntries()
    n_gen_md = file_md.Get(ch_gen).GetEntries()
    N_gen[key] = n_gen_mu + n_gen_md
    N_sel[key] = n_sel_mu + n_sel_md
    
    
eff_cut = {key: eff_genCut[key]/eff_gen[key] for key in eff_gen}

ss = sum([sigma[key]*eff_cut[key] for key in sigma])

f_gauss = {key: (sigma[key]*eff_cut[key])/ss for key in sigma}

r_rel = {key: f_gauss[key]/N_gen[key] for key in sigma}
r_max = max(r_rel.items(),key=lambda x: x[1])[1]
r_abs = {key: r_rel[key]/r_max for key in sigma}

print r_rel
print r_abs
