#!/bin/sh
# this is <pmplots1st.sh>
# ----------------------------------------------------------------------------
# 
# Copyright (c) 2023 by Thomas Forbriger (KIT, GPI, BFO) 
# 
# particle motion plots for fundamental frequency of 10.88 mHz and 
# first overtone at 21.6 mHz
#
# ----
# Licensed under the EUPL, Version 1.1 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
#
# https://joinup.ec.europa.eu/software/page/eupl5
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
# ----
#
# REVISIONS and CHANGES 
#    30/09/2023   V1.0   Thomas Forbriger
# 
# ============================================================================
#
#
VERSION=2023-12-01

# ----------------------------------------------------------------------------
# download time series data and metadata
BEGIN=2023/09/16T12:00:00
END=2023/09/17T12:00:00
CASEBASE=20230916

dodownload() {
##  dldata.py --datacenter BGR --network GR --location '*' \
##    --begin $BEGIN --end $END --outbase $CASEBASE \
##    --station BFO R
## 
##  dldata.py --datacenter GEOFON --network DK \
##    --begin $BEGIN --end $END --outbase $CASEBASE \
##    --location '' \
##    --station SCO R
## 
##  dldata.py --network IU --location '00' \
##    --begin $BEGIN --end $END --outbase $CASEBASE \
##    --station TIXI,ANMO,ULN,PAB,KEV,KONO,COLA,KBS,SFJD,SSPA R
## 
##  dldata.py --network II --location '00' \
##    --begin $BEGIN --end $END --outbase $CASEBASE \
##    --station ALE,BFO,BORG,KDAK R

  dldata.py --network IU --location '00' \
    --begin $BEGIN --end $END --outbase $CASEBASE \
    --station KEV,SFJD R
 
  dldata.py --network II --location '00' \
    --begin $BEGIN --end $END --outbase $CASEBASE \
    --station ALE R
}

dodownload

# ----------------------------------------------------------------------------
EBEGIN=2023/09/16T12:30:00
EEND=2023/09/16T14:00:00
LBEGIN=2023/09/16T15:30:00
LEND=2023/09/16T17:30:00

HIGHPASS=0.009
LOWPASS=0.023
SOURCELOC=72.833,-27.0

doplot() {
  ./plotstation.py --verbose --quantity acceleration $1 $2 \
    --begin $LBEGIN \
    --end $LEND \
    --inbase $CASEBASE \
    --source $SOURCELOC \
    --outbase polarization \
    --FFTbandwidth 2. \
    --fHP $HIGHPASS \
    --fLP $LOWPASS --noshow

  ./plotstation.py --verbose --quantity acceleration $1 $2 \
    --begin $LBEGIN \
    --end $LEND \
    --inbase $CASEBASE \
    --source $SOURCELOC \
    --ZNE \
    --outbase polarizationZNE \
    --FFTbandwidth 2. \
    --fHP $HIGHPASS \
    --fLP $LOWPASS --noshow

  ./plotstation.py --verbose --quantity displacement $1 $2 \
    --begin $LBEGIN \
    --end $LEND \
    --inbase $CASEBASE \
    --source $SOURCELOC \
    --outbase particlemotion \
    --FFTbandwidth 2. \
    --fHP $HIGHPASS \
    --fLP $LOWPASS --noshow

  ./plotstation.py --verbose --quantity acceleration $1 $2 \
    --begin $EBEGIN \
    --end $EEND \
    --inbase $CASEBASE \
    --source $SOURCELOC \
    --outbase early_polarization \
    --FFTbandwidth 2. \
    --fHP $HIGHPASS \
    --fLP $LOWPASS --noshow
}

doplot IU KEV
doplot IU SFJD
doplot II ALE

exit

doplot IU SSPA
doplot II BORG
doplot IU TIXI
doplot DK SCO
doplot II BFO
doplot IU ANMO
doplot IU ULN
doplot IU PAB
doplot IU KONO
doplot IU COLA
doplot IU KBS

# ----- END OF pmplots1st.sh ----- 
