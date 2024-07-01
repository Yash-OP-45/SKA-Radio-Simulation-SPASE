import folium
import os

map = folium.Map(location=[45.5236, -122.6750])
map.save('map.html')
cwd = os.getcwd()
print(f"Current working directory: {cwd}")
# Save the map to the current working directory
map_path = os.path.join(cwd, 'map.html')
map.save(map_path)
print(f"Map saved to: {map_path}")