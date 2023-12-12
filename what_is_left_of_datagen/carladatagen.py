import carla
import random
import math
import time
import os
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import clear_output
import subprocess
import traceback 
import psutil
import fnmatch

port = random.randint(2000,6000)
port = 2000
print(f"choosing port {port}")

cameradone = False
def process_img(image):
    i = np.array(image.raw_data)
    i2 = i.reshape((image.height, image.width, 4))
    i3 = i2[:, :, :3]
    return i3

def check_if_image_already_exists(vehicle_id, angle, height, pitch, distance,left_shift, color):
    return os.path.exists(f'D:/SelfDrivingImages/{vehicle_id}/ang{angle}h{height}p{pitch}dist{distance}lshift{left_shift}color{color}.png')

def capture_image(image, vehicle_id, angle, height, pitch, distance, left_shift, cam):
    try:
        image.save_to_disk(f'D:/SelfDrivingImages/{vehicle_id}/ang{angle}h{height}p{pitch}dist{distance}lshift{left_shift}color{color}.png')
        cam.destroy()
    except FileNotFoundError as e:
        print("FileNotFoundError:", e)
    except IOError as e:
        print("IOError:", e)
    except Exception as e:  # Catch any other exceptions
        print("An error occurred in capture_image:", e)
        traceback.print_exc()  # Print detailed traceback
    global cameradone
    cameradone= True

def check_vehicle(vehicle):
    return "volkswagen" in vehicle or "audi" in vehicle


def get_camera_transform(vehicle_transform, angle, distance, height, pitch, left_shift=0):
    # Convert angle to radians
    angle_rad = math.radians(angle)

    # Original location calculation
    location = vehicle_transform.location
    x = location.x + distance * math.cos(angle_rad)
    y = location.y + distance * math.sin(angle_rad)
    z = height

    # Calculate camera direction vector
    direction = carla.Location(location.x - x, location.y - y, location.z - z)

    # Calculate the perpendicular vector for left shift
    # It's perpendicular to the direction in which the camera is looking
    left_shift_vector = carla.Location(-direction.y, direction.x, 0)

    # Normalize the left_shift_vector and apply the shift
    magnitude = math.sqrt(left_shift_vector.x**2 + left_shift_vector.y**2)
    left_shift_vector.x = (left_shift_vector.x / magnitude) * left_shift
    left_shift_vector.y = (left_shift_vector.y / magnitude) * left_shift

    # Apply the left shift to x and y
    x += left_shift_vector.x
    y += left_shift_vector.y

    # Calculate yaw from the direction vector
    yaw = math.degrees(math.atan2(direction.y, direction.x))

    # Return the new transform with the left shift applied
    return carla.Transform(carla.Location(x=x, y=y, z=z), carla.Rotation(pitch=pitch, yaw=yaw))

PROCNAME = "CarlaUE4.exe"
for proc in psutil.process_iter():
    if(proc.name() == PROCNAME):
        proc.kill()
subprocess.Popen(["D:/WindowsNoEditor/CarlaUE4.exe", "-quality-level=Low", "-carla-port=" + str(port)])

time.sleep(15)

try:
    client = carla.Client('127.0.0.1', port)
    client.set_timeout(10.0)
    world = client.get_world()

    for vehicle in world.get_actors().filter('*vehicle*'):
        print("yeye")
        vehicle.destroy()

    #vehicle_blueprints = world.get_blueprint_library().filter('vehicle.*')
    camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
    camera_bp.set_attribute('image_size_x', str(800 - (800 % 64)))  # 800 is the nearest multiple of 64
    camera_bp.set_attribute('image_size_y', str(600 - (600 % 64)))  # 600 is the nearest multiple of 64
    camera_bp.set_attribute('fov', '90')

    #vehicle_bp = random.choice(vehicle_blueprints)

    spawn_point = world.get_map().get_spawn_points()[4]

    vehiclelist = []
    colorlist = ["255,0,0", "0,255,0", "0,0,255", "0,255,255", "255,0,255", "255,255,0", "255,255,255", "0,0,0"]

    filter_patterns = ["vehicle.audi.*", "vehicle.volkswagen.*", ]
    # Filter blueprints
    filtered_blueprints = []
    for blueprint in world.get_blueprint_library():
        if any(fnmatch.fnmatch(blueprint.id, pattern) for pattern in filter_patterns):
            filtered_blueprints.append(blueprint)

    for vehiclebp in filtered_blueprints:
        for color in colorlist:
            vehiclebp.set_attribute('color', color)
            vehicle = world.spawn_actor(vehiclebp, spawn_point)


            for angle in [0,30,60,90, 120, 150, 180, 210, 240,270,300,330,360]:#range(0, 361,30):# 18):  # Adjust angle steps as needed
                for height in [2, 5]:  # Vary height
                    for distance in [6,10]:  # Vary distance
                        for pitch in [-30,-20,-10]:
                            for left_shift in [-3, 0, 3]:
                            
                                #for weather in weathers:
                                    #world.set_weather(weather)
                                if(not check_if_image_already_exists( vehicle.type_id, angle, height, pitch, distance, left_shift, color)):
                                    camera_transform = get_camera_transform(vehicle.get_transform(), angle, distance, height, pitch, left_shift)
                                    camera = world.spawn_actor(camera_bp, camera_transform)
                                    camera.listen(lambda image: capture_image(image, vehicle.type_id, angle, height, pitch, distance,left_shift, camera))
                                    # while not cameradone:
                                    #     time.sleep(0.001)
                                    # cameradone = False
                                    time.sleep(0.26)  # Adjust sleep time as needed
            print("finished")
            vehicle.destroy()
except ConnectionError as e:
    print("ConnectionError:", e)
except TimeoutError as e:
    print("TimeoutError:", e)
except Exception as e:  # Catch any other exceptions not caught above
    print("An error occurred in the main loop:", e)
    traceback.print_exc()  # Print detailed traceback
    