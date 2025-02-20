import os
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.rcParams['animation.ffmpeg_path'] = '/ffmpeg/bin'
import matplotlib.colors as col
import matplotlib.cm as cm
import pdb
import math

# Choose boundaries of plasma in mm
xstep_mm = 1
xend_mm = 500

# Definition of Constants
C = 299892458                        # Speed of light in vacuum in m/s

def Gamma(p):
    return math.sqrt(1.0 + p**2)

def Velocity(px,ptot):
# Returns relativistic velocity from momentum
    return px / Gamma(ptot)

def getBallisticTraj(x_0,y_0,z_0,xi_0,px,py,pz,x_s):
# Use ballistic matrix to find positions on screens
    dx = x_s - x_0
    y_f = y_0 + dx * (py/px)
    z_f = z_0 + dx * (pz/px)

# Find time traveled to get proper xi
    p = math.sqrt(px**2 + py**2 + pz**2)
    vx = Velocity(px, p)
    vy = Velocity(py, p)
    vz = Velocity(pz, p)
    vtot = math.sqrt(vx**2 + vy**2 + vz**2)
    dtot = math.sqrt((x_s - x_0)**2 + (y_f - y_0)**2 + (z_f - z_0)**2)
    t = dtot/vtot

    xi_f = xi_0 + dx * (pz/px) + t

    return y_f, z_f, xi_f

def find_nearest_index(array,value):
    idx = np.searchsorted(array, value, side="right")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
        return idx-1
    else:
        return idx

def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)

def animate(x_f,y_f,xi_f,z_f,px_f,py_f,pz_f,sim_name,shape_name,noElec,iter):
    if (sim_name.upper() == 'OSIRIS_CYLINSYMM'):
        import include.simulations.useOsiCylin as sim
    elif (sim_name.upper() == 'QUASI3D'):
        import include.simulations.useQuasi3D as sim
    else:
        print("Simulation name unrecognized. Quitting...")
        exit()

# Define step size, current and end location in normalized units
    W_P = sim.getPlasFreq()
    xstep = xstep_mm * W_P * 10**(-3) / C
    xend = xend_mm * W_P * 10**(-3) / C
    xiter = int(xend_mm/xstep_mm)
    xn = 0
    xn_mm = 0
    y_dat, z_dat, xi_dat = [],[],[]

# # Histogram options
#     binsizez = 50
#     binsizey = 40
#     norm = mpl.colors.Normalize(vmin=0, vmax=50)
#     cmap = plt.cm.gist_gray

# Set up FFMpeg and figure
    Writer = animation.FFMpegWriter(fps=30, codec='libx264')
    metadata = dict(title='Movie Test', artist='Matplotlib',
                    comment='Movie support!')
    fig, ax = plt.subplots()
    #fig.subplots_adjust(bottom=-0.1)

    probe, = plt.plot([], [], 'C0o', markersize='2')
    #probe, = ax.hist2d(xi_dat, y_dat, bins=(binsizez,binsizey), cmap=cmap, norm=norm)
    plt.ylim(-1, 1)
    plt.xlim(35,40)#(15, 65)
    plt.xlabel('Z ($c/\omega_p$)')
    plt.ylabel('Y ($c/\omega_p$)')

    #xi_ax = ax.twiny()
    #xi_ax.set_xlabel("$\\xi$ ($c/\omega_p$)")
    #xi_ax.set_xlim(-37,13)

# Generate movie
    #pdb.set_trace()
    with Writer.saving(fig,"eProbe.mp4", dpi=400):
    # Start with initial position at 0 mm
        for i in range(0,noElec):
            y_dat.append(y_f[i])
            z_dat.append(z_f[i])
        probe.set_data(z_dat, y_dat)
        ax.set_title("X = 0 mm")
        writer.grab_frame()
    # Move electrons outside of plasma
        for i in range(0,xiter):
            y_dat.clear()
            z_dat.clear()
            xn += xstep
            xn_mm += xstep_mm
            ax.set_title("Electron Probe Evolution: X = " + str(xn_mm) + " mm" )
            for j in range(0,noElec):
                yn, zn, xin = getBallisticTraj(x_f[j], y_f[j], z_f[j], xi_f[j], px_f[j], py_f[j], pz_f[j], xn)
                y_dat.append(yn)
                z_dat.append(zn)
            probe.set_data(z_dat, y_dat)
            writer.grab_frame()
    print("Movie saved!")
# For movie inside plasma (probe should not change shape)
    #with writer.saving(fig, "writer_test.mp4", dpi=400):
    #     for i in range(len(x_dat)):
    #         ax.set_title("X = " + str(x_dat[0,i]) + " c/$\omega_p$" )
    #         probe.set_data(xi_dat[:,i], y_dat[:,i])
    #         writer.grab_frame()
