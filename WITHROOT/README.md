root -l -b -q main.C
DEBUG=1 root -l -q main.C - if we want to print

What is NANOAOD
https://indico.cern.ch/event/708041/papers/3276172/files/8621-nanoaod_acat19_v2.pdf

Each collision becomes one row in the tree ?

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

2.1

Typical branches/collections you may encounter include:

LHEPart*\*
LHEWeight*\*
LHEPdfWeight
LHEScaleWeight
LHE_HT
LHE_Njets

These describe things such as:

incoming partons
outgoing hard-process particles
matrix-element-level kinematics
PDF weights
renormalization/factorization scale variations
generator weights

The LHE stage is conceptually:

pp → hard process

For example, if you're producing:

pp → X X

2. GEN — generator-level event record

After the hard process, the event goes through the parton shower and hadronization.

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

You can use them to reconstruct the generator-level decay chain:

hard process
│
▼
heavy particle
│
├── decay product
│ │
│ └── ...
│
▼
parton shower
│
▼
hadronization
│
▼
stable particles

After the parton shower and hadronization, you have final-state particles.

These can be clustered into generator-level jets.

The corresponding branches are often:

GenJet_pt
GenJet_eta
GenJet_phi
GenJet_mass
GenJet_partonFlavour
GenJet_hadronFlavour

and possibly:

GenJetAK8\_\*

root h_nTau.root
TFile \*f = TFile::Open("h_nTau.root");
f->ls();
new TBrowser();
