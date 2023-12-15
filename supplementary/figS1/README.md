# Beamforming of the 2023-09-16 92s VLP event

This notebook (`beamforming.ipynb`) was used to estimate the location of the 2023-09-16 92s VLP event using cross-correlation beamforming, and produce figure S_beamforming and the movie S1.

We provide scripts to download (`download.py`) and pre-process (`prep.py`) the seismograms. For beamforming in a heterogeneous Earth (interpolated LITHO1 ([https://igppweb.ucsd.edu/~gabi/litho1.0.html](https://igppweb.ucsd.edu/~gabi/litho1.0.html)) model), run `fmm.py` and `fmm_merge.py` to get ray-traced traveltimes.

## Order of operations

`download.py`: download seismograms

`prep.py`: pre-process seismograms

`fmm.py`: compute ray-traced traveltimes, which are temporarily saved. This uses the model files `lith01_10mHz.txt` and `lith01_15mHz.txt` to estimate a 10.88mHz model.

`fmm_merge.py`: merge temporary saved traveltimes

`beamforming.ipynb`: beamforming notebook

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
- mpi4py (for parallel pre-processing and ray-tracing)
