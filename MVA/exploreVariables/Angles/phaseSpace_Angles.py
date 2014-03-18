#!/usr/bin/env python

import ROOT as r
from array import array
from math import cos
import sys
sys.path.append('/afs/cern.ch/user/g/gdujany/pyUtils')
from MultiPlot import MultiPlot

#(Momentum, Energy units are Gev/C, GeV)
mass_tau = 1.77682
mass_D = 1.86962
mass_Ds = 1.96849
mass_phi = 1.019455
mass_pi0 = 0.13498
mass_pip = 0.13957
mass_mu = 0.10566
mass_nu = 0
mass_rho = 0.77549
mass_a1 = 1.230
mass_K = 0.497648

inFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/tau2PhiMu_triggerNotApplied.root' # To take tau 4-vector

isGenCut = False

if isGenCut:
    histos_fileName = 'histos_phaseSpaceAngles_genCuts.root'
    outFile_name = 'plots_phaseSpaceAngles_genCuts.pdf'
    plotsDir = 'plotsAngles/phaseSpace_genCuts/'
else:
    histos_fileName = 'histos_phaseSpaceAngles.root'
    outFile_name = 'plots_phaseSpaceAngles.pdf'
    plotsDir = 'plotsAngles/phaseSpace/'


def makeHistos():
    histos = {}

    histos['Phi_CosTheta'] = r.TH1D('Phi_CosTheta', 'Phi_CosTheta;cos Helicity angle;A.U.', 100, -1., 1.)
    histos['KPlus_CosTheta'] = r.TH1D('KPlus_CosTheta', 'KPlus_CosTheta;cos Helicity angle;A.U.', 100, -1., 1.)
    histos['Mu_CosTheta'] = r.TH1D('Mu_CosTheta', 'Mu_CosTheta;cos Helicity angle;A.U.', 100, -1., 1.)
    histos['Tau_CosTheta'] = r.TH1D('Tau_CosTheta', 'Tau_CosTheta;cos Helicity angle;A.U.', 100, 0.85, 1.)
    histos['Phi_Theta'] = r.TH1D('Phi_Theta', 'Phi_Theta;Helicity angle;A.U.', 100, 0., 3.15)
    histos['KPlus_Theta'] = r.TH1D('KPlus_Theta', 'KPlus_Theta;Helicity angle;A.U.', 100, 0., 3.15)
    histos['Mu_Theta'] = r.TH1D('Mu_Theta', 'Mu_Theta;Helicity angle;A.U.', 100, 0., 3.15)
    histos['Tau_Theta'] = r.TH1D('Tau_Theta', 'Tau_Theta;Helicity angle;A.U.', 100, 0., 0.5)

    inFile = r.TFile(inFile_name)
    tree = inFile.Get('MCDecayTreeTuple/MCDecayTree')
    tree.SetBranchStatus("*",0)
    branches = ['{0}_{1}'.format(i,j) for i in ('Tau',) for j in ('TRUEP_E', 'TRUEP_X', 'TRUEP_Y', 'TRUEP_Z')]
    for var in branches:
        tree.SetBranchStatus(var,1)
        exec var+' = array("d",[0])'
        exec "tree.SetBranchAddress( '"+var+"', "+var+" )"
    evt = tree.__iter__()
    #evt.next()
    
    masses1 = [mass_phi, mass_mu]
    masses2 = [mass_K, mass_K]
    tau = r.TLorentzVector(0.0, 0.0, 0.0, mass_tau)
    tau.Boost(0.100914,-0.088738,0.987333)
    # event1 = r.TGenPhaseSpace()
    # event1.SetDecay(tau, len(masses1), array('d',masses1))

    nEvents = 1000000
    for cont in xrange(nEvents):
        if cont % 20000 == 0:
            print 'processing entrie ', cont, ' / ', nEvents,' : ', (cont*100)/nEvents,'%'
            
        evt.next()
        tau = r.TLorentzVector()
        tau.SetXYZT(Tau_TRUEP_X[0]/1000, Tau_TRUEP_Y[0]/1000, Tau_TRUEP_Z[0]/1000, Tau_TRUEP_E[0]/1000)
        event1 = r.TGenPhaseSpace()
        event1.SetDecay(tau, len(masses1), array('d',masses1))

        weight1 = event1.Generate()
        phi = event1.GetDecay(0)
        mu = event1.GetDecay(1)
        event2 = r.TGenPhaseSpace()
        event2.SetDecay(phi, len(masses2), array('d',masses2))
        weight2 = event2.Generate()
        Kp = event2.GetDecay(0)
        Km = event2.GetDecay(1)


        # compute angles       
        phi_SR_tau = phi.Clone()
        phi_SR_tau.Boost(-tau.BoostVector())

        mu_SR_tau = mu.Clone()
        mu_SR_tau.Boost(-tau.BoostVector())

        Kp_SR_phi = Kp.Clone()
        Kp_SR_phi.Boost(-phi.BoostVector())

        Km_SR_phi = Km.Clone()
        Km_SR_phi.Boost(-phi.BoostVector())

        beam = r.TVector3(0,0,1)

        def isGood(part):
            #if isGenCut: return True
            return  part.Pt()>0.25 and part.P()>2.5 and part.Theta()>0.005 and part.Theta()<0.4
       
        if (not isGenCut) or (isGood(mu) and isGood(Kp) and isGood(Km)):
            histos['Phi_CosTheta'].Fill(cos(tau.Vect().Angle(phi_SR_tau.Vect())), weight1*weight2)
            histos['KPlus_CosTheta'].Fill(cos(phi.Vect().Angle(Kp_SR_phi.Vect())), weight1*weight2)
            histos['Mu_CosTheta'].Fill(cos(tau.Vect().Angle(mu_SR_tau.Vect())), weight1*weight2)
            histos['Tau_CosTheta'].Fill(cos(beam.Angle(tau.Vect())))

            histos['Phi_Theta'].Fill(tau.Vect().Angle(phi_SR_tau.Vect()), weight1*weight2)
            histos['KPlus_Theta'].Fill(phi.Vect().Angle(Kp_SR_phi.Vect()), weight1*weight2)
            histos['Mu_Theta'].Fill(tau.Vect().Angle(mu_SR_tau.Vect()), weight1*weight2)
            histos['Tau_Theta'].Fill(beam.Angle(tau.Vect()))

        
        

    outFile = r.TFile(histos_fileName, 'RECREATE')
    for histo in histos.values():
        histo.Write()
    outFile.Close()


def makePlots():
    
    histoFile = r.TFile(histos_fileName)
    histos = {}
    for key in histoFile.GetListOfKeys():
        histos[key.GetName()] = histoFile.Get(key.GetName())

    for histo in histos.values():
            histo.Scale(1./(histo.GetBinWidth(1)*histo.Integral()))

    labels = dict(Mu_Theta = '#mu',
                  Phi_Theta = '#Phi',
                  KPlus_Theta='K^{+}',
                  Mu_CosTheta = '#mu',
                  Phi_CosTheta = '#Phi',
                  KPlus_CosTheta='K^{+}',
                  )

    c = r.TCanvas('c', 'c')
    c.Print(outFile_name+'[')

    hs = MultiPlot('hs', 'Theta;Theta;A.U.','h',
                   histos = {key:histos[key] for key in ['Mu_Theta', 'Phi_Theta', 'KPlus_Theta']},
                   labels=labels)
    hs.Draw()
    sin_funz = r.TF1('sin_funz', '0.5*TMath::Sin(x)', 0., 3.15)
    sin_funz.SetLineColor(r.kViolet-3)
    sin_funz.Draw('same')
    c.Print(outFile_name)
    c.Print(plotsDir+'Theta.pdf')

    hs = MultiPlot('hs', 'CosTheta;CosTheta;A.U.','h',
                   histos = {key:histos[key] for key in ['Mu_CosTheta', 'Phi_CosTheta', 'KPlus_CosTheta']},
                   labels=labels)
    hs.Draw()
    const_funz = r.TF1('sin_funz', '0.5', -1., 1.)
    const_funz.SetLineColor(r.kViolet-3)
    const_funz.Draw('same')
    c.Print(outFile_name)
    c.Print(plotsDir+'CosTheta.pdf')

    histos['Tau_Theta'].Draw()
    c.Print(outFile_name)

    histos['Tau_CosTheta'].Draw()
    c.Print(outFile_name)
    
    c.Print(outFile_name+']')

    print histos['Mu_CosTheta'].Integral()
    print histos['Mu_Theta'].Integral()


if __name__ == '__main__':

    r.gROOT.SetBatch()

    #makeHistos()
    makePlots()
