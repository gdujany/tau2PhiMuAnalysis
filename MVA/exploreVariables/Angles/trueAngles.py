#!/usr/bin/env python
import ROOT as r
from array import array
from math import cos
import sys
sys.path.append('/afs/cern.ch/user/g/gdujany/pyUtils')
from MultiPlot import MultiPlot


inFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/tau2PhiMu_triggerNotApplied.root'

histos_fileName = 'histos_trueAngles.root'
outFile_name = 'plots_trueAngles.pdf'

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
    branches = ['{0}_{1}'.format(i,j) for i in ('Tau', 'Phi', 'KPlus', 'KMinus', 'Mu') for j in ('TRUEP_E', 'TRUEP_X', 'TRUEP_Y', 'TRUEP_Z')]

    for var in branches:
        tree.SetBranchStatus(var,1)
        exec var+' = array("d",[0])'
        exec "tree.SetBranchAddress( '"+var+"', "+var+" )"

    # EVENT LOOP
    nEvents = tree.GetEntries()
    #nEvents = 100000 
    for cont, entrie in enumerate(tree):
        if cont == nEvents: break
        if cont % 20000 == 0:
            print 'processing entrie ', cont, ' / ', nEvents,' : ', (cont*100)/nEvents,'%'

        # TLorenzVectors
        tau = r.TLorentzVector()
        tau.SetXYZT(Tau_TRUEP_X[0], Tau_TRUEP_Y[0], Tau_TRUEP_Z[0], Tau_TRUEP_E[0])
        phi = r.TLorentzVector()
        phi.SetXYZT(Phi_TRUEP_X[0], Phi_TRUEP_Y[0], Phi_TRUEP_Z[0], Phi_TRUEP_E[0])
        mu = r.TLorentzVector()
        mu.SetXYZT(Mu_TRUEP_X[0], Mu_TRUEP_Y[0], Mu_TRUEP_Z[0], Mu_TRUEP_E[0])
        Kp = r.TLorentzVector()
        Kp.SetXYZT(KPlus_TRUEP_X[0], KPlus_TRUEP_Y[0], KPlus_TRUEP_Z[0], KPlus_TRUEP_E[0])
        Km = r.TLorentzVector()
        Km.SetXYZT(KMinus_TRUEP_X[0], KMinus_TRUEP_Y[0], KMinus_TRUEP_Z[0], KMinus_TRUEP_E[0])

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

        histos['Phi_CosTheta'].Fill(cos(tau.Vect().Angle(phi_SR_tau.Vect())))
        histos['KPlus_CosTheta'].Fill(cos(phi.Vect().Angle(Kp_SR_phi.Vect())))
        histos['Mu_CosTheta'].Fill(cos(tau.Vect().Angle(mu_SR_tau.Vect())))
        histos['Tau_CosTheta'].Fill(cos(beam.Angle(tau.Vect())))
        
        histos['Phi_Theta'].Fill(tau.Vect().Angle(phi_SR_tau.Vect()))
        histos['KPlus_Theta'].Fill(phi.Vect().Angle(Kp_SR_phi.Vect()))
        histos['Mu_Theta'].Fill(tau.Vect().Angle(mu_SR_tau.Vect()))
        histos['Tau_Theta'].Fill(beam.Angle(tau.Vect()))

    # END EVENT LOOP

    outFile = r.TFile(histos_fileName,'RECREATE')
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
    c.Print('plotsAngles/True/Theta.pdf')

    hs = MultiPlot('hs', 'CosTheta;CosTheta;A.U.','h',
                   histos = {key:histos[key] for key in ['Mu_CosTheta', 'Phi_CosTheta', 'KPlus_CosTheta']},
                   labels=labels)
    hs.Draw()
    const_funz = r.TF1('sin_funz', '0.5', -1., 1.)
    const_funz.SetLineColor(r.kViolet-3)
    const_funz.Draw('same')
    c.Print(outFile_name)
    c.Print('plotsAngles/True/CosTheta.pdf')

    histos['Tau_Theta'].Draw()
    c.Print(outFile_name)

    histos['Tau_CosTheta'].Draw()
    c.Print(outFile_name)

    c.Print(outFile_name+']')

   
             
if __name__ == '__main__':

    r.gROOT.SetBatch()
    
    #makeHistos()
    makePlots()
