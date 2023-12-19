#!/usr/bin/python

import os
os.system("ln -s /home/sylfest/projects/greenl_2023/grids/ ~/symlinks/greenl/ ")
os.system("ln -s /home/sylfest/projects/greenl_2023/sim/VC/ ~/symlinks/greenl/ ")
os.system("ln -s /home/sylfest/projects/greenl_2023/sim/box/ ~/symlinks/greenl/ ")


for mod in ["20M"]:
    save="gglo_box_%(mod)s_6hrs" %vars()
    dtopo="%(mod)s/%(mod)s" %vars()

    print("save %(save)s" %vars())
    cmd="""
    run_gglo.py \
    -d /home/sylfest/symlinks/greenl/grids/gglo/gglo_bathy_ella_50m.gphov \
    -r 0.5 \
    -q disp \
    -T 28800 \
    -t 10 \
    -s N \
    -g cart \
    -S %(save)s \
    -l /home/sylfest/symlinks/greenl/box/%(dtopo)s \
    -f 0.5/N/S/E/W \
    -L km \
    -E /home/sylfest/symlinks/greenl/grids/gglo/gauges_utm27_gglo.csv \
    -K \
    -Q Karr \
    """ %vars()
    print("cmd",cmd)
    os.system(cmd)
