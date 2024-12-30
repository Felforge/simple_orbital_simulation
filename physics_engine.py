import numpy as np
from scipy.integrate import solve_ivp

class PhysicsEngine:
    """
    Engine for oribital physics
    """
    def __init__(self, v0, r0, theta):
        self.gravitational_const = 6.6743e-11
        self.sun_mass = 1.988416e30
        self.mu = self.gravitational_const * self.sun_mass
        self.energy = 0.5 * (v0**2) - self.mu/r0
        self.r0 = r0
        self.v_r = v0 * np.sin(theta)
        self.v_t = v0 * np.cos(theta)
        self.angular_momentum = r0 * v0

    def get_semi_major(self):
        """
        Get furthest distance from point of rotation
        """
        return -self.mu / (2 * self.energy)

    def get_semi_minor(self):
        """
        Get closest distance to point of rotation
        """
        return self.angular_momentum / np.sqrt(self.mu * self.get_semi_major())

    def motion_derivatives(self, current_state):
        """
        Get derivatives of r, phi, and v_r to be used in finding position
        """
        r, _, r_dot = current_state
        phi_dot = self.angular_momentum/(r**2)
        r_ddot = r*(phi_dot**2) - self.mu/(r**2)
        return [r_dot, phi_dot, r_ddot]

    def get_position(self, t):
        """
        Find position at time t
        """
        state_0 = [self.r0, 0, self.v_r]
        state_t = solve_ivp(self.motion_derivatives, [0, t], state_0, method="RK4")
        r = state_t[0]
        phi = state_t[1]
        return r, phi
