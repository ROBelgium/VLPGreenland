#!/usr/bin/env python
# this is <FjordGeometry.py>
# ----------------------------------------------------------------------------
# 
# Copyright (c) 2023 by Thomas Forbriger (KIT, GPI, BFO) 
# 
# draw a sketch of the simplified fjord geometry
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
#    19/12/2023   V1.0   Thomas Forbriger
# 
# ============================================================================
#
import numpy as np
import copy 
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# ============================================================================
# set parameters

# the values of hs and dz are highly exaggerated with respect to the actual
# computation, where hs=20. and dz=8.8
# this is necassary to make these dimensions visible in the sketch

# width of fjord
L=2700.
# max depth of fjord
h=540.
# the extent of the shore wall to below the water surface
hs=110.
# vertical deflection of the water surface at the shore
dz=0.7*hs

# ============================================================================
# define polygons
# ---------------
BasinCrossSection=Polygon([(-L/2.,-1.5*hs),
                           (-L/2.,hs),
                           (0.,h),
                           (L/2.,hs),
                           (L/2.,-1.5*hs)],closed=False,fill=False)

# ----------------------------------------------------------------------------

WaterBody=Polygon([(-L/2.,dz),
                   (-L/2.,hs),
                   (0.,h),
                   (L/2.,hs),
                   (L/2.,-dz)],closed=False,fill=True, alpha=0.5,
                  zorder=-2)

# ============================================================================
# define functions
# ----------------
def plotarrow(ax, x1, y1, x2, y2):
    """
    Plot an arrow for annotations.

    Parameters:
        ax : matplotlib.pyplot.Axes
        x1, y1 : x,y-coordinates of the origin of the arrow
        x2, y2 : x,y-coordinates of the tip of the arrow
    """
    ax.arrow(x1, y1, x2-x1, y2-y1,
             width=0., 
             head_width=15.,
             fill=True,
             color='black',
             shape='full', 
             length_includes_head=True, 
             zorder=2)

# ----------------------------------------------------------------------------
def triangle(A, B, C, color):
    """
    Compute a triangle.

    Parameters:
        A, B, C : 2-tuples of floats
            x,y-coordinates of the three corners
        color : str
            color to be used for the polygon

    Returns:
        xc, yc, area, polygon
            xc, yc : float
                coordinates of the center of mass
            area : float
                area of the triangle
            polygon : matplotlib.patches.Polygon
                graphical representation of the triangle
    """
    xc=(A[0]+B[0]+C[0])/3.
    yc=(A[1]+B[1]+C[1])/3.
    area=0.5*np.abs((B[0]-A[0])*(C[1]-A[1])-(C[0]-A[0])*(B[1]-A[1]))
    polygon=Polygon([A,B,C],closed=True,fill=True,color=color,
                    linewidth=0.,
                    zorder=-2)
    return xc, yc, area, polygon

# ----------------------------------------------------------------------------
def rectangle(A, B, color):
    """
    Compute a rectangle.

    Parameters:
        A, B : 2-tuples of floats
            x,y-coordinates of the lower left and upper right corners
        color : str
            color to be used for the polygon

    Returns:
        xc, yc, area, polygon
            xc, yc : float
                coordinates of the center of mass
            area : float
                area of the rectangle
            polygon : matplotlib.patches.Polygon
                graphical representation of the rectangle
    """
    xc=(A[0]+B[0])/2.
    yc=(A[1]+B[1])/2.
    area=np.abs((A[0]-B[0])*(A[1]-B[1]))
    polygon=Polygon([(A[0], A[1]),
                     (A[0], B[1]),
                     (B[0], B[1]),
                     (B[0], A[1])],closed=True,fill=True,color=color,
                    linewidth=0.,
                    zorder=-2)
    return xc, yc, area, polygon

# ----------------------------------------------------------------------------
# mark length
marklength=L/40
def plot_watersurface(ax):
    """
    Plot the undisturbed water surface

    Parameter:
        ax : matplotlib.pyplot.Axes
    """
    ax.plot([-L/2., L/2.], [0.,0.], ls='--', color='black',
            linewidth=0.5)

# ----------------------------------------------------------------------------
def plot_markhs(ax):
    """
    Plot the annotations for the wall height hs

    Parameter:
        ax : matplotlib.pyplot.Axes
    """
    ax.plot([L/2., L/2.+marklength], [0.,0.], ls='--', color='black',
            linewidth=0.5)
    ax.plot([L/2., L/2.+marklength], [hs,hs], ls='--', color='black',
            linewidth=0.5)
    plotarrow(ax, (L+1.*marklength)/2., 0., (L+1.*marklength)/2., hs)
    plotarrow(ax, (L+1.*marklength)/2., hs, (L+1.*marklength)/2., 0.)
    ax.text((L+1.5*marklength)/2.,0.5*hs,'$h_s$',
            horizontalalignment='left',
            verticalalignment='center')

# ----------------------------------------------------------------------------
def plot_markh(ax):
    """
    Plot the annotations for the maximum water depth h

    Parameter:
        ax : matplotlib.pyplot.Axes
    """
    ax.plot([-L/2., -L/2.-marklength], [0.,0.], ls='--', color='black',
            linewidth=0.5)
    ax.plot([0., -L/2.-marklength], [h,h], ls='--', color='black',
            linewidth=0.5)
    plotarrow(ax, -(L+marklength)/2., 0., -(L+marklength)/2., h)
    plotarrow(ax, -(L+marklength)/2., h, -(L+marklength)/2., 0.)
    ax.text(-(L+1.5*marklength)/2.,0.5*h,'$h$',
            horizontalalignment='right',
            verticalalignment='center')

# ----------------------------------------------------------------------------
def plot_markdz(ax):
    """
    Plot the annotations for the maximum deflection of the water surface

    Parameter:
        ax : matplotlib.pyplot.Axes
    """
    ax.plot([L/2., L/2.+marklength], [0.,0.], ls='--', color='black',
            linewidth=0.5)
    ax.plot([L/2., L/2.+marklength], [-dz, -dz], ls='--', color='black',
            linewidth=0.5)
#     plotarrow(ax, (L+1.0*marklength)/2., -2.*dz, (L+1.0*marklength)/2., -dz)
#     plotarrow(ax, (L+1.0*marklength)/2., dz, (L+1.0*marklength)/2., 0.)
    plotarrow(ax, (L+1.*marklength)/2., 0., (L+1.*marklength)/2., -dz)
    plotarrow(ax, (L+1.*marklength)/2., -dz, (L+1.*marklength)/2., 0.)
    ax.text((L+1.5*marklength)/2.,-0.5*dz,'$\Delta z$',
            horizontalalignment='left',
            verticalalignment='center')

# ----------------------------------------------------------------------------
def plot_markL(ax):
    """
    Plot the annotations for the fjord width L

    Parameter:
        ax : matplotlib.pyplot.Axes
    """
    plotarrow(ax, -L/2., -1.*hs, L/2., -1.*hs)
    plotarrow(ax, L/2., -1.*hs, -L/2., -1.*hs)
    ax.text(0.,-1.1*hs,'$L$',
            horizontalalignment='center',
            verticalalignment='bottom')

# ============================================================================
# compute coordinates of center of mass 

# we subdivide the water body:
#   in the undistrubed equilibrium case (horizontal surface):
#     1. a triangle C
#     2. a rectangle N
#   in the case of the deflected water surface:
#     1. a basic triangle C
#     2. a rectangle B in between the walls
#     3. a triangle A at the water surface
Acol='#ff8888'
Bcol='#88ff88'
Ccol='#8888ff'
ACx, ACy, AA, AP=triangle((-L/2., dz),
                  (L/2.,dz),
                  (L/2.,-dz),
                  Acol)
BCx, BCy, BA, BP=rectangle((-L/2., dz),
                  (L/2.,hs),
                  Bcol)
CCx, CCy, CA, CP=triangle((-L/2., hs),
                  (L/2.,hs),
                  (0.,h),
                  Ccol)
NCx, NCy, NA, NP=rectangle((-L/2., 0),
                  (L/2.,hs),
                  Bcol)

# compute the center of mass of the water body in the deflected state
Cx=(ACx*AA+BCx*BA+CCx*CA)/(AA+BA+CA)
Cy=(ACy*AA+BCy*BA+CCy*CA)/(AA+BA+CA)

# compute the center of mass of the water body in the equilibrium state
Nx=(NCx*NA+CCx*CA)/(AA+BA+CA)
Ny=(NCy*NA+CCy*CA)/(AA+BA+CA)

# ----------------------------------------------------------------------------
def plotgeometry(ax):
    """
    Plot the background geometry needed for both sketches

    Parameter:
        ax : matplotlib.pyplot.Axes
    """
    plot_watersurface(ax)
    plot_markhs(ax)
    plot_markdz(ax)
    plot_markh(ax)
    plot_markL(ax)
    ax.set_aspect(1)
    ax.add_patch(copy.deepcopy(BasinCrossSection))
    ax.set(autoscale_on=True)
    ax.set(frame_on=False)
    ax.invert_yaxis()
    plotarrow(ax, Nx, Ny, Cx, Cy)
    ax.scatter([Nx], [Ny], s=0.2*dz, color='black', zorder=2)
    ax.grid(linewidth=0.4, linestyle=':')
    ax.set_xlabel('coordinate / m')
    ax.set_ylabel('depth / m')
    ax.set_title('Simplified cross-section of Dickson Fjord')

# ============================================================================
# plot sketch
# ===========

# plot fjord seiche
# -----------------
fig, ax = plt.subplots(figsize=(10.,4.))
#fig.canvas.draw()
plotgeometry(ax)
ax.add_patch(WaterBody)
# ax.set_xlim([-0.52*L,0.52*L])
# ax.set_ylim([-1.2*h,1.2*hs])
fig.savefig('FjordSeicheGeometry.pdf')
fig.savefig('FjordSeicheGeometry.png', dpi=300)
fig.savefig('FjordSeicheGeometry.svg', dpi=300)
del fig

# ----------------------------------------------------------------------------
# plot subvolumes
# ---------------

fig, ax = plt.subplots(figsize=(10., 4.))
#fig.canvas.draw()
plotgeometry(ax)
ax.add_patch(AP)
ax.add_patch(BP)
ax.add_patch(CP)

fig.savefig('FjordSubvolumesGeometry.pdf')
fig.savefig('FjordSubvolumesGeometry.png', dpi=300)
fig.savefig('FjordSubvolumesGeometry.svg', dpi=300)
del fig

# ----- END OF FjordGeometry.py ----- 
