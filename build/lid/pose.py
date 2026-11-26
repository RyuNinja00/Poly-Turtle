"""Rigid re-pose of the Smol + PREP so filament travels uphill (rev 2 lid).

Archived pose (cad/01): travel direction A descends 24.84 deg toward +X, inlet
(PREP) at the high -X end.  Rev 2: rotate 180 deg about Z, then tilt so the
travel direction rises ALPHA deg toward -X; the inlet becomes the low +X end and
filament comes up off the +X side of the spool.  pose(p) maps an archived
point to its new position.
"""
import numpy as np
from scipy.spatial.transform import Rotation as Rot

TF0 = np.array([50.82170486028815, -1.52379502811359, 104.38142041181])   # archived axis point
A0 = np.array([0.90750213, 0.0, -0.42004747])
V0 = np.array([0.41978434, -0.03539018, 0.90693365])
EL0 = np.degrees(np.arcsin(A0[2]))          # -24.84

def rotation(alpha):
    Rz = Rot.from_euler('z', 180, degrees=True)
    # after Rz the axis is (-0.9075, 0, -0.42): descending toward -X by |EL0|.
    # rotate about +Y by -(alpha - EL0) ... sign chosen numerically below
    for s in (1, -1):
        R = Rot.from_euler('y', s * (alpha - EL0), degrees=True) * Rz
        a = R.apply(A0)
        if abs(np.degrees(np.arcsin(a[2])) - alpha) < 1e-6 and a[0] < 0: return R
    raise ValueError

class Pose:
    def __init__(self, alpha, inlet):
        """inlet = new global position of the PREP entry point (axis, u = -50)."""
        self.alpha = alpha; self.R = rotation(alpha)
        p0 = TF0 + (-50.0) * A0
        self.t = np.asarray(inlet, float) - self.R.apply(p0)
        self.TF = self(TF0); self.A = self.R.apply(A0); self.V = self.R.apply(V0); self.W = np.cross(self.V, self.A)
    def __call__(self, P):
        return self.R.apply(np.asarray(P, float)) + self.t
