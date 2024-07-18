function y = detide(x,f)

%  if x is a time-series of values sampled at frequency f, detide(x,f) 
%  removes diurnal and semi-diurnal tides from the time series
%  by fitting sines and cosines of periods corresponding to 01, k1, n2, m2, and s2
%  (all of these are around 12 or 24 hrs)
%  P is the sampling period  
%

P = 1/f;
g1 = detrend(x);

%  make sure g1 is a column vector

g1 = g1(:);


% compute main tidal frequencies in Hz

%main tidal components, periods in hours:

o1 = 25.82;
k1 = 23.93;
n2 = 12.66;
m2 = 12.42;
s2 = 12.00;

p1 = 24.07;
k2 = 11.97;

% convert to frequencies in Hz

o1 = 1/(3600*o1);
k1 = 1/(3600*k1);
n2 = 1/(3600*n2);
m2 = 1/(3600*m2);
s2 = 1/(3600*s2);

p1 = 1/(3600*p1);
k2 = 1/(3600*k2);

% generate sines and cosines
% also vector of times in seconds

n = 1:length(g1);
t = P*n;

dc = ones(1,length(g1));

  so1 = sin(2*pi*o1*t);
  co1 = cos(2*pi*o1*t);
  sk1 = sin(2*pi*k1*t);
  ck1 = cos(2*pi*k1*t);
  sn2 = sin(2*pi*n2*t);
  cn2 = cos(2*pi*n2*t);
  sm2 = sin(2*pi*m2*t);
  cm2 = cos(2*pi*m2*t);
  ss2 = sin(2*pi*s2*t);
  cs2 = cos(2*pi*s2*t);
  
  sp1 = sin(2*pi*p1*t);
  cp1 = cos(2*pi*p1*t);
  sk2 = sin(2*pi*k2*t);
  ck2 = cos(2*pi*k2*t);

  design = [dc' so1' co1' sk1' ck1' sn2' cn2' sm2' cm2' ss2' cs2' sp1' cp1' sk2' ck2'];
  c = design\g1;
  
  %  normally the next two lines will be gone
  
  m2_amplitude = sqrt(c(8)^2 + c(9)^2);
  
  o1_amplitude = sqrt(c(2)^2 + c(3)^2);
  
  solution = c(1)*dc+c(2)*so1+c(3)*co1+c(4)*sk1+c(5)*ck1+c(6)*sn2+c(7)*cn2+c(8)*sm2+c(9)*cm2+c(10)*ss2+c(11)*cs2+c(12)*sp1+c(13)*cp1+c(14)*sk2+c(15)*ck2;

y = detrend(g1 - solution');

%  now make sure the returned vector (y) is a row/column vector if the the original (x) is a row/column vector

[m n] = size(x);
if m == 1
	y = y';
end

