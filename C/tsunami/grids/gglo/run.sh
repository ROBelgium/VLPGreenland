#!/bin/sh -x 

gdal_translate /home/sylfest/NGI/P/2022/02/20220296/Calculations/greenland2023/grids/Raw_GloBouss_UTM27_Sverresborg.tif sverre.nc
gmt grdfilter sverre.nc -Gsverre_sm.nc -D0 -Fb1000
gmt grdsample sverre_sm.nc -I100 -Gsverre_100m_sm.nc
format.py -f sverre_100m_sm.nc -s gglo_bathy_sverre_100m.gphov -x 0.001 -y 0.001 -z -0.001

gdal_translate /home/sylfest/NGI/P/2022/02/20220296/Calculations/greenland2023/grids/Raw_GloBouss_UTM27_EllaO.tif ella.nc
gmt grdfilter ella.nc -Gella_sm.nc -D0 -Fb1000
gmt grdsample ella_sm.nc -I50 -Gella_50m_sm.nc
format.py -f ella_50m_sm.nc -s gglo_bathy_ella_50m.gphov -x 0.001 -y 0.001 -z -0.001

#rm -rf ella*nc sverre*nc
