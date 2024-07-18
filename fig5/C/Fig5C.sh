#!/bin/sh
# this is <Fig5C.sh>
# ----------------------------------------------------------------------------
# 
# Copyright (c) 2023 by Thomas Forbriger (KIT, GPI, BFO) 
# 
# create Fig 5C
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
#    30/11/2023   V1.0   Thomas Forbriger
# 
# ============================================================================
#
# Download timeseries data and metadata needed for the diagram
# ------------------------------------------------------------

BEGIN=2023/09/16T00:00:00
END=2023/09/19T12:00:00

TSBASE=STS6BFO_long_20230916

./dldata.py --network II --location '10' \
  --begin $BEGIN --end $END --outbase $TSBASE \
  --station BFO R
 
# ============================================================================

OUTBASE=Fig4C
#
BEGIN=2023/09/16T11:00:00
END=2023/09/17T12:00:00

fHP=0.01
fLP=0.012

INBASE=${TSBASE}

#    --decay 5000.,0.08,2023-09-16T12:30:00 \
dodecayplot() {
  ./plotdecay.py --verbose --quantity displacement $* \
    --traceshift 0.2 \
    --begin $BEGIN \
    --end $END \
    --inbase ${INBASE} \
    --outbase ${OUTBASE} \
    --decay 500.,0.3,2023-09-16T12:30:00 \
    --decay 3000.,0.10,2023-09-16T12:30:00 \
    --fHP $fHP --fLP $fLP  --noshow 
}

doZplot() {
  ./plotdecay.py --verbose --quantity displacement  \
    --traceshift 0. \
    --begin $BEGIN \
    --end $END \
    --components Z \
    --titlefontsize "xx-small" \
    --fHP $fHP --fLP $fLP  --noshow  $*
}

NETWORK=II
STATION=BFO
dodecayplot ${NETWORK} ${STATION} --figsize=28.,14. 

BEGIN=2023-09-16T12:30:00
END=2023-09-16T13:15:00
doZplot ${NETWORK} ${STATION} --inbase=${INBASE} --outbase=${OUTBASE}Z \
  --figsize=16.,12. 

evince ${OUTBASE}*.pdf

# ----- END OF Fig5C.sh ----- 
