import json

with open("coordinates.json", "r", encoding="utf-8") as file:
    coordinates = json.load(file)

x_coords = [coord[0] for coord in coordinates]
y_coords = [coord[1] for coord in coordinates]

for x in x_coords:
    if x > -1000:
        print(x)

# with open("areas_coordinates.json", "w", encoding="utf-8") as file:
#     area_name = "b_site"
#     data = {
#         "area_name": area_name,
#         "coordinates": [(x, y) for x, y in zip(x_coords, y_coords)]
#     }
    
#     json.dump(data, file)
with open("areas_coordinates.json", "r", encoding="utf-8") as file:
    data = json.load(file)



new_data = {
    "area_name": "sand_land",
    "coordinates": [(x, y) for x, y in zip(x_coords, y_coords)]
}

data.append(new_data)

with open("areas_coordinates.json", "w", encoding="utf-8") as file:
    json.dump(data, file)









