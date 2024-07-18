#!/bin/sh

proj=/home/sylfest/projects/greenl_2023/
for v in 20M #10M
do
    fol=box_$v
    run_MOST.py -P $proj/sim/gglo/gglo_$fol/proj_ \
        -A $proj/data/most/ABC/A_d2_geo.most \
        -B $proj/data/most/ABC/B_d2_geo.most \
        -C $proj/data/most/EllaOe/ella_5m_tide_0.7m_geo.most \
        -c sim \
        -d MOST_$fol\_ella_tide1.6m \
        -t 0.2 \
        -T 2000 \
        -o 40 \
        -i 4 \
        -j 2 \
        -s 1 \
        -r \
        -m 400 \
        -z 1 \
        -a 0.05
done

        