#!/usr/bin/env python

from __future__ import division
import pickle
from math import sqrt, log10, floor

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

