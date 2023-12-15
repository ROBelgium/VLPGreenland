import obspy
from obspy.clients.fdsn.mass_downloader import (
    GlobalDomain,
    MassDownloader,
    Restrictions,
)

restrictions = Restrictions(
    starttime=obspy.UTCDateTime(2023, 9, 16),
    endtime=obspy.UTCDateTime(2023, 9, 30),
    chunklength_in_sec=14 * 86400,
    network="*",
    station="*",
    channel_priorities=["VHZ", "LHZ"],
    location_priorities=["", "00", "10", "01", "11"],
    reject_channels_with_gaps=False,
    minimum_length=0.0,
    minimum_interstation_distance_in_m=100.0,
)

mdl = MassDownloader(
    providers=[
        "BGR",
        "EIDA",
        "ETH",
        "GEOFON",
        "GFZ",
        "INGV",
        "IPGP",
        "IRIS",
        "KNMI",
        "NCEDC",
        "NIEP",
        "NOA",
        "ODC",
        "ORFEUS",
        "RESIF",
        "SCEDC",
        "UIB-NORSAR",
        "USP",
        "https://earthquakescanada.nrcan.gc.ca",
    ]
)

mdl.download(
    GlobalDomain(),
    restrictions,
    mseed_storage="waveforms",
    stationxml_storage="stations",
)
