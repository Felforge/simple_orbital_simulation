import math
import tkinter as tk
from tkinter import ttk
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
        self.start_status = False
        self.phi = 0
        self.velocity_vector = None

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

        self.v = 1000* self.config["default_velocity"] # Kilometers per Second
        self.theta = math.radians(self.config["default_velocity_angle"])

        self.r = self.config["earth_distance"] # Millions of Miles
        self.create_earth(self.r, self.phi)

        title_label = ttk.Label(
            self.control_panel,
            text="Controls",
            font=('Arial', 20, 'bold')
        )
        title_label.pack(pady=(0, 10))

        self.create_initial_conditions_group()

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

    def create_earth(self, r, phi):
        """
        Generates earth at distance r and angle phi
        """
        earth_color = self.config["earth_color"]
        r_x = r * math.cos(phi)
        r_y = r * math.sin(phi)
        self.earth_radius = self.config["earth_radius"]
        self.earth_center_x = self.sun_center_x + self.miles_to_pixels(r_x)
        self.earth_center_y = self.sun_center_y + self.miles_to_pixels(r_y)
        if self.earth_center_x > self.sun_center_x:
            self.earth_center_x += self.sun_radius + self.earth_radius
        elif self.earth_center_x < self.sun_center_x:
            self.earth_center_x -= self.sun_radius + self.earth_radius
        if self.earth_center_y > self.sun_center_y:
            self.earth_center_y += self.sun_radius + self.earth_radius
        elif self.earth_center_y < self.sun_center_y:
            self.earth_center_y -= self.sun_radius + self.earth_radius
        self.earth = self.canvas.create_oval(
            self.earth_center_x - self.earth_radius,
            self.earth_center_y - self.earth_radius,
            self.earth_center_x + self.earth_radius,
            self.earth_center_y + self.earth_radius,
            fill = earth_color,
            outline=""
        )
        if self.velocity_vector is not None:
            self.delete_velocity_vector(self.velocity_vector)
        self.velocity_vector = self.build_velocity_vector(self.v, self.theta, phi)
        
    def create_trajectory(self):
        """
        Create trajectory oval
        """

    def create_initial_conditions_group(self):
        """
        Create inital conditions control group
        """
        group = ttk.LabelFrame(self.control_panel, 
                               text="Initial Conditions", style="Panel.TLabelframe")
        group.pack(pady=(0, 10), padx=10, fill=tk.X)

        # Radius Dial
        frame = ttk.Frame(group)
        frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(frame, text="Start Radius").pack(side=tk.LEFT)
        self.radius_var = tk.StringVar()
        self.radius_var.set(f"{self.r} Million Miles")
        ttk.Label(frame, textvariable=self.radius_var, width=15).pack(side=tk.RIGHT)
        self.radius_slider = ttk.Scale(group, from_=10.00, to=300.00, 
                                       orient=tk.HORIZONTAL, command=self.set_radius)
        self.radius_slider.pack(fill=tk.X, padx=5, pady=(0, 10))

        # Speed Dial
        frame = ttk.Frame(group)
        frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(frame, text="Start Velocity").pack(side=tk.LEFT)
        self.velocity_var = tk.StringVar()
        self.velocity_var.set(f"{float(self.v / 1000):.2f} km/s")
        ttk.Label(frame, textvariable=self.velocity_var, width=10).pack(side=tk.RIGHT)
        self.velocity_slider = ttk.Scale(group, from_=20.00, to=50.00,
                                         orient=tk.HORIZONTAL, command=self.set_velocity)
        self.velocity_slider.pack(fill=tk.X, padx=5, pady=(0, 10))

        # Angle Dial
        frame = ttk.Frame(group)
        frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(frame, text="Start Angle").pack(side=tk.LEFT)
        self.theta_var = tk.StringVar()
        self.theta_var.set(f"{float(math.degrees(self.theta)):.1f} degrees")
        ttk.Label(frame, textvariable=self.theta_var, width=10).pack(side=tk.RIGHT)
        self.theta_slider = ttk.Scale(group, from_=0.0, to=360.0,
                                         orient=tk.HORIZONTAL, command=self.set_theta)
        self.theta_slider.pack(fill=tk.X, padx=5, pady=(0, 10))

    def set_radius(self, r):
        """
        Set earth radius
        """
        self.r = float(r) * 1.609344e9
        self.radius_var.set(f"{float(r):.2f} Million Miles")
        self.canvas.delete(self.earth)
        self.create_earth(float(r), self.phi)

    def set_velocity(self, v):
        """
        Set tangential velocity
        """
        self.velocity_var.set(f"{float(v):.2f} km/s")
        self.v = float(v) * 1000
        self.delete_velocity_vector(self.velocity_vector)
        self.velocity_vector = self.build_velocity_vector(self.v, self.theta, self.phi)

    def set_theta(self, theta):
        """
        Set theta angle of velocity vector
        """
        self.theta_var.set(f"{float(theta):.1f} degrees")
        self.theta = math.radians(float(theta))
        self.delete_velocity_vector(self.velocity_vector)
        self.velocity_vector = self.build_velocity_vector(self.v, self.theta, self.phi)

    def build_velocity_vector(self, v, theta, phi):
        """
        Creative velocity vector for given 
        """
        color = self.config["velocity_vector_color"]

        x1 = self.earth_center_x + self.earth_radius * math.cos(phi)
        y1 = self.earth_center_y + self.earth_radius * math.sin(phi)
        magnitude = v // 1000
        zero_angle = theta - math.pi / 2
        x2 = x1 + magnitude * math.cos(zero_angle)
        y2 = y1 + magnitude* math.sin(zero_angle)

        arrowhead_angle = math.pi / 6
        arrowhead_length = 5
        ax1 = x2 - arrowhead_length * math.cos(zero_angle - arrowhead_angle)
        ay1 = y2 - arrowhead_length * math.sin(zero_angle - arrowhead_angle)
        ax2 = x2 - arrowhead_length * math.cos(zero_angle + arrowhead_angle)
        ay2 = y2 - arrowhead_length * math.sin(zero_angle + arrowhead_angle)

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
            
    def miles_to_pixels(self, miles):
        """
        Convert millions of miles to pixels
        Max distance of 300 mil miles maps to 450 pixels
        """
        max_pixels = 450
        max_dist = 300
        return (miles * max_pixels) // max_dist
