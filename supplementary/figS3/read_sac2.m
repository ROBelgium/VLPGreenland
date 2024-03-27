function [x,myhead,dt,nsta,nchn,ntyp,nscan,jy,jd,jh,jm,sec] = read_sac2(fname,arch)
%
%  [x,myhead,dt,nsta,nchn,ntyp,nscan,jy,jd,jh,jm,sec]=read_sac2(fname,arch); reads SAC binary file 
%     where: fname is the file name
%            arch  is ieee-le (=little-endian) or ieee-be (=big-endian)');
%
%                     ieee-le is suitable for INTEL
%                     ieee-be is suitable for SUN and MOTOROLA architectures
%
%     output:   x       seismogram
%               myhead  header of timeseries.
%               dt      sample interval in seconds
%               nsta    station code
%               nchn    channel code
%               ntyp    network code
%               nloc    location code
%
%                                -Ruedi, 15.5.2014, BFO
%
if ( (nargin < 1) || (nargin > 2) )
   usage('read_sac(fname,arch) reads SAC binary file where fname is filename \n and arch is ieee-le (=little-endian) or ieee-be (=big-endian)');
   return;
elseif (nargin == 1)
  arch = 'ieee-le';          % ieee-le is suitable for INTEL
end

fid=fopen (fname,'rb',arch); 
if (fid ==-1) 
  error (['Error opening ',fname,' for input !']); 
end; 
 
bpw=4;              % bytes per word    
% read SAC header 
  dt                 = fread (fid,1,'float32');
                       fseek (fid,70*bpw,'bof'); 
  jy                 = fread (fid,1,'int32');
  jd                 = fread (fid,1,'int32');
  jh                 = fread (fid,1,'int32');
  jm                 = fread (fid,1,'int32');
  sec                = fread (fid,1,'int32');
  msec               = fread (fid,1,'int32');
                       fseek (fid,79*bpw,'bof'); 
  nscan              = fread (fid,1,'int32');
                       fseek (fid,110*bpw,'bof'); 
  nsta               = strvcat(fread (fid,5,'char*1')); 
  nsta               = deblank(nsta');
                       fseek (fid,112*bpw,'bof'); 
  nloc               = strvcat(fread (fid,5,'char*1')); 
  nloc               = deblank(nloc');
                       fseek (fid,150*bpw,'bof'); 
  nchn               = strvcat(fread (fid,5,'char*1'));  
  nchn               = deblank(nchn');
                       fseek (fid,152*bpw,'bof'); 
  ntyp               = strvcat(fread (fid,5,'char*1'));  
  ntyp               = deblank(ntyp');
% read data
                       fseek (fid,158*bpw,'bof'); 
  x                  = fread (fid,nscan,'float32');

fclose (fid); 

sec=sec+0.001*msec;

myhead=sprintf('    1  %-4s %-4s %-4s %4d %03d:%02d:%02d:%06.3f %9.3f%9d',nsta,nchn,ntyp,jy,jd,jh,jm,sec,dt,nscan); 
printf('%s\n',myhead);
%
% now write out gfs-ascii file
%
% gfsname='myfile.gfs';
% fid=fopen (gfsname,'wt'); 
% fprintf(fid,'    1  %4s %4s %4s %4d %03d:%02d:%02d:%06.3f %9.3f%9d\n',nsta,nchn,ntyp,jy,jd,jh,jm,sec,dt,nscan); 
% fprintf(fid,'%17.12g\n',x);
% fclose (fid); 

% save -binary p1s32.bin x
