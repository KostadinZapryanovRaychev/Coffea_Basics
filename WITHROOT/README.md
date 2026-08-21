root -l -b -q main.C
DEBUG=1 root -l -q main.C - if we want to print

What is NANOAOD
https://indico.cern.ch/event/708041/papers/3276172/files/8621-nanoaod_acat19_v2.pdf

how to do analysis

https://codimd.web.cern.ch/PMpenr-wQXGb49NavQSu1w?view

Article

https://journals.aps.org/prd/abstract/10.1103/PhysRevD.111.112004

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

Muons are measured in the pseudorapidity range |𝜂| <2.4,
To suppress muons from hadron decays and other nonprompt sources, an additional requirement is imposed on the relative isolation, defined as the ratio of the energy from neutral and charged PF candidates in a cone of Δ⁢𝑅≡√(Δ⁢𝜂)2+(Δ⁢𝜙)2<0.4
Electrons are reconstructed using energy deposits in the ECAL detector that have a matching track in (𝜂,𝜙) space in the silicon tracking system, within |𝜂| <2.4. Electron candidates that fall in the transition region between the barrel and the end cap of the CMS detector, located at 1.44 <|𝜂| <1.57,
To identify electrons, we use the high-energy electron pairs (HEEP) ID for the selection of signal events;
Events are required to have one 𝜏h candidate accompanied by a 𝜇, 𝑒, or second 𝜏h candidate of opposite-sign (OS) charge, all within |𝜂| <2.1. To avoid possible overlaps among the three channels, we reject events containing additional lepton candidates of any flavor beyond the selected OS lepton candidate pair. Specifically, the additional lepton can be a 𝜇 or 𝑒 candidate with 𝑝T>10  GeV and |𝜂| <2.1
𝑍′ bosons through quark-antiquark annihilation, events from vector boson fusion are suppressed by vetoing events with a pair of jets 𝑗1,2, each of which passes 𝑝T >30  GeV and |𝜂| <4.7, with a pseudorapidity separation |Δ⁢𝜂⁡(𝑗1,𝑗2)|>4.2 and an invariant mass above 500 GeV.

A. The 𝜏𝜇⁢𝜏h SR
The 𝜏𝜇⁢𝜏h events are required to satisfy the single-muon trigger, whose efficiency exceeds 90% over the full 𝜂 range for the selected muon candidates with 𝑝T>35  GeV. Muons are also required to be well isolated and to pass the tight ID criteria defined in Ref. [38]. The 𝜏h candidate is required to satisfy 𝑝T >20  GeV. The two candidates are required to be well separated in (𝜂,𝜙) space by the criterion Δ⁢𝑅≡√(Δ⁢𝜙⁡(𝜏𝜇,𝜏h))2+(Δ⁢𝜂⁡(𝜏𝜇,𝜏h))2>0.3. We reject events containing 𝑏 jet candidates with 𝑝T>30  GeV and |𝜂| <2.4. Events from DY, 𝑊 +jets, and QCD multijet production are significantly suppressed by requiring the 𝜏𝜇 and 𝜏h candidates to have a large azimuthal separation given by cos⁡Δ⁢𝜙⁡(𝜏𝜇,𝜏h)<−0.98. In addition, we require that
→
𝑝
miss
T lie in the direction opposite that of the 𝜏h or of the 𝜏𝜇 candidate with the highest 𝑝T (leading lepton, ℓl), by requiring cos⁡Δ⁢𝜙⁡(𝑝miss
T,ℓl)<−0.95. This requirement further reduces the contribution of 𝑊 +jets and QCD multijet events. The transverse mass of the leading lepton and
→
𝑝
miss
T, 𝑚T⁡(𝑝miss
T,ℓl)=√𝑝miss
T⁡𝑝T⁡(ℓl)⁢(1−cos⁡(Δ⁢𝜙⁡(𝑝miss
T,ℓl))), is required to be greater than 150 GeV for further suppression of 𝑊 +jets events.

B. The 𝜏𝑒⁢𝜏h SR
Similar selection criteria are applied to the 𝜏𝑒⁢𝜏h channel, with the following differences. We require these events to satisfy a single-electron trigger that has an efficiency above 90% for electrons after the requirement 𝑝T >35⁢(55)  GeV for data collected in 2016 (2017–2018).

C. The 𝜏h⁢𝜏h SR
For the 𝜏h⁢𝜏h channel we select events that satisfy a dedicated trigger [29] with at least two 𝜏h candidates. We require each 𝜏h candidate to have 𝑝T>70  GeV, ensuring a trigger efficiency of at least 90%. The two 𝜏h candidates must be separated by Δ⁢𝑅 >0.3. Events with any 𝑏 jet candidate having 𝑝T>30  GeV and |𝜂| <2.4 are removed, to suppress top quark backgrounds. To reduce the contribution of DY events, the reconstructed mass of the 𝜏h pair is required to exceed 100 GeV. To discriminate against 𝑊 +jets and QCD multijet events, we require the two 𝜏h candidates to have a large azimuthal separation, cos⁡Δ⁢𝜙⁡(𝜏1
h,𝜏2
h)<−0.95, while the
→
𝑝
miss
T and the leading- 𝑝T 𝜏h candidate 𝜏l
h are required to satisfy |cos⁡Δ⁢𝜙⁡(𝑝miss
T,𝜏l
h)|>0.9. Further suppression of the contribution of QCD multijet events is achieved with a requirement 𝑝miss
T>30  GeV.

how much tau leptons in one event
distrubution it Pt
how much are hadronic decayed
how much are leptonic decayed
how much are muonic channel
how much electronic channel

in each event

one prong two prong to know more

stacked plots root or overlayed

LHC Run 3: DeepTau, PNet, and UParT the Algo used for rectostruntict tao leptons
