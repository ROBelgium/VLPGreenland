from pathlib import Path

import numpy as np
from obspy import UTCDateTime, read, read_inventory
from tqdm import tqdm

Path("waveforms_prep").mkdir(exist_ok=True)

# pre-processing can be slow, good to run in parallel.
# if mpi4py not installed/available, set to False
use_mpi = True
if use_mpi:
    # for 32 cores run with: mpirun -n 32 python prep.py
    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        inv = read_inventory("stations/*")
        inv_split = [inv[i::size] for i in range(size)]

    else:
        inv_split = None

    inv = comm.scatter(inv_split, root=0)
else:
    rank = 1
    size = 1
    inv = read_inventory("stations/*")

for net in tqdm(inv, disable=rank != 0, desc=f"rank {rank}/{size}"):
    for sta in net:
        if Path(f"waveforms_prep/{net.code}.{sta.code}.mseed").is_file():
            continue

        # read in seismograms
        try:
            st = read(f"waveforms/{net.code}.{sta.code}.*")
        except:
            print(f"can't read {net.code}.{sta.code}")
            continue

        # remove instrument resposne
        try:
            st.remove_response(inventory=inv)
        except:
            print(f"can't remove response {net.code}.{sta.code}")
            continue

        # merge to one trace
        try:
            st.merge(fill_value=0)
        except:
            print(f"can't merge {net.code}.{sta.code}")
            continue

        # force merged trace to fixed length
        st.trim(
            starttime=UTCDateTime("2023-09-16T00:00:00.0Z"),
            endtime=UTCDateTime("2023-09-30T00:00:00.0Z"),
            pad=True,
            fill_value=0,
        )

        # if large amounts of missing data, skip station
        if np.count_nonzero(st[0].data) < 0.9 * len(st[0].data):
            print(f"SKIP {net.code}.{sta.code}: too much data missing comp1")
            continue

        # if sampling rate is not 0.1 Hz, resample to 0.1
        tr = st[0]
        # most non-VHZ channels are LHZ (1Hz)
        if tr.stats.sampling_rate == 1:
            tr.decimate(10)
        # some channels are BHZ (usually 20Hz)
        if tr.stats.sampling_rate == 20:
            tr.decimate(10)
            tr.decimate(10)
            tr.decimate(2)
        # remaining cases
        if tr.stats.sampling_rate != 0.1:
            tr.resample(0.1)
        # after this, all channels are sampled at 0.1 Hz -> VHZ
        tr.stats.channel = "VHZ"

        tr.detrend("demean")
        tr.detrend("linear")

        tr.write(
            f"waveforms_prep/{net.code}.{sta.code}.mseed",
            format="MSEED",
        )
