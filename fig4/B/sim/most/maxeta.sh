#!/usr/bin/sh

tide=1.6
#tide=0.7
nc_maxeta.py -f sim_runup_ha.nc -s maxeta_tide$tide\.nc
nc_gridadj3.py -f maxeta_tide$tide\.nc -s tmp222.nc -x 1000 -c Karr -r
gmt grdmath tmp222.nc $tide ADD = tmp333.nc
gmt grdclip -Sa999999/Nan tmp333.nc -Gmaxeta_tide$tide\_utm27_meter.nc
gdal_translate maxeta_tide$tide\_utm27_meter.nc maxeta_tide$tide\_utm27_meter.asc
