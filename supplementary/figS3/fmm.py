from itertools import product
from pathlib import Path

import cartopy.crs as ccrs
import numpy as np
import pykonal
import pylab as plt
import torch
from geokernels.distance import geodist
from mpi4py import MPI
from obspy import Inventory, read_inventory
from scipy.interpolate import RegularGridInterpolator
from tqdm import tqdm

Path("fmm_out").mkdir(exist_ok=True)

# only mpi version, pykonal not parallelized by default and slow on dense grids
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    # LOAD STATION GEOMETRY
    print("loading metadata")
    p = Path("waveforms_prep")
    stations_prepped = [x.name.removesuffix(".mseed") for x in p.glob("*.mseed")]

    all_inv = read_inventory("stations/*")

    prepped_inv = Inventory()
    for sta in tqdm(sorted(stations_prepped)):
        prepped_inv += all_inv.select(
            network=f"{sta.split('.')[0]}",
            station=f"{sta.split('.')[1]}",
        )

    # extract array coordinates, and remember order of coordinates
    coordinates = []
    coordinates_stations = []
    for net in tqdm(prepped_inv):
        for sta in net:
            # skip duplicates
            if f"{net.code}.{sta.code}" in coordinates_stations:
                continue
            coordinates.append([sta.longitude, sta.latitude])
            coordinates_stations.append(f"{net.code}.{sta.code}")
    station_coordinates = torch.tensor(np.array(coordinates))

    # LOAD MODELS FOR INTERPOLATION
    print("loading models")
    models = {}
    # These velocity models are from the paper can be found at:
    # https://igppweb.ucsd.edu/~gabi/litho1.0.html
    modelfiles = ["./lith01_10mHz.txt", "./lith01_15mHz.txt"]
    lith01names = ["lith01_100s", "lith01_66s"]
    for modelfile, name in zip(modelfiles, lith01names):
        model = np.loadtxt(modelfile)

        coords_lon = model[:, 0]
        coords_lat = model[:, 1]
        abs_vel = model[:, 2]

        coords_lon = coords_lon.reshape(360, 180)
        coords_lat = coords_lat.reshape(360, 180)
        abs_vel = abs_vel.reshape(360, 180)

        coords_lon = coords_lon[:, 0]
        coords_lat = coords_lat[0, :]

        # convert from [0, 360] to [-180, 180]
        coords_lon -= 180
        coords_lon = np.hstack([coords_lon[:180], coords_lon[180:]])
        abs_vel = np.vstack([abs_vel[180:, :], abs_vel[:180, :]])

        coords_lat = coords_lat[::-1]
        abs_vel = abs_vel[:, ::-1]

        model_degree_spacing = 1

        coords = torch.tensor(list(product(coords_lon, coords_lat)))
        print(coords.shape)

        models[name] = [coords_lon, coords_lat, coords, abs_vel]

    # interpolate 66s and 100s model to 92s
    weightfactor = 8 / (100 - 66)

    interp_model = (1 - weightfactor) * models["lith01_100s"][
        -1
    ] + weightfactor * models["lith01_66s"][-1]
    models["lith01_92s_interp"] = [coords_lon, coords_lat, coords, interp_model]

    # pick model for fmm
    coords_lon, coords_lat, coords, abs_vel = models["lith01_92s_interp"]

    # z, lat, lon
    # translate spacing to pi numbers

    # translate to pykonal coords
    # coords = torch.tensor(coords)

    # prepare interpolation of traveltimes
    new_degree_spacing = 0.1
    new_coords_lon = torch.arange(-180, 180, new_degree_spacing)
    new_coords_lat = torch.arange(-90, 90 + new_degree_spacing, new_degree_spacing)
    new_gridpoints = torch.tensor(list(product(new_coords_lon, new_coords_lat)))
    xx_new, yy_new = np.meshgrid(new_coords_lon, new_coords_lat)
    print(new_gridpoints.shape)

    interp = RegularGridInterpolator(
        (coords_lon, coords_lat), abs_vel, bounds_error=False, fill_value=None
    )

    new_abs_vel = interp((xx_new, yy_new))
    print(new_abs_vel.shape)

    # beamforming run
    s_grid_lim_lon = -38, -14
    s_grid_lim_lat = 68.5, 77
    s_grid_spacing_lon = 0.1
    s_grid_spacing_lat = 0.1

    # source locations
    s_grid_coords_lon = torch.arange(
        s_grid_lim_lon[0],
        s_grid_lim_lon[1] + s_grid_spacing_lon,
        s_grid_spacing_lon,
    )
    s_grid_coords_lat = torch.arange(
        s_grid_lim_lat[0],
        s_grid_lim_lat[1] + s_grid_spacing_lat,
        s_grid_spacing_lat,
    )
    sources = torch.tensor(list(product(s_grid_coords_lat, s_grid_coords_lon)))
    # inv = read_inventory("stations/*")
    sources_split = [sources[i::size] for i in range(size)]
    indices_split = [list(range(i, sources.shape[0], size)) for i in range(size)]
    traveltimes_per_gridpoint_and_station = np.zeros(
        [sources.shape[0], station_coordinates.shape[0]]
    )
else:
    sources_split = None
    new_gridpoints = None
    new_coords_lon = None
    new_coords_lat = None
    new_degree_spacing = None
    new_abs_vel = None
    station_coordinates = None
    indices_split = None
    traveltimes_per_gridpoint_and_station = None

new_gridpoints = comm.bcast(new_gridpoints, root=0)
new_coords_lon = comm.bcast(new_coords_lon, root=0)
new_coords_lat = comm.bcast(new_coords_lat, root=0)
new_degree_spacing = comm.bcast(new_degree_spacing, root=0)
new_abs_vel = comm.bcast(new_abs_vel, root=0)
station_coordinates = comm.bcast(station_coordinates, root=0)
traveltimes_per_gridpoint_and_station = comm.bcast(
    traveltimes_per_gridpoint_and_station, root=0
)

indices = comm.scatter(indices_split, root=0)
sources = comm.scatter(sources_split, root=0)

# traveltimes_per_gridpoint_and_station = []
for source, s_index in tqdm(
    zip(sources, indices),
    disable=rank != 0,
    desc=f"rank {rank+1}/{size}",
    total=len(sources),
):
    # compute distances to all gridpoints
    source_d = source.flip(0).repeat(new_gridpoints.shape[0], 1)
    distances = geodist(new_gridpoints.flip(1), source_d, metric="km")

    # find closest gridpoint
    didx = np.argmin(distances)
    closest_lat, closest_lon = np.array(new_gridpoints[didx])
    lon_idx = np.argmin(abs(new_coords_lon - closest_lon))
    lat_idx = np.argmin(abs(new_coords_lat - closest_lat))

    # instantiate fmm
    solver = pykonal.EikonalSolver(coord_sys="spherical")
    solver.velocity.min_coords = 6371.0, 0, 0
    # new_new_intervals = new_degree_spacing * np.pi / 180
    intervals = new_degree_spacing * np.pi / 180
    solver.velocity.node_intervals = 1, intervals, intervals
    solver.velocity.npts = 1, new_coords_lat.shape[0], new_coords_lon.shape[0]
    solver.velocity.values = np.array([new_abs_vel])

    src_idx = (0, lat_idx, lon_idx)
    solver.traveltime.values[src_idx] = 0
    solver.unknown[src_idx] = False
    solver.trial.push(*src_idx)
    solver.solve()

    # And finally, get the traveltime values.
    out = solver.traveltime.values[0, :, :]

    interp = RegularGridInterpolator(
        (new_coords_lon, new_coords_lat), out.T, bounds_error=False, fill_value=None
    )

    traveltimes = interp(station_coordinates)
    traveltimes_per_gridpoint_and_station[s_index] = traveltimes

# save results temporarily, then merge with fmm_merge.py
np.save(f"fmm_out/traveltimes_{rank}.npy", traveltimes_per_gridpoint_and_station)
np.save(f"fmm_out/s_indices_{rank}.npy", indices)
