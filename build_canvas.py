import math
import tkinter as tk
from tkinter import ttk
import numpy as np
import sv_ttk
from physics_engine import PhysicsEngine

class SimpleOribitalSimulation:
    """
    Build canvas for simple orbital simulation
    """
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.width = config["width"]
        self.height = config["height"]
        self.frame_rate = config["animation_fps"]
        self.animation_delay = 1000 // self.frame_rate
        self.orbit_duration = config["orbit_duration"]
        self.time_step = None
        self.time_ellapsed = 0
        self.running = False
        self.started = False
        self.phi = 0
        self.velocity_vector = None
        self.physics_engine = None

        self.root.title(config["window_title"])
        self.root.geometry(f"{self.width}x{self.height}")

        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        control_x = config["control_x"]
        self.display_width = self.width - control_x - 40 # 40 is 4 times padx
        self.display_height = self.height - 20 # 20 is 2 times pady

        self.canvas = tk.Canvas(
            self.main_container,
            width = self.display_width,
            height = self.display_height,
            bg = config["background_color"]
        )
        self.canvas.pack(side=tk.LEFT, padx=(0, 10))

        self.control_panel = ttk.Frame(self.main_container, width=control_x)
        self.control_panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.control_panel.pack_propagate(False)

        self.create_sun()

        self.v = 1000 * self.config["default_velocity"] # Kilometers per Second
        self.r = self.config["earth_distance"] * 1.609344e9 # Millions of Miles

        self.earth = self.create_earth(self.r, self.phi, self.v)

        self.trajectory = self.create_trajectory()

        title_label = ttk.Label(
            self.control_panel,
            text="Controls",
            font=('Arial', 20, 'bold')
        )
        title_label.pack(pady=(0, 10))

        self.create_initial_conditions_group()

        self.create_buttons()

        sv_ttk.set_theme("dark")

    def create_sun(self):
        """
        Create sun in the center of the canvas
        """
        sun_color = self.config["sun_color"]
        self.sun_radius = self.config["sun_radius"]
        self.sun_center_x = self.display_width // 2
        self.sun_center_y = self.display_height // 2
        self.canvas.create_oval(
            self.sun_center_x - self.sun_radius,
            self.sun_center_y - self.sun_radius,
            self.sun_center_x + self.sun_radius,
            self.sun_center_y + self.sun_radius,
            fill = sun_color,
            outline=""
        )

    def create_earth(self, r, phi, v):
        """
        Generates earth at distance r and angle phi
        """
        earth_color = self.config["earth_color"]
        r_x = r * math.cos(phi)
        r_y = r * math.sin(phi)
        self.earth_radius = self.config["earth_radius"]
        self.earth_center_x = self.distance_to_pixels(r_x) + self.sun_center_x
        self.earth_center_x += (self.sun_radius + self.earth_radius) * math.cos(phi)
        self.earth_center_y = self.distance_to_pixels(r_y) + self.sun_center_y
        self.earth_center_y += (self.sun_radius + self.earth_radius) * math.sin(phi)
        if self.velocity_vector is not None:
            self.delete_velocity_vector(self.velocity_vector)
        self.velocity_vector = self.build_velocity_vector(v, phi)
        return self.canvas.create_oval(
            self.earth_center_x - self.earth_radius,
            self.earth_center_y - self.earth_radius,
            self.earth_center_x + self.earth_radius,
            self.earth_center_y + self.earth_radius,
            fill = earth_color,
            outline=""
        )

    def create_trajectory(self):
        """
        Create trajectory oval
        """
        trajectory_color = self.config["trajectory_color"]

        self.physics_engine = PhysicsEngine(self.v, self.r)
        orbital_period = self.physics_engine.get_orbital_period()
        points = []
        for t in np.linspace(0, orbital_period, 40):
            r, phi, _ = self.physics_engine.get_position(t)
            x = r * math.cos(phi)
            y = r * math.sin(phi)
            x_pixels = self.distance_to_pixels(x)
            x_pixels += self.sun_center_x + (self.sun_radius + self.earth_radius) * math.cos(phi)
            y_pixels = self.distance_to_pixels(y)
            y_pixels += self.sun_center_y + (self.sun_radius + self.earth_radius) * math.sin(phi)
            points.append(x_pixels)
            points.append(y_pixels)

        return self.canvas.create_line(
            *points,
            fill=trajectory_color,
            dash=(10, 10),
            smooth=True
        )

    def create_initial_conditions_group(self):
        """
        Create inital conditions control group
        """
        group = ttk.LabelFrame(self.control_panel,
                               text="Initial Conditions", style="Panel.TLabelframe")
        group.pack(pady=(40, 60), padx=10, fill=tk.X)

        # Radius Dial
        frame = ttk.Frame(group)
        frame.pack(fill=tk.X, padx=5, pady=10)
        ttk.Label(frame, text="Start Radius").pack(side=tk.LEFT)
        self.radius_var = tk.StringVar()
        self.radius_var.set(f"{self.r / 1.609344e9} Million Miles")
        ttk.Label(frame, textvariable=self.radius_var, width=15).pack(side=tk.RIGHT)
        self.radius_slider = ttk.Scale(group, from_=30.00, to=100.00,
                                       orient=tk.HORIZONTAL, command=self.set_radius)
        self.radius_slider.pack(fill=tk.X, padx=5, pady=(0, 30))

        # Velocity Dial
        frame = ttk.Frame(group)
        frame.pack(fill=tk.X, padx=5, pady=10)
        ttk.Label(frame, text="Start Velocity").pack(side=tk.LEFT)
        self.velocity_var = tk.StringVar()
        self.velocity_var.set(f"{self.v / 1000} km/s")
        ttk.Label(frame, textvariable=self.velocity_var, width=10).pack(side=tk.RIGHT)
        self.velocity_slider = ttk.Scale(group, from_=28.50, to=35.00,
                                       orient=tk.HORIZONTAL, command=self.set_velocity)
        self.velocity_slider.pack(fill=tk.X, padx=5, pady=(0, 30))


    def set_radius(self, r):
        """
        Set earth radius
        """
        if not self.running and not self.started:
            self.r = float(r) * 1.609344e9
            self.radius_var.set(f"{float(r):.2f} Million Miles")
            self.canvas.delete(self.earth)
            self.earth = self.create_earth(self.r, self.phi, self.v)
            self.canvas.delete(self.trajectory)
            self.trajectory = self.create_trajectory()

    def set_velocity(self, v):
        """
        Set tangential velocity
        """
        if not self.running and not self.started:
            self.velocity_var.set(f"{float(v):.2f} km/s")
            self.v = float(v) * 1000
            self.delete_velocity_vector(self.velocity_vector)
            self.velocity_vector = self.build_velocity_vector(self.v, self.phi)
            self.canvas.delete(self.trajectory)
            self.trajectory = self.create_trajectory()

    def build_velocity_vector(self, v, phi):
        """
        Creative velocity vector for given 
        """
        color = self.config["velocity_vector_color"]

        x1 = self.earth_center_x + self.earth_radius * math.cos(phi)
        y1 = self.earth_center_y + self.earth_radius * math.sin(phi)
        magnitude = v // 1000
        velocity_angle = phi + math.pi/2
        x2 = x1 + magnitude * math.cos(velocity_angle)
        y2 = y1 + magnitude* math.sin(velocity_angle)

        arrowhead_angle = math.pi / 6
        arrowhead_length = 5
        ax1 = x2 - arrowhead_length * math.cos(velocity_angle - arrowhead_angle)
        ay1 = y2 - arrowhead_length * math.sin(velocity_angle - arrowhead_angle)
        ax2 = x2 - arrowhead_length * math.cos(velocity_angle + arrowhead_angle)
        ay2 = y2 - arrowhead_length * math.sin(velocity_angle + arrowhead_angle)

        return {
            "line" : self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2),
            "arrowhead" : self.canvas.create_line(
                x2, y2, ax1, ay1, x2, y2, ax2, ay2, fill=color, width=2
            )
        }

    def delete_velocity_vector(self, vector):
        """
        Delete velocity vector
        """
        for item in vector.values():
            self.canvas.delete(item)

    def distance_to_pixels(self, distance):
        """
        Convert millions of miles to pixels
        Max distance of 300 mil miles maps to 450 pixels
        """
        distance /= 1.609344e9
        max_pixels = 450
        max_dist = 300
        return (distance * max_pixels) // max_dist

    def create_buttons(self):
        """
        Create start, stop and reset buttons
        """
        button_frame = ttk.LabelFrame(self.control_panel, text="Simulation Controls")
        button_frame.pack(pady=(60, 40), padx=10, fill=tk.X)

        # Start Button
        start_button = ttk.Button(
            button_frame,
            text="Start",
            command=self.start_simulation
        )
        start_button.pack(pady=20, padx=10, fill=tk.X)

        # Stop Button
        stop_button = ttk.Button(
            button_frame,
            text="Stop",
            command=self.stop_simulation
        )
        stop_button.pack(pady=20, padx=10, fill=tk.X)

        # Reset Button
        reset_button = ttk.Button(
            button_frame,
            text="Reset",
            command=self.reset_simulation
        )
        reset_button.pack(pady=20, padx=10, fill=tk.X)

    def start_simulation(self):
        """
        Start simulation
        """
        self.running = True
        self.started = True
        self.time_step = self.physics_engine.get_orbital_period()
        self.time_step /= (self.frame_rate * self.orbit_duration)
        self.animate()

    def stop_simulation(self):
        """
        Stop simulation
        """
        self.running = False

    def reset_simulation(self):
        """
        Reset simulation to original state
        """
        self.running = False
        self.started = False
        self.time_ellapsed = 0
        self.v = 1000 * self.config["default_velocity"]
        self.velocity_var.set(f"{self.v / 1000} km/s")
        self.r = self.config["earth_distance"] * 1.609344e9
        self.radius_var.set(f"{self.r / 1.609344e9} Million Miles")
        self.phi = 0
        self.canvas.delete(self.earth)
        self.delete_velocity_vector(self.velocity_vector)
        self.canvas.delete(self.trajectory)
        self.earth = self.create_earth(self.r, self.phi, self.v)
        self.trajectory = self.create_trajectory()

    def animate(self):
        """
        Animate simulation
        """
        if self.running:
            self.time_ellapsed += self.time_step
            self.r, self.phi, self.v = self.physics_engine.get_position(self.time_ellapsed)
            self.radius_var.set(f"{round(self.r / 1.609344e9, 2)} Million Miles")
            self.velocity_var.set(f"{round(self.v / 1000, 2)} km/s")
            self.canvas.delete(self.earth)
            self.delete_velocity_vector(self.velocity_vector)
            self.earth = self.create_earth(self.r, self.phi, self.v)
            self.root.after(self.animation_delay, self.animate)
