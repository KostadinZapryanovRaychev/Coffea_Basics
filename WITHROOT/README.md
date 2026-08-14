root -l -b -q main.C
DEBUG=1 root -l -q main.C - if we want to print

What is NANOAOD
https://indico.cern.ch/event/708041/papers/3276172/files/8621-nanoaod_acat19_v2.pdf

how to do analysis

https://codimd.web.cern.ch/PMpenr-wQXGb49NavQSu1w?view

Each column is called a branch ?

Event Tau_pt Tau_eta Muon_pt Jet_pt HLT_IsoMu24
0 ... ... ... ... ...
1 ... ... ... ... ...
2 ... ... ... ... ...

1782 branches ---> Columns X 60806 rows each

1. Task to try to print each branch for event 1 and to try to understand the meaning of it

rm -f /tmp/main*test /Users/macbookpro/Documents/BAN-Doctor-Degree/Tools/Coffea/WITHROOT/*\_column\_.txt

2.  LHE
    │
    │ hard scattering / matrix element
    ▼
    GEN / GenParticles
    │
    │ parton shower + hadronization
    ▼
    GEN particles / stable final-state particles
    │
    ▼
    SIM
    │
    │ detector simulation
    ▼
    DIGI
    │
    │ detector electronics response
    ▼
    RECO
    │
    │ reconstructed tracks, vertices, jets, electrons, muons, etc.
    ▼
    PAT / MiniAOD
    │
    ▼
    NanoAOD
    │
    ▼
    Analysis

The generator record is usually represented by collections/branches related to:

GenPart
GenJet
GenJetAK8
GenMET

Depending on the format and production, you may also see generator-level information associated with:

GenEventInfo
Generator
Pileup
GenPart\_\*

This is probably the most important one for what you're describing.

Typical branches:

GenPart_pt
GenPart_eta
GenPart_phi
GenPart_mass
GenPart_pdgId
GenPart_status
GenPart_statusFlags
GenPart_genPartIdxMother

Workflow
NanoAOD
↓
BranchReader
↓
Selector
↓
HistogramWriter
↓
ROOT histograms

root h_nTau_selection.root
TFile \*f = TFile::Open("h_nTau_selection.root");
f->ls()
new TBrowser();

for local usage

{
"inputFile": "../nanoaodsim_coffea_1.root"
}

--- The main hadronic tau decays

τ⁻ → π⁻ ντ

τ⁻ → K⁻ ντ

τ⁻ → π⁻ π⁰ ντ

τ⁻ → K⁻ π⁰ ντ

τ⁻ → π⁻ π⁰ π⁰ ντ

τ⁻ → K⁻ π⁰ π⁰ ντ

τ⁻ → π⁻ π⁺ π⁻ ντ

τ⁻ → K⁻ π⁺ π⁻ ντ

---

---- The main leptonic channels

τ− → e−νˉe​ντ​
τ− → μ−νˉμ​ντ​

---- The main semi leptonic channels

τ− →e−νˉe​ντ

τ− →μ−νˉμ​ντ​​

---

so we look for this channel the following channels

Z′ → τ+τ −→ (μ− (νˉμ) ​(ντ)​) (π+(ντ)​)

Z′ → τ+τ −→ (μ−νˉμ​ντ​) (K+ντ​)

Q Electric charge
B Baryon number
L Lepton number

Color charge (in strong interactions)

energy
momentum

The magnetic moment (\(\vec{\mu }\)) of a point-like Dirac particle is defined as

\_\_
mu = g( q/2m ) S

g- gyromagnetic momment
m - mass of particle
q - electric charge
s - sping ( for fermions 1/2)

magnetic moment of tau = -5.34 times 10^{-27} J/T.

electric dipole moment
dτ =1.5×10−17e cm. or e+ <---> e- this distance equals to 1.5 X 10 of power of -17 distance

Imaginary electric dipole moment it has again very small

τWEAK DIPOLE MOMENT (dwτ)τWEAK DIPOLE MOMENT (dwτ)τWEAK DIPOLE MOMEN ----- HADJIISKA TO EXPLAIN ME THIS !!!!

https://pdg.lbl.gov/2026/listings/contents_listings.html from here decays
Γ1 particle−≥0 neutrals≥0K0ντ(“1-prong”)(85.24±0.06 ) %
Γ2 particle−≥0 neutrals≥0K0Lντ(84.58±0.06 ) %
Γ3 μ− [a]νμ ντ (17.37±0.04 ) %
