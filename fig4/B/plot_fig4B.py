import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import torch
from obspy import UTCDateTime
from obspy.geodetics import kilometers2degrees
from scipy.signal import iirfilter, sosfiltfilt, zpk2sos

# load data, waveforms are already sorted by distance
# a by-product of the beamforming code (see suppmat/Fig__/beamforming.ipynb)
data = torch.load("waveforms_24h.pt")
waveforms = data["waveforms"]
distances_to_reference = data["distances_to_reference"]
stations = data["station_names"]
coordinates = data["coordinates"]

print(waveforms.shape)

# filter in band 10mhz - 12mHz
fn = 0.5 * 0.1
low = 10e-3 / fn
high = 12e-3 / fn
z, p, k = iirfilter(4, [low, high], btype="band", ftype="butter", output="zpk")
sos = zpk2sos(z, p, k)
waveforms = torch.tensor(sosfiltfilt(sos, waveforms, axis=1).copy())
# taper to suppress filter artefact at edges
p = 0.1
taper_len = int(waveforms.shape[-1] * p)
hann_window = torch.hann_window(2 * taper_len)
taper = torch.ones(waveforms.shape[-1])
taper[:taper_len] = hann_window[:taper_len]
taper[-taper_len:] = hann_window[-taper_len:]

# prep for plot
# normalise each waveform
waveforms /= waveforms.max(dim=1, keepdim=True)[0]

# stack waveforms in 100km distance bins
distance_bins = np.arange(0, 20_000, 100)
bin_idx = np.digitize(distances_to_reference, distance_bins)
sampling_rate = 0.1

# within each bin shift to correct for 4.1 km/s
for bidx, b in enumerate(distance_bins):
    # get waveforms and distances corresponding to this bin
    waveforms_b = waveforms[bin_idx == bidx]
    # skip empty bins
    if len(waveforms_b) == 0:
        continue
    distances_b = distances_to_reference[bin_idx == bidx]
    # traveltimes from closest station to others
    tt = distances_b / 4.1
    tt -= tt.min()
    # shift waveforms
    freqs = torch.fft.fftfreq(waveforms_b.shape[-1], d=1 / sampling_rate)
    gfs = torch.exp(1j * 2 * np.pi * freqs * tt[:, None])
    shifted_spectra = torch.fft.fft(waveforms_b, dim=-1) * gfs
    waveforms_b = torch.fft.ifft(shifted_spectra, dim=-1).real
    # put back in waveforms
    waveforms[bin_idx == bidx] = waveforms_b

# stack shifted waveforms
waveforms = torch.stack(
    [waveforms[bin_idx == i].mean(dim=0) for i in range(len(distance_bins))]
)

# line with v=4.1 km/s slope
x = torch.linspace(0, 5400, 100)
y = 4.1 * x
y = kilometers2degrees(y)

# make selection based on beam SNR for cleaner plot
# compute SNR
expected_arrivals = distance_bins / 4.1 + 3600
# buffer to ignore filter artefacts
buffer = int(600 * sampling_rate)
window_for_snr_estimate = int(3600 * sampling_rate)
# need to do step by step, as traveltime changes
snr = torch.zeros(len(expected_arrivals))
for idx, expected_arrival in enumerate(expected_arrivals):
    noise = waveforms[
        idx,
        int(expected_arrival * sampling_rate)
        - window_for_snr_estimate : int(expected_arrival * sampling_rate),
    ].std()
    signal = waveforms[
        idx,
        int(expected_arrival * sampling_rate) : int(expected_arrival * sampling_rate)
        + window_for_snr_estimate,
    ].std()

    snr[idx] = signal / noise

snr_threshold = 3

# cut to time for plotting
start_idx = int(1200 * sampling_rate)
end_idx = int((3600 + 23 * 3600) * sampling_rate)
waveforms = waveforms[:, start_idx:end_idx]

# normalise again
waveforms /= waveforms.max(dim=1, keepdim=True)[0]

# prep time axis
# these times come from the beamforming code
starttime = UTCDateTime("2023-09-16T11:35:00.0Z")
endtime = UTCDateTime("2023-09-17T12:35:00.0Z")
time = np.arange(starttime, endtime, 1 / sampling_rate)
time_plt = np.array([UTCDateTime(t).datetime for t in time])
time_plt = time_plt[start_idx:end_idx]

# select based on SNR
waveforms = waveforms[snr > snr_threshold]

# scale
waveforms *= 2.5
# shift on y-axis
d = kilometers2degrees(distance_bins[snr > snr_threshold])
waveforms += d[:, None]
# plot

fig, ax = plt.subplots(figsize=(4, 2))
ax.plot(time_plt, waveforms.T, lw=0.4, c="k", alpha=0.5)
ax.set(
    ylabel="Distance to landslide (deg)",
    xlim=(
        UTCDateTime("2023-09-16T12:00:00.0Z").matplotlib_date,
        UTCDateTime("2023-09-16T14:30:00.0Z").matplotlib_date,
    ),
    ylim=(0, 180),
    yticks=(0, 60, 120, 180),
)


# format dates on x-axis
locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
formatter = mdates.ConciseDateFormatter(locator)
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter)

fig.savefig("fig4b.pdf", dpi=300, bbox_inches="tight")
