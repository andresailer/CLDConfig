#!/usr/bin/env python3

import sys
from math import sqrt, sin, cos, tan, atan, acos, pi
from podio import root_io
from edm4hep import utils, LorentzVectorE

import ROOT


def main():
    files = sys.argv[1:]
    print(files)
    histosP, histosT = [], []
    for aFile in files:
      print("Reading file", aFile)
      particleType = aFile.split('.')[0].rsplit("_")[-2]
      basename = aFile.split('.')[0].rsplit("_")[1]  #  assuming 'rec_basename...'
      histoP, histoT = getHisto(aFile, f"{basename}_{particleType}")
      histosP.extend(histoP)
      histosT.extend(histoT)

      
    colors = [ROOT.kBlack, ROOT.kGreen+2, ROOT.kRed-7, ROOT.kCyan+1]
    c1 = ROOT.TCanvas("c1", "c1", 800, 600)
    first = True
    counter = -1
    for h in histosP:
        counter += 1
        h.SetLineColor(colors[counter%4])
        h.SetLineWidth(3)
        if first:
            h.Draw()
            first = False
        else:
            h.Draw("same")

    c1.GetPad(0).BuildLegend()
    c1.SaveAs("HistosP.png")

    first = True
    counter = -1
    for h in histosT:
        counter += 1
        h.SetLineColor(colors[counter%4])
        h.SetLineWidth(3)
        if first:
            h.Draw()
            first = False
        else:
            h.Draw("same")

    c1.GetPad(0).BuildLegend()
    c1.SaveAs("HistosT.png")

def getHisto(aFile, basename, maxEvents=10000, nBins=100, pMax=50, pGen=40.0):
    """Plot the momentum of the file of SiTracks_Refitted"""

    reader = root_io.Reader(aFile)
    isProd = "prod" in aFile

    axisTitles = ";(p_{Rec}-p_{Gen})/p_{Gen};Entries"
    hMom = ROOT.TH1D(f"{basename}_momentum", axisTitles, nBins, -2.0/pGen, 2.0/pGen)
    hMom.SetTitle(basename)

    axisTitles = ";#theta_{Rec} [deg];Entries"
    hTheta = ROOT.TH1D(f"{basename}_theta", axisTitles, nBins, -0.1, 0.1)
    hTheta.SetTitle(basename)

    axisTitles = ";p_{Rec};Entries"
    hMinus = ROOT.TH1D(f"prod_momentum_mu-", axisTitles, 200, 0.0, 100.0)
    hMinus.SetTitle("Prod mu-")
    hPlus = ROOT.TH1D(f"prod_momentum_mu+", axisTitles, 200, 0.0, 100.0)
    hPlus.SetTitle("Prod mu+")
    
    counter = 0
    for event in reader.get("events"):
        counter += 1
        if counter > maxEvents:
            break
        tracks = event.get("SiTracks_Refitted")
        if len(tracks) > 1 and not isProd:
            print("More than one track!", counter)
            continue
        theTS = None
        for track in tracks:
          for ts in track.getTrackStates():
            if ts.location == 1:
              theTS = ts
          if not theTS:
            print("No trackstate at IP found", counter)
            continue
          momentum, theta, charge = getMomentum(theTS, basename)
          if not momentum:
              continue
          if not isProd:
              hMom.Fill((momentum - pGen) / pGen)
              hTheta.Fill((theta * 180 / pi)-89.0)
          else:
            if charge > 0:
              hPlus.Fill(momentum)
            else:
              hMinus.Fill(momentum)

    if isProd:
      return [hPlus, hMinus], []
    return [hMom], [hTheta]


def getMomentum(theTS, basename):
    """Get the momentum from the trackState"""
    omega = theTS.omega
    tanlambda = theTS.tanLambda
    phi0 = theTS.phi
    theta = atan(1.0 / (tanlambda))

    bfield = 2.0
    charge = +1 if omega > 0 else -1
    if (charge == +1 and basename == "mu-") or (charge == -1 and basename == "mu+"):
        print("Error: The Charge is ", charge, "for", basename, counter)
        return None, None, charge

    factor = 3e-4  #
    momentum = factor * bfield / abs(omega) * sqrt(1 + tanlambda*tanlambda)

    # correct for the lorentz boost, pxp only
    pxp = momentum * cos(phi0) * sin(theta)
    py = momentum * sin(phi0) * sin(theta)
    pz = momentum * cos(theta)

    # now un boost
    angle = -0.015
    ta = tan(angle)
    ta2 = ta * ta
    gamma = sqrt(1.0 + ta2)
    betagamma = ta
    muMass = 0.1057 # GeV muon Mass
    # e2 =  pxp * pxp + py * py + pz * pz + 
    # px = betagamma * sqrt(e2) + gamma * pxp

    e = sqrt(pxp * pxp + py * py + pz * pz + muMass*muMass)
    px = pxp * gamma + e * betagamma

    # un boost theta
    theta = atan( sqrt((px*px + py*py)) / pz)
    theta = theta if theta > 0 else abs(theta)
    
    momentum = sqrt(px*px + py*py + pz*pz)
    return momentum, theta, charge
  
if __name__ == "__main__":
    main()
