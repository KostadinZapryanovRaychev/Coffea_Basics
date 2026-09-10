root -l -b -q main.C
DEBUG=1 root -l -q main.C - if we want to print

{
"inputFile": "../nanoaodsim_coffea_1.root"
}

What is NANOAOD
https://indico.cern.ch/event/708041/papers/3276172/files/8621-nanoaod_acat19_v2.pdf

how to do analysis

https://codimd.web.cern.ch/PMpenr-wQXGb49NavQSu1w?view

https://twiki.cern.ch/twiki/bin/viewauth/CMS/TauIDRecommendationForRun3
tau pdg recommendations

Article

https://journals.aps.org/prd/abstract/10.1103/PhysRevD.111.112004

Meaning of columns

https://cms-xpog.docs.cern.ch/autoDoc/NanoAODv12/2022/2023/doc_DYJetsToLL_M-50_TuneCP5_13p6TeV-madgraphMLM-pythia8_Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2.html

interesting to be checked

https://github.com/cms-tau-pog/TauIDSFs/blob/master/docs/TESunc.png

root h_nTau_selection.root
TFile \*f = TFile::Open("h_nTau_selection.root");
f->ls()
new TBrowser();

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

## Hadronically decayed tau selection

Used in `main.C` as `hadronicTauCuts["tauDecayedHadronically"]`.

| Variable      | Requirement         |
| ------------- | ------------------- |
| pT(τ)         | > 70 GeV            |
| \|η(τ)\|      | < 2.1               |
| \|dz(τ)\|     | < 0.2 cm            |
| DeepTau VSjet | ≥ 6 (Tight)         |
| DeepTau VSmu  | ≥ 4 (Tight)         |
| DeepTau VSe   | ≥ 5 (Medium)        |
| decayMode     | ∈ {0, 1, 2, 10, 11} |

### Why each cut is there

**pT(τ) > 70 GeV**
A trigger requirement, not a tau-physics one. The dedicated di-tau trigger
only reaches ~90% efficiency above 70 GeV (arXiv:2412.04357, Sec. 6.3), so
lower-pT candidates aren't reliably recorded in real data. It also rejects
much of the QCD-jet background, whose steeply falling spectrum piles up
near threshold.

**|η(τ)| < 2.1**
Keeps candidates inside the region where DeepTau's jet/e/μ rejection is
reliable. Tighter than HPS's raw |η| < 2.3 fiducial reach
(CMS-AN-2020-134, Table 56). pg 60

**|dz(τ)| < 0.2 cm**
Vertex association: requires the tau's leading track to originate close to
the event's primary vertex along the beam axis, rejecting taus
reconstructed from pileup (a separate, simultaneous pp collision).

**DeepTau VSjet ≥ 6 (Tight)**
The main purity driver. HPS builds a tau-shaped candidate out of any
1-or-3-track jet fragment; without this cut, the tau collection is
dominated by ordinary QCD jets misreconstructed as taus (jet→τ_h fake rate
~0.6% at this WP vs. ~60% genuine efficiency, per the paper).

**DeepTau VSmu ≥ 4 (Tight)**
Rejects real muons that a track plus a minimal calorimeter deposit can
fake as a 1-prong tau candidate.

**DeepTau VSe ≥ 5 (Medium)**
Rejects real electrons, whose ECAL shower plus a track can fake a
1-prong(+strip) tau candidate. Looser than VSjet/VSmu since electron fakes
are a smaller background here (CMS Sec. 5.2 specifies Medium for this WP
across channels).

**decayMode ∈ {0, 1, 2, 10, 11}**
Restricts to physically real topologies: 1-prong (0, 1, 2: π/K ± up to
2π⁰) and 3-prong (10, 11: 3π/K ± optional π⁰). Excludes modes 5/6
(2-prong), which the Tau POG documents as reconstruction failures rather
than real decays.

Cross-checked against: arXiv:2412.04357 / PRD 111, 112004 (Sec. 6.3),
CMS-AN-2020-134 (Tables 56/57), and the CMS Tau POG Run-3 ID
recommendations page.

### Does this "guarantee" a tau decayed hadronically?

No. It's a purity-maximizing selection, not a certainty:

- It only uses reconstructed detector quantities — the generator-level
  truth (`GenPart_pdgId`/`status`) isn't checked at all.
- Even at VSjet Tight, ~0.6% of real jets still fake a τ_h candidate.
  Given how much larger the QCD jet cross section is than the signal,
  that small fake rate can still be a real background — exactly why CMS
  builds a dedicated data-driven QCD estimate (the ABCD method) rather
  than relying on the cut alone.
- What it does deliver is high purity — a candidate passing all seven
  rows is very likely (order 90%+, depending on process and pT) a genuine
  hadronic tau, not a jet/electron/muon — good enough to build an
  analysis on, the same standard CMS itself uses.

  ​

  ​/Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD

  data_tier_name:"NANOAOD"
  modification_time:1741034371
  modified_by:"/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=cmsunified/CN=658085/CN=Robot: CMS Unified account"
  creation_date:1737132344
  dataset_id:15216132
  name:"/Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD"
  physics_group_name:"NoGroup"
  primary_dataset.name:"Tau"
  xtcrosssection:0
  primary_ds_name:"Tau"
  create_by:"WMAgent"
  dataset_access_type:"VALID"
  status:"VALID"
  acquisition_era_name:"Run2024C"
  last_modification_date:1741034371
  processed_ds_name:"Run2024C-2024CDEReprocessing-v1"
  prep_id:"ReReco-Run2024C-Tau-2024CDEReprocessing-00001"
  creation_time:1737132344
  created_by:"WMAgent"
  datatype:"data"
  primary_ds_type:"data"
  last_modified_by:"/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=cmsunified/CN=658085/CN=Robot: CMS Unified account"
  processing_version:1

Dataset: /Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD
Dataset size: 77820791067 (77.8GB) Number of blocks: 15 Number of events: 50839148 Number of files: 74 Dataset size: 7.7820791067e+10 (77.8GB) Creation time: 2025-01-17 16:45:44 Cross section: 0 Physics group: NoGroup Status: VALID Type: data
Release, Blocks, Files, Runs, Configs, Parents, Children, Sites, Origin sites, Physics Groups XSDB Sources: dbs3rucio hide
DAS service: dbs3 DAS api: filesummaries
median_cdate:1737309579
nfiles:74
num_lumi:24600
name:[]interface {}{"/Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD"}
size:77820791067
num_file:74
nblocks:15
nevents:50839148
median_ldate:1737309579
nlumis:24600
max_ldate:1738017634

DAS service: rucio DAS api: dataset4dataset
states:mongo.DASRecord{"T1_IT_CNAF_Tape":"AVAILABLE",
"T1_UK_RAL_Disk":"AVAILABLE",
"T1_US_FNAL_Disk":"AVAILABLE",
"T1_US_FNAL_Tape_Test":"AVAILABLE",
"T2_FR_GRIF":"AVAILABLE",
"T2_KR_KISTI":"AVAILABLE",
"T2_UA_KIPT":"AVAILABLE",
"T2_UK_London_IC":"AVAILABLE",
"T2_US_Caltech":"AVAILABLE"}
rses:mongo.DASRecord{"T1_IT_CNAF_Tape":[]interface {}{},
"T1_UK_RAL_Disk":[]interface {}{},
"T1_US_FNAL_Disk":[]interface {}{},
"T1_US_FNAL_Tape_Test":[]interface {}{},
"T2_FR_GRIF":[]interface {}{},
"T2_KR_KISTI":[]interface {}{},
"T2_UA_KIPT":[]interface {}{},
"T2_UK_London_IC":[]interface {}{},
"T2_US_Caltech":[]interface {}{}}
bytes:77820791067
available_bytes:77820791067
length:74
nblocks:15
available_length:74
size:77820791067
name:"/Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD"

DAS service: dbs3 DAS api: dataset_info
modification_time:1741034371
last_modified_by:"/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=cmsunified/CN=658085/CN=Robot: CMS Unified account"
processed_ds_name:"Run2024C-2024CDEReprocessing-v1"
name:"/Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD"
prep_id:"ReReco-Run2024C-Tau-2024CDEReprocessing-00001"
xtcrosssection:0
create_by:"WMAgent"
data_tier_name:"NANOAOD"
last_modification_date:1741034371
dataset_access_type:"VALID"
primary_ds_type:"data"
acquisition_era_name:"Run2024C"
processing_version:1
status:"VALID"
modified_by:"/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=cmsunified/CN=658085/CN=Robot: CMS Unified account"
created_by:"WMAgent"
physics_group_name:"NoGroup"
datatype:"data"
creation_time:1737132344
dataset_id:15216132
creation_date:1737132344
primary_ds_name:"Tau"
primary_dataset.name:"Tau"

DAS service: dbs3 DAS api: dataset_info
modified_by:"/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=cmsunified/CN=658085/CN=Robot: CMS Unified account"
data_tier_name:"NANOAOD"
dataset_access_type:"VALID"
status:"VALID"
create_by:"WMAgent"
processing_version:1
acquisition_era_name:"Run2024C"
xtcrosssection:0
creation_date:1737132344
primary_dataset.name:"Tau"
last_modified_by:"/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=cmsunified/CN=658085/CN=Robot: CMS Unified account"
last_modification_date:1741034371
primary_ds_name:"Tau"
created_by:"WMAgent"
datatype:"data"
processed_ds_name:"Run2024C-2024CDEReprocessing-v1"
dataset_id:15216132
name:"/Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD"
prep_id:"ReReco-Run2024C-Tau-2024CDEReprocessing-00001"
primary_ds_type:"data"
modification_time:1741034371
physics_group_name:"NoGroup"
creation_time:1737132344

DAS service: dbs3 DAS api: datasetlist
dataset_id:15216132
dataset_access_type:"VALID"
primary_ds_type:"data"
data_tier_name:"NANOAOD"
creation_date:1737132344
acquisition_era_name:"Run2024C"
physics_group_name:"NoGroup"
primary_ds_name:"Tau"
processing_version:1
last_modification_date:1741034371
prep_id:"ReReco-Run2024C-Tau-2024CDEReprocessing-00001"
xtcrosssection:0
last_modified_by:"/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=cmsunified/CN=658085/CN=Robot: CMS Unified account"
create_by:"WMAgent"
processed_ds_name:"Run2024C-2024CDEReprocessing-v1"
name:"/Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD"

dasgoclient -query="dataset=/Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD"
