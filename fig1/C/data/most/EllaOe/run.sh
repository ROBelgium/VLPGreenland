#!/bin/sh

for r in 2m 1m 
do
gmt grdsample ella_oe_base_area_utm27.nc -Rell$r\.nc -Gtmp.nc
gmt grdclip -Sb0/NAN tmp.nc -Gtmp2.nc
gmt grdmath tmp2.nc -1 MUL ell$r\.nc AND = ella_$r\_utm27.nc
done
