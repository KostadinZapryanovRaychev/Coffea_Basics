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

masseless quark model ???

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

Z′ → τ+τ −→ (μ− (antiνμ) ​(ντ)​) (π+( anti ντ)​) checked

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

for electron channel from the manuel

Cut Barrel EndCap
H/E < 0.060 0.065
σiηiη < 0.011 0.031
|∆ηin| < 0.004 N/A
|∆φin| < 0.020 N/A
|1/E − 1/p| 0.013 0.013
ECAL PF Cluster Isolation < 0.160 0.120
HCAL PF Cluster Isolation < 0.120 0.120
Tracker Isolation < 0.08 0.08

Ht should be also examinated

The search is motivated by
B Meson anomalies

𝐵 → 𝐾+ 𝜈 𝜈¯

Flavour universality states that each flavour (or generation of leptons ), is equally likely to interact with a W boson.

The new ATLAS result is based on a study of its full dataset from the second run of the LHC, collected between 2015 and 2018. The analysis looked at over 100 million top-quark-pair collision events. The top quark decays promptly into a W boson and a bottom quark, so this sample provides 100 million pairs of W bosons. By counting the number of these events with two electrons (and no muon) or two muons (and no electron), physicists can test whether the W boson decays more often into an electron or a muon.

Z→e+e− Г=83.4093 MeV
Z→μ+μ− Г=83.4087 Me
Z→τ+τ− Г=83.2205 MeV

Z→e+e−,
Z→μ+μ−,
Z→τ+τ−,
Z→ννˉ,
Z→q+qˉ,

Γe​,Γμ​,Γτ​,Γν​,Γq​,…

ΓZ ​≃2.5 GeV = 2500 МеV
ГZtau/tau = 83 MeV

those are on tree level ( meaning from Quantum field theory we cound only first order processes without loop)

One of the decayse of B mesons are to D meson and tau and tau neutrino

B→Dτντ​

B→Deνe​

B→Dμνμ​​

We expecte each of this to be euqally distributted the

R(D)=Γ(B→Dτντ)/Γ(B→Dℓνℓ) we expect this for instance to be close to some number

SM predictions is due to LFU R(D)SM​≈0.294

but experimmentally we observe a value

R(D)exp ≈ 0.347
​

| Quantity                   | What it compares/measures                       |                  SM |         Experiment |
| -------------------------- | ----------------------------------------------- | ------------------: | -----------------: |
| (R(D))                     | (B\to D\tau\nu) vs (B\to D\ell\nu)              |     (0.299\pm0.004) |    (0.342\pm0.026) |
| (R(D^\*))                  | (B\to D^_\tau\nu) vs (B\to D^_\ell\nu)          |     (0.257\pm0.005) |    (0.287\pm0.012) |
| (R(J/\psi))                | (B_c\to J/\psi\tau\nu) vs (B_c\to J/\psi\mu\nu) |     (0.258\pm0.004) |      (0.52\pm0.20) |
| (BR(B^+\to K^+\nu\bar\nu)) | Fraction of (B^+) decays into (K^+\nu\bar\nu)   | (4.29\times10^{-6}) | (2.3\times10^{-5}) |

the B meson anomalies

predicts

R(D),R(D
∗
),R(J/ψ),BR(B→Kν
ν
ˉ
)

↓

experiments measure them

↓

some measurements have shown deviations

↓

physicists ask whether

SM+new interaction
​

fits everything better.

Candidate new interactions include:

Z
′
​

W
′
​

leptoquark
​

new scalars
​

Table 20: Electron ID Selections.
Cut Barrel EndCap
H/E < 0.060 0.065
σiηiη < 0.011 0.031
|∆ηin| < 0.004 N/A
|∆φin| < 0.020 N/A
|1/E − 1/p| 0.013 0.013
ECAL PF Cluster Isolation < 0.160 0.120
HCAL PF Cluster Isolation < 0.120 0.120
Tracker Isolation < 0.08 0.08

https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideMuonIdRun2

Table 21: µ Identification
Cut
recoMu.isGlobalMuon()
muon::isPFMuon()
recoMu.globalTrack()-> normalizedChi2()< 10
recoMu.globalTrack()-> hitPattern().numberOfValidMuonHits()> 0
recoMu.numberOfMatchedStations()> 1
fabs(recoMu.muonBestTrack()-> dxy(vertex-> position()))< 0.2
fabs(recoMu.muonBestTrack()-> dz(vertex-> position()))< 0.5
recoMu.innerTrack()-> hitPattern().numberOfValidPixelHits()> 0
recoMu.innerTrack()-> hitPattern().trackerLayersWithMeasurement()> 5

Table 22: Reconstructed Tau Decay Modes
HPS Tau Decay Modes
Single Charged Hadron + Zero Strip
Single Charged Hadron + One Strip
Single Charged Hadron + Two Strips
Two Charged Hadrons
Three Hadrons

Table 23: τh
ID criteria.
TauIDAlgorithm TauIdDeepTau2017v2p1
Isolation Tight
Prongs 1 or 3 hp
|η(τh
)| < 2.1
Discriminator against µ Tight (for all channels)
Discriminator against e loose (τhτh
), Medium (eτh and µτh
)

the following: ∆pT
(τ`/h
, τh
490 ),
cos[∆φ(τ`/h
, τh
)], mreco(τ`/h
, τh
), and cos{∆φ[pT
(τh
), E
miss
T
491 ]}.

N
signal
​

=N
observed
​

−N
background
​

    ​

So if you don't know the QCD background accurately, you can't reliably determine whether you have a signal.
