import tkinter as tk
from tkinter import filedialog, messagebox
import geopandas as gpd
import folium
import json
import math
import numpy as np
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.geometry.polygon import Polygon as ShapelyPolygon

r_earth = 6371000  # Earth radius in meters

# Convert meters to degrees of latitude and longitude
# As long as dx and dy are small compared to the radius of the earth and you don't get too close to the poles.
def meters_to_degrees(meters, latitude):
    degrees_lat = (meters / r_earth) * (180.0 / math.pi)
    degrees_lon = (meters / r_earth) * (180.0 / math.pi) / math.cos(latitude * math.pi / 180.0)
    return degrees_lat, degrees_lon

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QGroundControl Plan Generator")
        self.create_widgets()
    
    def create_widgets(self):
        tk.Label(self, text="GeoJSON File:").grid(row=0, column=0, padx=10, pady=5)
        self.file_path_entry = tk.Entry(self, width=50)
        self.file_path_entry.grid(row=0, column=1, padx=10, pady=5)
        tk.Button(self, text="Browse", command=self.open_file_dialog).grid(row=0, column=2, padx=10, pady=5)

        tk.Label(self, text="Home Position Latitude:").grid(row=1, column=0, padx=10, pady=5)
        self.home_lat_entry = tk.Entry(self)
        self.home_lat_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self, text="Home Position Longitude:").grid(row=2, column=0, padx=10, pady=5)
        self.home_lon_entry = tk.Entry(self)
        self.home_lon_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self, text="Home Position Altitude:").grid(row=3, column=0, padx=10, pady=5)
        self.home_alt_entry = tk.Entry(self)
        self.home_alt_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(self, text="Mission Altitude (m):").grid(row=4, column=0, padx=10, pady=5)
        self.altitude_entry = tk.Entry(self)
        self.altitude_entry.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(self, text="Spraying Diameter (m):").grid(row=5, column=0, padx=10, pady=5)
        self.spraying_diameter_entry = tk.Entry(self)
        self.spraying_diameter_entry.grid(row=5, column=1, padx=10, pady=5)

        tk.Button(self, text="Generate Plan", command=self.generate_plan).grid(row=6, column=1, padx=10, pady=20)

    def open_file_dialog(self):
        file_path = filedialog.askopenfilename(filetypes=[("GeoJSON files", "*.geojson")])
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)
    
    def generate_plan(self):
        file_path = self.file_path_entry.get()
        home_lat = float(self.home_lat_entry.get())
        home_lon = float(self.home_lon_entry.get())
        home_alt = float(self.home_alt_entry.get())
        altitude = float(self.altitude_entry.get())
        spraying_diameter_meters = float(self.spraying_diameter_entry.get())
        
        home_position = [home_lat, home_lon, home_alt]
        
        self.create_qgroundcontrol_plan(file_path, home_position, altitude, spraying_diameter_meters)

    def create_qgroundcontrol_plan(self, file_path, home_position, altitude, spraying_diameter_meters):
        # Read the GeoJSON file
        gdf = gpd.read_file(file_path)
        
        # Extract coordinates from all geometries
        all_coords = []
        for geom in gdf.geometry:
            all_coords.extend(self.extract_coordinates(geom, spraying_diameter_meters))
        
        # Create waypoints
        waypoints = []
        for i, (lon, lat) in enumerate(all_coords):
            waypoints.append({
                "type": "SimpleItem",
                "autoContinue": True,
                "coordinate": [lat, lon, altitude],  # Use the altitude input
                "command": 16,  # Command: NAV_WAYPOINT
                "doJumpId": i + 1,
                "frame": 3,  # Frame: MAV_FRAME_GLOBAL_RELATIVE_ALT
                "params": [0, 0, 0, None, lat, lon, altitude]
            })
        
        # Create QGroundControl plan structure
        qgc_plan = {
            "fileType": "Plan",
            "geoFence": {
                "circles": [],
                "polygons": [],
                "version": 2
            },
            "mission": {
                "cruiseSpeed": 15,
                "firmwareType": 12,
                "hoverSpeed": 5,
                "items": waypoints,
                "plannedHomePosition": home_position,  # Use the home position input
                "vehicleType": 2,
                "version": 2
            },
            "rallyPoints": {
                "points": [],
                "version": 2
            },
            "version": 1
        }
        
        # Save to JSON file
        with open('qgroundcontrol_plan.json', 'w') as f:
            json.dump(qgc_plan, f, indent=4)
        
        # Save waypoints to Folium map
        map_center = gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()
        folium_map = folium.Map(location=map_center, zoom_start=13)
        for lat, lon in all_coords:
            folium.Marker(location=[lon, lat], icon=folium.Icon(color='blue')).add_to(folium_map)
        for geom in gdf.geometry:
            folium.GeoJson(geom).add_to(folium_map)
        folium_map.save('waypoints_map.html')
        
        messagebox.showinfo("Success", "QGroundControl plan created successfully!")

    def extract_coordinates(self, geometry, spraying_diameter_meters):
        if geometry.geom_type == 'Point':
            return [geometry.coords[0]]
        elif geometry.geom_type == 'Polygon':
            return self.generate_waypoints_within_polygon(geometry, spraying_diameter_meters)
        elif geometry.geom_type == 'MultiPolygon':
            coords = []
            for polygon in geometry:
                coords.extend(self.generate_waypoints_within_polygon(polygon, spraying_diameter_meters))
            return coords
        else:
            raise ValueError(f"Unsupported geometry type: {geometry.geom_type}")

    def generate_waypoints_within_polygon(self, polygon: ShapelyPolygon, spraying_diameter_meters: float) -> list:
        # Get bounds of the polygon
        minx, miny, maxx, maxy = polygon.bounds
        
        # Approximate latitude for conversion purposes (use the midpoint)
        mid_lat = (miny + maxy) / 2
        
        # Convert spraying diameter to degrees
        spacing_lat, spacing_lon = meters_to_degrees(spraying_diameter_meters, mid_lat)
        
        # Generate grid points
        x_coords = np.arange(minx + spacing_lon / 2, maxx, spacing_lon)
        y_coords = np.arange(miny + spacing_lat / 2, maxy, spacing_lat)
        grid_points = [Point(x, y) for x in x_coords for y in y_coords]
        
        # Filter points based on the overlap condition
        waypoints = []
        for point in grid_points:
            circle = point.buffer(spacing_lon / 2)  # Use longitude degrees for buffer
            intersection_area = polygon.intersection(circle).area
            circle_area = circle.area
            
            # Check if the intersection area is more than 50% of the circle area
            if intersection_area / circle_area > 0.5:
                waypoints.append(point)
        
        # If no waypoints or spraying diameter is larger than the polygon, use the centroid
        if not waypoints:
            waypoints = [polygon.centroid]
        
        # Convert waypoints to coordinates
        waypoint_coords = [(point.x, point.y) for point in waypoints]
        
        return waypoint_coords

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
