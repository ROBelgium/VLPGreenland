#!/usr/bin/python3
import numpy as np
import os

#file with domain of C-grid (xlr,ylr,xur,yur,gridno for each line) 
corn = "../cornersC_v2"
#corn = "../corners_d63"

DEM  = "../../bathy_50m_neg.nc"
projkey="Karr"
os.chdir("ABC")
arr=np.loadtxt(corn)
print("corn",arr)
#print(range(0,len(arr),2))
buff=2000
mbuff=10
for i in [1]: #range(len(arr)):
    print("i",i,arr[i,:])
    xll,yll,xur,yur,no=int(arr[i,0]),int(arr[i,1]),int(arr[i,2]),int(arr[i,3]),int(arr[i,4])
    print("no,xll,yll,xur,yur",no,xll,yll,xur,yur)
    #add extra buffer to left to have better overlap between grids (except for western grid, 1)
    # if int(no)==1:
    #     yll-=200
    # if int(no)==2:
    #     yll-=200
    # # if int(no)==4:
    #     xur-=200
    #C-grid
    for r in [20,50,100]:
        outprev="C_d%(no)d_%(r)dm_geo" %vars()
        #RR="-R%(xll)f/%(xur)f/%(yll)f/%(yur)f -I%(r)d= " %vars()
        #cmd="gmt grdsample %(DEM)s %(RR)s -nl -G%(out)s_utm32.nc" %vars()
        cmd="gdal_translate -tr %(r)f %(r)f -projwin %(xll)f %(yur)f %(xur)f %(yll)f %(DEM)s %(outprev)s_utm_meter.nc" %vars()
        print("cmd",cmd)
        os.system(cmd)
        cmd="gdal_translate -tr %(r)f %(r)f -projwin %(xll)f %(yur)f %(xur)f %(yll)f %(DEM)s %(outprev)s_utm_meter.asc" %vars()
        print("cmd",cmd)
        os.system(cmd)
        for s in ["sm",""]:   
            out=outprev    
            if s=="sm":
                out+="_sm"
                cmd="gmt grdfilter -D0 -Fb50 %(outprev)s_utm_meter.nc -Gtmp.nc" %vars()
                print(cmd)
                os.system(cmd)
                os.system("format.py -f tmp.nc -s %(out)s_utm_meter.nc"%vars())
            #exit()
            #print("out",out,outprev)
            
            cmd="nc_gridadj3.py -f %(out)s_utm_meter.nc -s %(out)s.nc -x 0.001 -c %(projkey)s  -Z z" %vars()
            print("cmd",cmd)
            os.system(cmd)
            #exit()
            cmd="format.py -f %(out)s.nc -s %(out)s.most -X 360" %vars()
            if s!="sm":
                cmd="format.py -f %(out)s.nc -s %(out)s.most -i Band1 -X 360" %vars()
            print("cmd3",cmd)
            os.system(cmd) 
            print("sm",s)
            #exit()
    #B-grid
    r=100
    out="B_d%(no)d" %vars()
    # if int(no)==3:
    #     print("B:no==3")
    #     xll,yll,xur,yur=xll-buff,yll-mbuff,xur+buff,yur+buff
    # elif int(no)==1:
    #     print("B:no==1")
    #     xll,yll,xur,yur=xll-mbuff,yll-buff,xur+buff,yur+mbuff    
    # else:
    xll,yll,xur,yur=xll-buff,yll-buff,xur+buff,yur+buff
    cmd="gdal_translate -tr %(r)f %(r)f -projwin %(xll)f %(yur)f %(xur)f %(yll)f %(DEM)s %(out)s_utm32.nc" %vars()
    print("cmd",cmd)
    os.system(cmd)
    cmd="gmt grdfilter -D0 -Fb200 %(out)s_utm32.nc -Gtmp.nc" %vars()
    print("cmd",cmd)
    os.system(cmd) 
    os.system("format.py -f tmp.nc -s %(out)s_utm32_sm.nc"%vars())
    #cmd="nc_gridadj3.py -f %(out)s_utm32_sm.nc -s %(out)s_geo.nc -x 0.001 -c %(projkey)s  -Z z" %vars()
    cmd="nc_gridadj3.py -f %(out)s_utm32_sm.nc -s %(out)s_geo.nc -x 0.001 -c %(projkey)s  -Z z" %vars()
    print("cmd",cmd)
    os.system(cmd)

    cmd="format.py -f %(out)s_geo.nc -s %(out)s_geo.most  -X 360" %vars()
    print("cmd",cmd)
    os.system(cmd) 
    #A-grid
    r=200
    out="A_d%(no)d" %vars()
    # if int(no)==3:
    #     xll,yll,xur,yur=xll-buff,yll-mbuff,xur+buff,yur+buff
    #     print("A:no==3")
    # elif int(no)==1:
    #     print("A:no==1")
    #     xll,yll,xur,yur=xll-mbuff,yll-buff,xur+buff,yur+mbuff
    # else:
    xll,yll,xur,yur=xll-buff,yll-buff,xur+11500-buff,yur+3500-buff
    cmd="gdal_translate -tr %(r)f %(r)f -projwin %(xll)f %(yur)f %(xur)f %(yll)f %(DEM)s %(out)s_utm32.nc" %vars()
    print("cmd",cmd)
    os.system(cmd)
    cmd="gmt grdfilter -D0 -Fb200 %(out)s_utm32.nc -Gtmp.nc" %vars()
    print("cmd",cmd)
    os.system(cmd) 
    os.system("format.py -f tmp.nc -s %(out)s_utm32_sm.nc"%vars())
    cmd="nc_gridadj3.py -f %(out)s_utm32_sm.nc -s %(out)s_geo.nc -x 0.001 -c %(projkey)s  -Z z" %vars()
    print("cmd",cmd)
    os.system(cmd)
    cmd="format.py -f %(out)s_geo.nc -s %(out)s_geo.most -X 360" %vars()
    print("cmd",cmd)
    os.system(cmd) 

 