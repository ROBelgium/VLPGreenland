# Beamforming of the 2023-09-16 92s VLP event

This notebook (`beamforming.ipynb`) was used to estimate the location of the 2023-09-16 92s VLP event using cross-correlation beamforming, and produce figure S_beamforming and the movie S1.

We provide scripts to download (`download.py`) and pre-process (`prep.py`) the seismograms. For beamforming in a heterogeneous Earth (interpolated LITHO1 ([https://igppweb.ucsd.edu/~gabi/litho1.0.html](https://igppweb.ucsd.edu/~gabi/litho1.0.html)) model), run `fmm.py` and `fmm_merge.py` to get ray-traced traveltimes.

## Python requirements

- Python
- Scientific Python stack (numpy, matplotlib, ...)
- pytorch (for fast matrix operations)
- obspy (for loading, prepping, reading seismic data and handling time)
- pykonal (for ray-traced traveltimes)
- tqdm (for progressbars)
- cartopy (for maps)
- geokernels (for distances on Earth)
- cmcrameri (for colormaps)
