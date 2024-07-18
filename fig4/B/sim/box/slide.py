#!/usr/bin/python

import math,numpy,os,sys,getopt,string
from sct.io import io
from sct.Grid1D import Grid1D as G

d=io(quiet=1)
"""
Change log:

2021-09-20  SGL Added option for giving inital position of front of slide (-F and -f)

"""


def help():
    print """
This script computes source-sink files for slide generated waves. The output is by now \"joined-gphov\" with a file with the times for the output fields, the tt3 format for Geoclaw and the XYT-format for COMCOT.

The files are generated on a cartesian grid (scale km, height and velocity given in m and m/s, respectively). The files can be projected into geographical coordinates by giving the utm-zone and the location of the origo of the cartesian grid in geographical coordinates. This require GMT to be installed on your system.

Useage: slide.py [options]

[-s|--stem    <value>] stem for output files: stemF and stem.tim
                       [def. \"slide\"]
[-d|--slide]           use this flag to output the thickness of the slide
                       instead of source-sink. [def. source-sink]

Slide progression:
[-R|--R       <value>] where <value> is three numbers defining the length of
                       acceleration phase, length of constant velocity, and
                       decelleration phase, given in km and on this form:
                       Ra/Rc/Rd, e.g. 3/5/1. (km/km/km) [def. 0/1/5]
[-v|--maxvel  <value>] maximum velocity of slide (m/s)  [def. 30]
[-V|--velprog  <file>] a two-column file (sec and km) with time and
                       position for describing the slide progression
                       (replaces the combination of input -R and -v) 
[-p|--pangle  <value>] direction of slide path (linear), (degrees) [def. 0]
[-X|--maxR    <value>] setting the maximal run-out. If reached this distance
                       the slide stop moving.
[-q|--posprog <file>]  a three column file with position of slidepaht in
                       first two and the accumulated distance in third.

Shape of slide:
[-L|--length  <value>] length of slide (km)         [def. 1]
[-W|--width   <value>] width of slide  (km)         [def.0.5]
[-H|--height  <value>] height of slide (meters!)    [def. 100]
[-S|--smooth  <value>] factor for smoothing (typically S=0.5*L in skredp)
                       [def. 0.5]
[-r|--rot     <value>] rotation of slide (degrees) [def. 0]
[-c|--circular]        flag for indicating that the slide is circular
                       with height H and total widt W


Other options:
[-o|--local   <value>] center of slide on the cartesian grid (km) [def. 0/0]
[-O|--global  <value>] center of initial slide in geographical coord. If
                       this option is omitted and utmzone is given, the local
                       coord. are projected into geographical coord. using
                       the utmzone [def. 0/0]. Can't be used with -F/-f option 
                       inital location of front of slide
[-u|--utmzone <value>] giving the utmzone here, e.g. 18Q (see
                       http://www.dmap.co.uk/utmworld.htm). This option
                       is also a flag for projecting the files into
                       geographical coordinates [def. none]
[-F|--front   <x/y>]   coordinates of front of slide
[-f|--frontadd <value>] adjust the front of slide (adding the value along the
                       direction of the slide). Positive value -> longer 
                       into the water, negative value -> longer up in the slope. 
                       Can only be used in combination with option -F.
[-t|--dt      <value>] resolution in time (s) [def. 20]
[-D|--domain  <value>] for specifying the cartesian domain, e.g. 0/1/0/3
                       (km/km/km/km) xstart/xend/ystart/yend
                       [def. -10/10/-10/10]
[-n|--nodes   <value>] number of nodes in x and y directon, initeger,
                       [def. 100/100]
[-m|--mtv]             flag for writing out mtv files for each time-level,
                       filenames: slide\%04d.mtv [def. do not write out)
[-N|--netcdf]          flag for writing out netcdf files for each time-level,
                       filenames: slide\%04d.nc [def. do not write out)
[-k|--km]              flag for giving the (output ) depth of slide in km
                       (not meters) and the sink/source distribution in km/s
                       (not m/s).
[-T|--tstop   <value>] set manually tstop
[-C|--comcot  <name>]  will produce the XYT-format for COMCOT instead of
                       the GGLO -format (joined gphov). The <name> is the
                       filename for the XYT-data
[-G|--geoclaw <name>]  Geoclaw tt3 format
"""

#start of program:

#default values
NC = -12
#parameters for slide
Ra = 0      #distance in km of acceleration 
Rc = 1      #distance in km of constant velocity
Rd = 5      #distance in km of decceleration
L  = 1      #length of slide (km)
W  = 0.5      #width of slide  (km)
dH = 100    #height of slide (m)
S  = 0.5    #length of smoothing (km)
vmax      = 0.03  #km/s
rotation  = 0 #rotation of slide
pathangle = 0 #direction of slidepath
frontx  = False    #giving the location of the front of the slide 
fronty  = False
frontadd  = 0        #adjusting the location of the front (fine tuning)

xc        = False #location of center of slide (local grid, km)
yc        = False #location of center of slide (local grid, km)
distp     = 0 #location of slide (along path) at prev. timestep
gdx       = 1 #degrees pr. km
gdy       = 1 #degrees pr. km

project   = False #project data into geographical coord or apply kilometers
utmsone   = "18Q" #give utm zone
xgc       = 0     #global position in geographical coordinates
ygc       = 0     #global position in geographical coordinates
srcsink   = True
dt        = 20   #length of dt in seconds
fnprogr   = False #time/position of slide
progt     = False # time -"-
progx     = False # position -"-
tstop_man = 0     # manually set tstop
tottime   = 0
maxR      = False # stop slide motion if reached this distance
circular  = False # circular slide with height H and width W
posprog   = False # twocolumn file with position of slidepath

#number of gridpoints in output:
nx        = 100
ny        = 100
comcot    = False
geoclaw   = False

#domain
xs  = -10
xe  = 10
ys  = -10
ye  = 10


km  = False
mtv = False
nc  = False

##########################################################
# improvements not yet implemented:
#
# trackslide                          ====>>>> OK 20052014
# ...pathangle is not changed (same orientation of slide)
#
# q or bottomdeformation              ====>>>> OK 29012009
# curved path
# calculate the volume                ====>>>> OK 29012009
# arbitrary slide progression         ====>>>> OK 29012009
# possibility to set manually tstop
# 
#
##########################################################


#READ INPUT

try:
    tmp=sys.argv[1]
except:
    help()
    sys.exit()
#stem of output:
fname="slide"

#d=io()
#d.log()
#read input
options,args=getopt.getopt\
              (sys.argv[1:],'hR:L:W:H:S:v:r:p:o:O:u:t:D:n:s:mdkV:T:X:C:Nq:cG:F:f:',\
               ['help','R=','length=','width=','height=','smooth=','maxvel=','rot=','pangle=','local=','global=','utmzone=','dt=','domain=','nodes=','stem=','mtv','slide','km','velprog=','tstop=','maxR=','comcot=','netcdf','posprog=','circular','geolaw=','front=','frontadd='])
for option,value in options:
    if option in ('-h','--help'):
        help()
        sys.exit(0)
    elif option in ('-R','--R'):
        inp=value.split("/")
        Ra=float(inp[0])
        Rc=float(inp[1])
        Rd=float(inp[2])
        print "R",Ra,Rc,Rd
    elif option in ('-L','--length'):
        L=float(value)
    elif option in ('-W','--width'):
        W=float(value)
    elif option in ('-H','--height'):
        dH=float(value)
    elif option in ('-S','--smooth'):
        S=float(value)
    elif option in ('-v','--maxvel'):
        vmax=0.001*float(value) #input is m/s, script apply km/s
    elif option in ('-r','--rot'):
        rotation=float(value)
    elif option in ('-p','--pangle'):
        pathangle=float(value)
    elif option in ('-o','--local'):
        inp=value.split("/")
        xc=float(inp[0])
        yc=float(inp[1])
    elif option in ('-O','--global'):
        inp=value.split("/")
        xgc=float(inp[0])
        ygc=float(inp[1])
    elif option in ('-u','--utmzone'):
        utmsone=str(value)
        project=True
    elif option in ('-t','--dt'):
        dt=float(value)
    elif option in ('-D','--domain'):
        inp=value.split("/")
        xs=float(inp[0])
        xe=float(inp[1])
        ys=float(inp[2])
        ye=float(inp[3])
    elif option in ('-n','--nodes'):
        inp=value.split("/")
        nx=int(inp[0])
        ny=int(inp[1])
    elif option in ('-F','--front'):
        inp=value.split("/")
        frontx=float(inp[0])
        fronty=float(inp[1])
    elif option in ('-f','--frontadd'):
        frontadd=float(value)
    elif option in ('-s','--stem'):
        fname=str(value)
    elif option in ('-m','--mtv'):
        mtv=True
    elif option in ('-N','--netcdf'):
        nc=True
    elif option in ('-d','--slide'):
        srcsink=False
    elif option in ('-k','--km'):
        km=True
    elif option in ('-T','--tstop'):
        tstop_man=float(value)
    elif option in ('-X','--maxR'):
        maxR=float(value)
    elif option in ('-V','--velprog'):
        fnprogr=str(value)
        [progt,progx]=d.read(value)
        prog=G(progt,progx)
        tottime=prog.x[-1]
    elif option in ('-C','--comcot'):
        comcotfile=str(value)
        comcot=True
    elif option in ('-G','--geoclaw'):
        geoclawfile=str(value)
        geoclaw=True
        print "geoclaw...",geoclawfile
    elif option in ('-q','--posprog'):
        file=str(value)
        pp=numpy.loadtxt(file,unpack=True)
        posprogdist=G(pp[2],pp[1])
        posprogx=G(pp[1],pp[0])
        posprog=True
    elif option in ('-c','--circular'):
        circular=True

       
#total time:

if tottime==0:
    Ta=math.pi*Ra/(2*vmax)
    Tc=Rc/vmax
    Td=math.pi*Rd/(2*vmax)
    tottime=Ta+Tc+Td
    print 30*"#"
    print tottime
#if 0<tstop_man<tottime:
if 0<tstop_man:
    tottime=tstop_man

#calculate number of time-levels:
nt=int(1.2*tottime/dt)
print 30*"#"
print "timelevels",nt
#---------------------------------------------------------------------


angle=rotation*math.pi/180.0
pangle=pathangle*math.pi/180.0
print "pangle",pangle,pathangle

dx=float(xe-xs)/(float(nx)-1)
dy=float(ye-ys)/(float(ny)-1)

X=numpy.zeros([nx,ny],float)
Y=numpy.zeros([nx,ny],float)
Z=numpy.zeros([nx,ny],float)
Zall=numpy.zeros([nx,ny,nt],float)

tmp=numpy.zeros([nx,ny],float)

#find the center of slide if front location is given:
if xgc and frontx:
    print "You can't combine option -O and -F, choose one of them and use -F and -u if you want to both define the location of the front of the slide and projecting the data into degrees"
    sys.exit()


#find center of slide if position of front is given
if frontx:
    xc=frontx-((L+S)/2)*math.cos(pangle)
    yc=fronty-((L+S)/2)*math.sin(pangle)
    print "frontx",frontx, fronty,xc, yc
    if frontadd:
        xc+=frontadd*math.cos(pangle)
        yc+=frontadd*math.sin(pangle)
#---------------------------------------------------------------------
#projection of data --------------------------------------------------
#---------------------------------------------------------------------
xc0=xc
yc0=yc
projcentr=False
if project:
    #GMT must be installed on the computer
    if xgc==0 and ygc==0:
        #xc,yc is in utm-coordinates, calculate geogrphical coord
        tmpx=xc*1000 #meters
        tmpy=yc*1000 #meters
        projcentr=True
        cmd=""" echo %(tmpx)f %(tmpy)f |
        gmt mapproject  -C -F -I -Ju%(utmsone)s/1:1 """ % vars()
        #cmd=""" echo %(tmpx)f %(tmpy)f |
        #mapproject  -C -F -I -R0/360/-90/90 -Ju%(utmsone)s/1:1 """ % vars()
        [xgc,ygc]=os.popen(cmd).readline().strip().split()
        print "projected origo:",xgc,ygc
    print "\nutmsone",utmsone
    utmsone=str(utmsone)
    xgc=float(xgc)
    ygc=float(ygc)
    cmd=""" echo %(xgc)f %(ygc)f |
    gmt mapproject  -C -F -Ju%(utmsone)s/1:1 """ % vars()
    [xcutm,ycutm]=os.popen(cmd).readline().strip().split()

    tmpx=float(xcutm)+1000
    tmpy=float(ycutm)
    cmd=""" echo %(tmpx)f %(tmpy)f |
    gmt mapproject  -C -F -I  -Ju%(utmsone)s/1:1 """ % vars()
    [xg_e,t]=os.popen(cmd).readline().strip().split()
    
    tmpx=float(xcutm)
    tmpy=float(ycutm)+1000
    cmd=""" echo %(tmpx)f %(tmpy)f |
    gmt mapproject  -C -F -I  -Ju%(utmsone)s/1:1 """ % vars()
    [t,yg_e]=os.popen(cmd).readline().strip().split()

    #degrees per km:
    gdx=float(xg_e)-xgc
    gdy=float(yg_e)-ygc
    
    print "degrees per km, lon/lat: %.6f/%.6f" %(gdx,gdy)

else:
    xc0=0
    yc0=0
#---------------------------------------------------------------------

xypos=open(fname+".xypos","w")

#---------------------------------------------------------------------

#functions:


## def slideDepth (x,y,xc,yc):
##     #depth in km (depending on input parameters also)
##     xn=x-xc
##     yn=0
    
##     xn*=math.cos(angle)
##     xn+=(y-yc)*math.sin(angle)
##     yn=-(x-xc)*math.sin(angle)+(y-yc)*math.cos(angle)
##     if (-(0.5*L+S)<xn and xn<-0.5*L):
##         val=dH*math.exp(-math.pow(2*(xn+0.5*L)/S,4.0)-(math.pow(2*yn/W,4.0)))
##         return val
##     elif (-0.5*L<=xn and xn<0.5*L):
##         val=dH*math.exp(-(math.pow(2*yn/W,4.0)))
##         return val
##     elif (0.5*L<=xn and xn<0.5*L+S):
##         val=dH*math.exp(-math.pow(2*(-xn+0.5*L)/S,4.0)-(math.pow(2*yn/W,4.0)))
##         return val      
##     else:
##         return 0

def slideDepth (x,y,xc,yc):
    #depth in km (depending on input parameters also)

    dist=math.pow((math.pow((x-xc),2.0)+math.pow((y-yc),2.0)),0.5)
    #print dist

    if circular:
        if (dist<W):
            val=dH*math.exp(-(math.pow(2*dist/W,4.0)))
            return val
        else:
            return 0
    else:
        #depth in km (depending on input parameters also)
        xn=x-xc
        yn=0
        
        xn*=math.cos(angle)
        xn+=(y-yc)*math.sin(angle)
        yn=-(x-xc)*math.sin(angle)+(y-yc)*math.cos(angle)
        if (-(0.5*L+S)<xn and xn<-0.5*L):
            val=dH*math.exp(-math.pow(2*(xn+0.5*L)/S,4.0)-(math.pow(2*yn/W,4.0)))
            return val
        elif (-0.5*L<=xn and xn<0.5*L):
            val=dH*math.exp(-(math.pow(2*yn/W,4.0)))
            return val
        elif (0.5*L<=xn and xn<0.5*L+S):
            val=dH*math.exp(-math.pow(2*(-xn+0.5*L)/S,4.0)-(math.pow(2*yn/W,4.0)))
            return val      
        else:
            return 0



def findRunoutDist (t):
    #global tottime
    s=0
    if fnprogr:
        #READ VELOCITY PROGRESSION FROM FILE
        res=prog.interp_lin([t])
        s=res[1][0]
    else: 
        #USING SINUSODIAL PROGRESSION (ALA SKREDP)
        #find the propagation distance for slide during time dt:

        Ta=math.pi*Ra/(2*vmax)
        Tc=Rc/vmax
        Td=math.pi*Rd/(2*vmax)
        
        tottime=Ta+Tc+Td
        if (t<0):
            s=0
        elif (t>=0 and t<Ta):
            s=Ra*(1-math.cos(vmax*t/Ra))
        elif (t>=Ta and t<Tc+Ta):
            s=Ra+vmax*(t-Ta)
        elif (t>=Tc+Ta and t<Ta+Tc+Td):
            s=Ra+Rc+Rd*math.sin((vmax/Rd)*(t-Ta-Tc))
        else:
            s=Ra+Rc+Rd

    if maxR and s>maxR:
        s=maxR
    return s

def compute_pos_slide(dist):
    if posprog:
        res=posprogdist.interp_lin([dist])
        ypos=res[1][0]
        res=posprogx.interp_lin([ypos])
        xpos=res[1][0]
        
        dx=xpos-xc
        dy=ypos-yc
        
    else:
        dx=(dist-distp)*math.cos(pangle)
        dy=(dist-distp)*math.sin(pangle)
    return dx,dy


def compute_slide(time):
    global xc,yc,distp,xypos
    dist=findRunoutDist(time)
    dx,dy=compute_pos_slide(dist)
    xc+=dx
    yc+=dy
    xypos.write("%.4f %.4f\n" %(xc,yc))
    #print "slide: time",time,"dist",dist,"center",xc,yc
    distp=dist
    for i in range(nx):
        for j in range(ny):
            tmp[i,j]=slideDepth(X[i,j],Y[i,j],xc,yc)
    return tmp

def volume(dx,dy,z):
    #volume in km3
    volume=0
    for i in range(nx):
        for j in range(ny):
            volume+=z[i,j]*dx*dy*0.001
    return volume
            
    
#fill up X and Y:

for i in range(nx):
    X[i,:]+=i*dx+xs
for i in range(ny):
    Y[:,i]+=i*dy+ys

#initial and final slide thickness:
Z=compute_slide(0)
d.write(fname+"_start.nc",X,Y,Z,txt="toplabel=\"start, "+fname+"\"")
Z=compute_slide(tottime)

d.write(fname+"_final.nc",X,Y,Z,txt="toplabel=\"final, "+fname+"\"")

f=open(fname+".tim",'w')

Zp=Z
xcp=xc
ycp=yc
if comcot:
    F=open(fname,'w')
else:
    F=open(fname+"F",'w')
F.close()
#if tstop_man<tottime:
#    print "tottime",tottime
#    print "tstop",tstop_man
#    tottime=tstop_man

maxvol=0
print "tottime %.2f" % tottime
#save time/position in a file:
TP=open(fname+".progr",'w')
for i in range(1,nt+1):
    time=i*dt
    Z=compute_slide(time)
    TP.write("%f %f\n" %(time,findRunoutDist(time)))
    #volume:
    vol=volume(dx,dy,Z)
    if vol>maxvol:
        maxvol=vol
    print "time...",time,"volume",maxvol
    lengthscale=1       #meter
    if km:
        lengthscale=0.001 #km
    if srcsink:
            tmp=lengthscale*(Z-Zp)/dt  
    else:
        tmp=lengthscale*Z
    Zall[:,:,i-1]=tmp
    #write out q:
    #d.write("tmp",((X-xc0)*gdx)+xgc,((Y-yc0)*gdy)+ygc,tmp,type="gphov")
    Zp=Z
    xcp=xc
    ycp=yc
file=open("volume=%.5fkm^3" % maxvol , 'w')
file.close()

#write out acceleration and velocity of slide motion to this file:
AC=open(fname+".acc",'w')
VE=open(fname+".vel",'w')
V2=open(fname+".distvel",'w')
time=2*dt
DT=0.1*dt
while tottime >time:

    p1=findRunoutDist(time-2*DT)
    p2=findRunoutDist(time-DT)
    p3=findRunoutDist(time)
    ac=(p3-2*p2+p1)/(DT*DT)

    AC.write("%f %f\n" %(time,ac*1000))         #m/s2
    VE.write("%f %f\n" %(time,1000*(p3-p2)/DT)) #m/s
    V2.write("%f %f\n" %(p3,1000*(p3-p2)/DT)) #m/s

    time+=dt
   
AC.close()
VE.close()
V2.close()

os.system("rm -f tmp*")


#write out results:
if comcot:
    comf=open(comcotfile,'w')
    comf.write("%d %d %d\n" %(nx,ny,nt))
    #x
    for i in range(nx):
        res=(i*dx+xs-xc0)*gdx+xgc
        comf.write("%f\n" % res)
    #y
    for i in range(ny):
        res=(i*dy+ys-yc0)*gdy+ygc
        comf.write("%f\n" % res)
    #t
    #comtv16=open("bottom_motion_time.dat",'w')
    for i in range(nt):
        res=i*dt
        comf.write("%f\n" % res)
        #comtv16.write("%f\n" % res)
    #comtv16.close()
    print "x0",((X[0,0]-xc0)*gdx)+xgc
    print "y0",((Y[0,0]-yc0)*gdy)+ygc
    print "xe",((X[-1,0]-xc0)*gdx)+xgc
    print "ye",((Y[0,-1]-yc0)*gdy)+ygc

elif geoclaw:
    gcl=open(geoclawfile,'w')
    x0=(((X[0,0]-xc0)*gdx)+xgc)*1000
    y0=(((Y[0,0]-yc0)*gdy)+ygc)*1000
    dx*=1000
    dy*=1000
    t0=0
    #t=t0+dt
    gcl.write("""%(nx)d
%(ny)d
%(nt)d
%(x0)20.10e
%(y0)20.10e
%(t0)20.10e    
%(dx)20.10e
%(dy)20.10e
%(dt)20.10e 
""" %vars())
    

for k in range(1,nt+1):
    tmp=Zall[:,:,k-1]
    #mtv-format for developement:
    if mtv:
        file="slide%04d.mtv" % k
        d.write(file,((X-xc0)*gdx)+xgc,((Y-yc0)*gdy)+ygc,tmp)
    if nc:
        file="slide%04d.nc" % k
        d.write(file,((X-xc0)*gdx)+xgc,((Y-yc0)*gdy)+ygc,tmp)

    if comcot:
        #comfv16=open("bottom_motion_%06d.dat" %(k),'w')
        for j in range(ny):
            for i in range(nx):
                comf.write("%f\n" % Zall[i,j,k-1])
                val=Zall[i,j,k-1]+800
                #comfv16.write("%10.5f\n" % val)
        #comfv16.close()
    elif geoclaw:
        #comfv16=open("bottom_motion_%06d.dat" %(k),'w')
        for j in range(ny-1,-1,-1):
            for i in range(nx):
                #if Zall[i,j,k-1]>0.0:
                #   print "hei",Zall[i,j,k-1]*1000
                if km:
                    val=Zall[i,j,k-1]*1000
                else:
                    val=Zall[i,j,k-1]
                gcl.write("%20.10e " % val)
            gcl.write("\n")
         
    else:
        
        #append stemF file:
        d.write("tmp",((X-xc0)*gdx)+xgc,((Y-yc0)*gdy)+ygc,Zall[:,:,k-1],type="gphov")
        os.system("cat tmp  >> "+fname+"F")
        #write out the time 
        f.write("%f\n" % float((k-1)*dt))
if comcot:
    comf.close()
    print "\n>>>>> completed, file written in XYT (COMCOT) format: "+comcotfile+"  <<<<<\n"
elif geoclaw:
    print "geoc"
    gcl.close()
    print "\n>>>>> completed, file written in tt3 (Geoclaw) format: "+geoclawfile+"  <<<<<\n"
else:
    print "\n>>>>> completed, files written:",fname+"F,",fname+".tim and ",fname+".progr <<<<<\n"

f.close()
xypos.close()
TP.close()


#adjust heading in gphov (include the number of timelevels):
#if comcot or geoclaw:
#    print "passing ..."
#else:
#    lines=open(fname+"F",'r').readlines()
#    firstline=lines[0].strip()
#    print "firstline",firstline
#    firstline=firstline[:-1]+str(nt)
#    print "firstline",firstline
#    file=open(fname+"F",'w')
#    file.write(firstline+"\n")
#    for line in lines[1:]:
#        file.write(line)
#    file.close()

