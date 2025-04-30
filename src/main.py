import tkinter as tk
from tkinter import messagebox, ttk, font
import matplotlib.pyplot as plt
import numpy as np
import random
import math


def calc_temp(iteration, initial_temp):
    return initial_temp/math.log10(iteration + 2)


class VRPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vehicle Routing Problem Solver")
        
        window_width = 1000
        window_height = 700
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        self.cities = [(300, 300)]
        self.capacities = [0]
        self.iteration = 0
        self.best_routes = []
        self.best_distance = float('inf')
        self.current_routes = []
        self.current_distance = 0
        
        self.initial_temp = 1000
        self.cooling_rate = 0.995
        self.temp = self.initial_temp
        self.num_vehicles = 3
        self.truck_capacity = 10
        
        self.temperatures = []
        self.distances = []
        self.current_distances = []
        
        self.create_ui()
        
    def create_ui(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.notebook = ttk.Notebook(self.main_frame)
        
        self.setup_tab = ttk.Frame(self.notebook)
        self.simulation_tab = ttk.Frame(self.notebook)
        self.results_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.setup_tab, text="1. Setup")
        self.notebook.add(self.simulation_tab, text="2. Simulation")
        self.notebook.add(self.results_tab, text="3. Results")
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        self.setup_config_tab()
        
        self.setup_simulation_tab()
        
        self.setup_results_tab()
        
    def setup_config_tab(self):
        config_frame = ttk.LabelFrame(self.setup_tab, text="Configuration")
        config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(config_frame, text="Number of trucks:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.truck_number_var = tk.StringVar(value="3")
        ttk.Entry(config_frame, textvariable=self.truck_number_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(config_frame, text="Truck capacity:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.truck_capacity_var = tk.StringVar(value="10")
        ttk.Entry(config_frame, textvariable=self.truck_capacity_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(config_frame, text="Initial temperature:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.initial_temp_var = tk.StringVar(value="1000")
        ttk.Entry(config_frame, textvariable=self.initial_temp_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(config_frame, text="Cooling rate:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.cooling_rate_var = tk.StringVar(value="0.995")
        ttk.Entry(config_frame, textvariable=self.cooling_rate_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Button(config_frame, text="Apply Configuration", command=self.apply_configuration).grid(row=4, column=0, columnspan=2, padx=10, pady=10)
        
        instruction_frame = ttk.LabelFrame(self.setup_tab, text="Instructions")
        instruction_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        instructions = (
            "1. Set the number of trucks and their capacity\n"
            "2. Click 'Apply Configuration'\n"
            "3. Go to the 'Simulation' tab to add cities and run the algorithm\n"
            "4. Add cities by clicking on the map and setting their demand\n"
            "5. Run the simulation to optimize routes"
        )
        ttk.Label(instruction_frame, text=instructions, justify=tk.LEFT).pack(padx=10, pady=10)
        
    def setup_simulation_tab(self):
        self.simulation_frame = ttk.Frame(self.simulation_tab)
        self.simulation_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas_frame = ttk.LabelFrame(self.simulation_frame, text="Map")
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, width=600, height=600, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas.bind("<Button-1>", self.canvas_click)
        
        self.control_frame = ttk.LabelFrame(self.simulation_frame, text="Controls")
        self.control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        
        city_frame = ttk.LabelFrame(self.control_frame, text="Add Cities")
        city_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(city_frame, text="City demand:").pack(anchor=tk.W, padx=5, pady=2)
        self.capacity_var = tk.StringVar(value="2")
        ttk.Entry(city_frame, textvariable=self.capacity_var, width=10).pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(city_frame, text="Click on the map to place a city").pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Separator(self.control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=10)
        
        sim_frame = ttk.LabelFrame(self.control_frame, text="Simulation")
        sim_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(sim_frame, text="Initialize Solution", command=self.initialize_solution).pack(fill=tk.X, padx=5, pady=3)
        ttk.Button(sim_frame, text="Next Iteration", command=self.next_iteration).pack(fill=tk.X, padx=5, pady=3)
        ttk.Button(sim_frame, text="Run 100 Iterations", command=self.next_100_iteration).pack(fill=tk.X, padx=5, pady=3)
        
        ttk.Separator(self.control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=10)
        
        self.status_frame = ttk.LabelFrame(self.control_frame, text="Status")
        self.status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_text = tk.Text(self.status_frame, height=10, width=30, wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Button(self.control_frame, text="Reset", command=self.reset_simulation).pack(fill=tk.X, padx=5, pady=10)
        
        self.update_canvas()
        self.update_status()
        
    def setup_results_tab(self):
        results_frame = ttk.Frame(self.results_tab)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Button(results_frame, text="Plot Temperature & Distance", command=self.plot_decay).pack(pady=10)
        
        self.results_text = tk.Text(results_frame, height=20, width=50, wrap=tk.WORD, state=tk.DISABLED)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def apply_configuration(self):
        try:
            self.num_vehicles = int(self.truck_number_var.get())
            self.truck_capacity = int(self.truck_capacity_var.get())
            self.initial_temp = float(self.initial_temp_var.get())
            self.cooling_rate = float(self.cooling_rate_var.get())
            self.temp = self.initial_temp
            
            self.update_status()
            messagebox.showinfo("Configuration Applied", 
                               f"Configuration set to:\n"
                               f"Number of trucks: {self.num_vehicles}\n"
                               f"Truck capacity: {self.truck_capacity}\n"
                               f"Initial temperature: {self.initial_temp}\n"
                               f"Cooling rate: {self.cooling_rate}")
            
            self.notebook.select(1)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for all configuration values.")
    
    def canvas_click(self, event):
        if len(self.cities) > 1 and self.iteration > 0:
            messagebox.showinfo("Simulation in progress", 
                              "Simulation has already started. Reset to add more cities.")
            return
            
        x, y = event.x, event.y
        
        try:
            capacity = int(self.capacity_var.get())
        except ValueError:
            capacity = 2
            self.capacity_var.set("2")
            
        if sum(self.capacities) + capacity > (self.truck_capacity * self.num_vehicles):
            messagebox.showerror("Demand Overload", "The total demand would exceed the capacity of all trucks.")
            return
            
        self.cities.append((x, y))
        self.capacities.append(capacity)
        
        self.update_canvas()
        self.update_status()
    
    def update_canvas(self):
        self.canvas.delete("all")
        
        depot = self.cities[0]
        self.canvas.create_oval(depot[0] - 9, depot[1] - 9, depot[0] + 9, depot[1] + 9, fill='red', outline='black')
        self.canvas.create_text(depot[0], depot[1] - 15, text="Depot", font=('Arial', 10))
        
        for i in range(1, len(self.cities)):
            city = self.cities[i]
            self.canvas.create_oval(city[0] - 6, city[1] - 6, city[0] + 6, city[1] + 6, fill='lightblue', outline='black')
            self.canvas.create_text(city[0], city[1] - 12, text=f"D:{self.capacities[i]}", font=('Arial', 8))
        
        if self.current_routes:
            self.plot_routes(self.current_routes)
    
    def update_status(self):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        
        best_distance_str = "N/A" if self.best_distance == float('inf') else f"{self.best_distance:.2f}"
        status = (
            f"Trucks: {self.num_vehicles}\n"
            f"Capacity per truck: {self.truck_capacity}\n"
            f"Cities: {len(self.cities) - 1}\n"
            f"Total demand: {sum(self.capacities)}\n"
            f"Iteration: {self.iteration}\n"
            f"Temperature: {self.temp:.2f}\n"
            f"Best distance: {best_distance_str}\n"
        )
        
        self.status_text.insert(tk.END, status)
        self.status_text.config(state=tk.DISABLED)
        
        if self.iteration > 0:
            self.update_results()
    
    def update_results(self):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        results = f"Best solution found at iteration {self.iteration}:\n\n"
        results += f"Total distance: {self.best_distance:.2f}\n\n"
        
        for i, route in enumerate(self.best_routes):
            if route:
                route_demand = sum(self.capacities[city] for city in route)
                results += f"Truck {i+1} (Capacity used: {route_demand}/{self.truck_capacity}):\n"
                path = ["Depot"] + [f"City {city}" for city in route] + ["Depot"]
                results += " → ".join(path) + "\n\n"
            else:
                results += f"Truck {i+1}: Not used\n\n"
        
        self.results_text.insert(tk.END, results)
        self.results_text.config(state=tk.DISABLED)
    
    def initialize_solution(self):
        if len(self.cities) <= 1:
            messagebox.showerror("Not enough cities", "Please add at least one city before starting the simulation.")
            return
            
        self.iteration = 0
        self.current_routes = self.initial_solution()
        self.current_distance = self.total_distance(self.current_routes)
        self.best_routes = [route[:] for route in self.current_routes]
        self.best_distance = self.current_distance
        
        self.temperatures = []
        self.distances = []
        self.current_distances = []
        
        self.update_canvas()
        self.update_status()
        messagebox.showinfo("Initialization Complete", "Initial solution generated. You can now run iterations.")
    
    def reset_simulation(self):
        if messagebox.askyesno("Reset Confirmation", "Are you sure you want to reset the simulation? All cities will be removed except the depot."):
            self.cities = [self.cities[0]]
            self.capacities = [0]
            self.iteration = 0
            self.current_routes = []
            self.best_routes = []
            self.current_distance = 0
            self.best_distance = float('inf')
            self.temp = self.initial_temp
            self.temperatures = []
            self.distances = []
            self.current_distances = []
            
            self.update_canvas()
            self.update_status()

    def distance(self, city1, city2):
        return np.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)
        
    def total_distance(self, routes):
        distance = 0
        for route in routes:
            if len(route) > 1:
                distance += self.distance(self.cities[0], self.cities[route[0]])
                for i in range(1, len(route)):
                    distance += self.distance(self.cities[route[i - 1]], self.cities[route[i]])
                distance += self.distance(self.cities[route[-1]], self.cities[0])
        return distance
        
    def initial_solution(self):
        indices = list(range(1, len(self.cities)))
        random.shuffle(indices)
        routes = [[] for _ in range(self.num_vehicles)]
        capacities_used = [0] * self.num_vehicles

        for city in indices:
            capacity = self.capacities[city]
            for i in range(self.num_vehicles):
                if capacities_used[i] + capacity <= self.truck_capacity:
                    routes[i].append(city)
                    capacities_used[i] += capacity
                    break

        return routes
        
    def neighbor_solution(self, routes):
        new_routes = [route[:] for route in routes]
        route1, route2 = random.sample(range(len(new_routes)), 2)

        if new_routes[route1] and new_routes[route2]:
            city1 = random.choice(new_routes[route1])
            city2 = random.choice(new_routes[route2])

            route1_capacity = sum(self.capacities[city] for city in new_routes[route1]) - self.capacities[city1] + \
                              self.capacities[city2]
            route2_capacity = sum(self.capacities[city] for city in new_routes[route2]) - self.capacities[city2] + \
                              self.capacities[city1]

            if route1_capacity <= self.truck_capacity and route2_capacity <= self.truck_capacity:
                index1 = new_routes[route1].index(city1)
                index2 = new_routes[route2].index(city2)
                new_routes[route1][index1], new_routes[route2][index2] = new_routes[route2][index2], new_routes[route1][
                    index1]

        return new_routes
        
    def simulated_annealing(self):
        if not self.cities or len(self.cities) <= 1:
            messagebox.showerror("Invalid Input", "Please add cities before running the simulation")
            return

        if self.iteration == 0:
            self.current_routes = self.initial_solution()
            self.current_distance = self.total_distance(self.current_routes)
            self.best_routes = [route[:] for route in self.current_routes]
            self.best_distance = self.current_distance

        new_routes = self.neighbor_solution(self.current_routes)
        new_distance = self.total_distance(new_routes)
        delta_d = new_distance - self.current_distance
        
        if delta_d < 0 or random.random() < math.exp(-delta_d / self.temp):
            self.current_routes = new_routes
            self.current_distance = new_distance
            if new_distance < self.best_distance:
                self.best_routes = [route[:] for route in new_routes]
                self.best_distance = new_distance

        self.temp *= self.cooling_rate
        self.iteration += 1

        self.temperatures.append(self.temp)
        self.distances.append(self.best_distance)
        self.current_distances.append(self.current_distance)

        self.update_canvas()
        self.update_status()

    def next_100_iteration(self):
        if not self.current_routes and self.iteration == 0:
            self.initialize_solution()
            
        for i in range(100):
            self.simulated_annealing()

    def next_iteration(self):
        if not self.current_routes and self.iteration == 0:
            self.initialize_solution()
        else:
            self.simulated_annealing()

    def plot_routes(self, routes):
        depot = self.cities[0]
        
        for i, route in enumerate(routes):
            if not route:
                continue
                
            color = plt.cm.tab10(i % 10)
            color = f'#{int(color[0] * 255):02x}{int(color[1] * 255):02x}{int(color[2] * 255):02x}'
            
            if route:
                first_city = self.cities[route[0]]
                self.canvas.create_line(depot[0], depot[1], first_city[0], first_city[1], 
                                       fill=color, width=2, arrow=tk.LAST)
            
            for j in range(len(route) - 1):
                city1 = self.cities[route[j]]
                city2 = self.cities[route[j + 1]]
                self.canvas.create_line(city1[0], city1[1], city2[0], city2[1], 
                                       fill=color, width=2, arrow=tk.LAST)
            
            if route:
                last_city = self.cities[route[-1]]
                self.canvas.create_line(last_city[0], last_city[1], depot[0], depot[1], 
                                       fill=color, width=2, arrow=tk.LAST)
                
            if route:
                label_x = (depot[0] + self.cities[route[0]][0]) / 2
                label_y = (depot[1] + self.cities[route[0]][1]) / 2
                self.canvas.create_oval(label_x-8, label_y-8, label_x+8, label_y+8, fill=color, outline='black')
                self.canvas.create_text(label_x, label_y, text=str(i+1), fill='white')

    def plot_decay(self):
        fig, axs = plt.subplots(2, figsize=(10, 8))

        axs[0].plot(range(len(self.temperatures)), self.temperatures, label='Temperature', markersize=3)
        axs[0].set_title('Temperature Decay')
        axs[0].set_xlabel('Iteration')
        axs[0].set_ylabel('Temperature')
        axs[0].legend()

        axs[1].plot(range(len(self.distances)), self.distances, label='Best Distance', color='r',
                    linewidth=3, zorder=3)
        axs[1].plot(range(len(self.current_distances)), self.current_distances, label='Current Distance', color='b',
                    alpha=0.5)
        axs[1].set_title('Best and Current Distance over Iterations')
        axs[1].set_xlabel('Iteration')
        axs[1].set_ylabel('Distance')
        axs[1].legend()

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = VRPApp(root)
    root.mainloop()
