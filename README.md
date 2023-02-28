# pmacsBrainExtraction

Wrapper scripts to perform brain extraction on BIDS datasets using fast deep learning
tools like SynthStrip.

These scripts are designed to provide routine brain masking on a standing BIDS dataset.

Both [SynthStrip](https://surfer.nmr.mgh.harvard.edu/docs/synthstrip/) and
[HD-BET](https://github.com/MIC-DKFZ/HD-BET) are very easy to use. Run the containers
directly to see usage for individual input images.


## Citations

If using these masks in publications, please cite the appropriate papers:

Andrew Hoopes, Jocelyn S. Mora, Adrian V. Dalca, Bruce Fischl, Malte Hoffmann.
[SynthStrip: Skull-Stripping for Any Brain Image](https://pubmed.ncbi.nlm.nih.gov/35842095)
_NeuroImage_ 2022, 260:119474

Isensee F, Schell M, Pflueger I, Brugnara G, Bonekamp D, Neuberger U, Wick A, Schlemmer
HP, Heiland S, Wick W, Bendszus M, Maier-Hein KH, Kickingereder P.
[Automated brain extraction of multisequence MRI using artificial neural
networks](https://pubmed.ncbi.nlm.nih.gov/31403237)
_Hum Brain Mapping_ 2019, 40(17):4952-4964
