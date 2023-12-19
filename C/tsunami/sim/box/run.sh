#!/bin/sh

dir=5M
mkdir $dir
cd $dir
slide.py -s $dir -R "0.0/0.0/4.0" -v 90 -p 90 -L 5 -W 0.240 -H 90 -k -n 200/200 -S 0.3 -r 90 -F "303.600/8089.600" -t 2 -D "302/307/8087/8095" -N
cd ..

dir=10M
mkdir $dir
cd $dir
slide.py -s $dir -R "0.0/0.0/4.0" -v 90 -p 90 -L 5 -W 0.3 -H 100 -k -n 200/200 -S 0.3 -r 90 -F "303.600/8089.600" -t 2 -D "302/307/8087/8095" -N
cd ..

dir=20M
mkdir $dir
cd $dir
slide.py -s $dir -R "0.0/0.0/4.0" -v 90 -p 90 -L 5 -W 0.3 -H 200 -k -n 200/200 -S 0.3 -r 90 -F "303.600/8089.600" -t 2 -D "302/307/8087/8095" -N
cd ..

