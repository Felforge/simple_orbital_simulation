import numpy as np
from scipy.integrate import solve_ivp

class PhysicsEngine:
    """
    Engine for oribital physics
    """
    def __init__(self, v0, r0):
        self.gravitational_const = 6.6743e-11
        self.sun_mass = 1.988416e30
        self.mu = self.gravitational_const * self.sun_mass
        self.r0 = r0
        self.v0 = v0
        self.energy = 0.5 * (v0**2) - self.mu/r0
        self.special_angular_momentum = r0 * v0

    def get_semi_major(self):
        """
        Get furthest distance from point of rotation
        """
        return -self.mu / (2 * self.energy)

    def get_semi_minor(self):
        """
        Get closest distance to point of rotation
        """
        return self.special_angular_momentum / np.sqrt(self.mu / self.get_semi_major())

    def motion_derivatives(self, _, current_state):
        """
        Get derivatives of r, phi, and v_r to be used in finding position
        """
        r, _, r_dot = current_state
        phi_dot = self.special_angular_momentum/(r**2)
        r_ddot = r*(phi_dot**2) - self.mu/(r**2)
        return [r_dot, phi_dot, r_ddot]

    def get_position(self, t):
        """
        Find position at time t
        """
        state_0 = [self.r0, 0, 0]
        state_t = solve_ivp(self.motion_derivatives, [0, t], state_0, method="RK45",
                            rtol=1e-8, atol=1e-8, max_step=self.get_orbital_period()/100)
        r = state_t.y[0][-1]
        phi = state_t.y[1][-1]
        omega = self.special_angular_momentum/(r**2)
        v_t = r * omega
        return r, phi, v_t

    def get_orbital_period(self):
        """
        Return orbital period in seconds
        """
        return 2 * np.pi * np.sqrt(self.get_semi_major()**3 / self.mu)

    def get_eccentricity(self):
        """
        Get eccentricity of orbit
        """
        return np.sqrt(1 - (self.get_semi_minor()**2)/(self.get_semi_major()**2))

    def get_v_max(self):
        """
        Return maximum velocity of orbit in m/s
        """
        v_max_1 = np.sqrt(2 * self.mu / self.r0)
        multiple = (1 + self.get_eccentricity()) / (1 - self.get_eccentricity())
        v_max_2 = np.sqrt(self.mu / self.get_semi_major()) * multiple
        return min(v_max_1, v_max_2)


    def get_v_min(self):
        """
        Return minim velocity of orbit in m/s
        """
        divisor = self.get_semi_major() * (1 + self.get_eccentricity())
        return np.sqrt(self.mu / divisor)
