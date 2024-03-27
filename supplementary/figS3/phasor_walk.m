%
% phasor walks for Greenland VLP record
%
%        this is for Rob Anthony to play with...
% 
%                       Ruedi,  BFO,  26.3.2024
%
clear
set(0, 'defaultaxesfontname', 'Helvetica')
set(0, 'defaultaxesfontsize', 16)
set(0, 'defaultaxeslinewidth', 1.3)
set(0, 'defaulttextfontname', 'Helvetica')
set(0, 'defaulttextfontsize', 16)
%
arch='ieee-le';
[lhz,myhead,dt,nsta,nchn,ntyp,nscan,jy,jd,jh,jm,sec]=read_sac2('II.XBFO.60.LHZ.M.2023,259,6:0:0.SAC',arch);
%
lhz=decimate(decimate(lhz,5),4);
dt=dt*5*4;
N = length(lhz)

lhz=detide(lhz,1/dt);

Q330HR = 2^26/40;            % digitizer gain   
STS6A  = 1200;               % generator constant

lhz = lhz / (Q330HR*STS6A);  % convert to m/s

lhz = 1.e9*lhz ;             % convert to nm/s 

fc = [10 12]'*1e-3;   %  design band-pass filter between 10 and 12 mHz
fnu = 1/(2*dt);
Wc = fc/fnu;

[B,A]=butter(2,Wc);          % butterworth filter 
u = filter(B,A,lhz);         %  apply filter
%
%   target frequencies for three phasor walks
%
w1=10.875/1000;      % 
w2=10.88/1000;       % 
w3=10.89/1000;       % 
%
%  compute phasor walks. 
%     u is the seismogram
%     p1,p2,p3 contain the complex phasors of each sample u
%     X1,X2,X3 contain the summed phasors
%     X1(end), X2(end), X3(end) are the digital Fourier transform DFT of the whole series u 
%          at the respective frequencies w1,w2 or w3.
%

t = (0:N-1)'*dt;       %  Time axis
e = exp(-2*pi*w1*i*t);    p1 = u .* e;
e = exp(-2*pi*w2*i*t);    p2 = u .* e;
e = exp(-2*pi*w3*i*t);    p3 = u .* e;

X1 = cumsum(p1)/N;
X2 = cumsum(p2)/N;
X3 = cumsum(p3)/N;

figure(1),plot(X1,'r;10.875 mHz;');     %  plot real vs imaginary parts of X1
title(['phasor walk, BFO STS-6A 51h';'Symbols at 10hr intervals']) 
grid
xlabel('real part')
ylabel('imaginary part')
axis equal

hold on
plot(X2,'b;10.88 mHz;')
plot(X3,'k;10.89 mHz;')

n10h = 10*3600/dt;
n20h = 20*3600/dt;
n30h = 30*3600/dt;
n40h = 40*3600/dt;

plot(real(X1(n10h)),imag(X1(n10h)),'*r')
plot(real(X1(n20h)),imag(X1(n20h)),'*r')
plot(real(X1(n30h)),imag(X1(n30h)),'*r')
plot(real(X1(n40h)),imag(X1(n40h)),'*r')

plot(real(X2(n10h)),imag(X2(n10h)),'*b')
plot(real(X2(n20h)),imag(X2(n20h)),'*b')
plot(real(X2(n30h)),imag(X2(n30h)),'*b')
plot(real(X2(n40h)),imag(X2(n40h)),'*b')

plot(real(X3(n10h)),imag(X3(n10h)),'*k')
plot(real(X3(n20h)),imag(X3(n20h)),'*k')
plot(real(X3(n30h)),imag(X3(n30h)),'*k')
plot(real(X3(n40h)),imag(X3(n40h)),'*k')
hold off

% print -dpdfcairo fig_phasor_RA.pdf
print -dpdf      fig_phasor_RA.pdf

