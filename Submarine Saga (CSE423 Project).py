# OpenGL Imports
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Standard Library Imports
import math
import time
import random
import ctypes
from math import tan, pi

# Window Dimensions
W_Width, W_Height = 1366, 768

# Constants
GLUT_BITMAP_HELVETICA_18 = ctypes.c_void_p(int(5))

# Game States
game_over = False
paused = False
restart_game = False
background_update_needed = False

# Timing
start_time1 = time.time()
start_time2 = time.time() + 3
tor_time1 = time.time() - 2
tor_time2 = time.time() - 2
last_update = time.time()
last_spawn_time = time.time()
last_spawn_time_shark = time.time()
spawn_interval = 10.0

# Speeds
speed_rain = 6
speed_sub = 20
speed_sub1 = 20
speed_rad = 0.015
speed_tor = 20
fall_speed = 6

# Player, Submarines, and Entities
player = None
submarines = []
bubbles = []
torpedo1 = []
torpedo2 = []
rains = []
sharks = []
unique_circles = []

# Boat and Bombs
boatx = 80
boaty = 233
bombs = [[-boatx + 15, boaty + 20], [-boatx + 55, boaty + 20], [-boatx + 95, boaty + 20], [-boatx + 135, boaty + 20]]
bombN = [True, True, True, True]
theta = random.randrange(-30, 30)
bomb_left = [tan((225 + theta) * (pi / 180)), tan((225 + theta + 20) * (pi / 180))]
bomb_right = [tan((315 + theta) * (pi / 180)), tan((315 + theta + 20) * (pi / 180))]

# Background Colors
background_color = [0.0, 0.5, 1.0]  # Day mode (light blue)
light_water_color = (0.53, 0.81, 0.98)  # Light blue water
bottom_color = (0.36, 0.25, 0.20)  # Brown bottom
raindrop_color = [0.0, 0.0, 1.0]  # Blue raindrops
house_color = [1.0, 1.0, 1.0]
step_size = 0.1

# Submarine 11
list1 = [[-530, 180], [-630, 180], [-630, 130], [-530, 130]]
list2 = [[-660, 165], [-680, 165], [-680, 145], [-660, 145], [-655, 155]]
list3 = [[-550, 200], [-580, 200], [-610, 180], [-550, 180]]
list4 = [[-560, 215], [-570, 215], [-570, 200], [-560, 200]]
list5 = [[-540, 165], [-560, 165], [-560, 145], [-540, 145]]
list6 = [[-570, 130], [-610, 130], [-610, 115], [-570, 115], [-555, 122.5]]
circle1 = [-580, 155]
circle2 = [-615, 155]

# Submarine 22
list11 = [[530, 180], [630, 180], [630, 130], [530, 130]]
list22 = [[660, 165], [680, 165], [680, 145], [660, 145], [655, 155]]
list33 = [[550, 200], [580, 200], [610, 180], [550, 180]]
list44 = [[560, 215], [570, 215], [570, 200], [560, 200]]
list55 = [[540, 165], [560, 165], [560, 145], [540, 145]]
list66 = [[570, 130], [610, 130], [610, 115], [570, 115], [555, 122.5]]
circle11 = [580, 155]
circle22 = [615, 155]

# Background and Pause
background_list = None
pause = None


def convert_coordinate(x, y):
    # Cache these values
    global W_Width, W_Height
    half_width = W_Width // 2
    half_height = W_Height // 2
    return x - half_width, half_height - y

def draw_points(x, y, s):
    glPointSize(s) 
    glBegin(GL_POINTS)
    glVertex2f(x,y) 
    glEnd()
    
def draw_points_batch(points, size):
    glPointSize(size)
    glBegin(GL_POINTS)
    for x, y in points:
        glVertex2f(x, y)
    glEnd()

def draw_lines(color, x1, y1, x2, y2):
    glColor3f(color[0], color[1], color[2])  # Set the color
    zone = findZone(x1, y1, x2, y2)
    
    # Convert coordinates to integers
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    
    x1, y1, x2, y2 = convertToZone0(zone, x1, y1, x2, y2)
    points = MidPointLine(x1, y1, x2, y2)
    convertToZoneM(color, zone, points)
    
def draw_filled_circle(x, y, rad, color):
    glColor3f(color[0], color[1], color[2])
    point = MidPointCircle(rad)
    allpoint = zone_converter(x, y, point)
    for i in allpoint:
        for j in i:
            draw_points(j[0], j[1], 1.2)
    filled_circle_helper(x,y,rad, color)
    
def draw_hollow_circle(x, y, rad, color):
    glColor3f(color[0], color[1], color[2])
    point = MidPointCircle(rad)
    allpoint = zone_converter(x, y, point)

    # Draw hollow circle
    for i in allpoint:
        for j in i:
            draw_points(j[0], j[1], 1.2)  # Draw the outline of the circle
            
def draw_filled_shape(color, vertices):
    glColor3f(*color)
    for i in range(len(vertices)):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % len(vertices)]  # Wrap to the first vertex
        draw_lines(color, x1, y1, x2, y2)  # Use midpoint line algorithm

def fill_rectangle(color, x_min, y_min, x_max, y_max):
    glColor3f(*color)
    step = 2  # Increase step size for fewer points
    points = []
    for y in range(int(y_min), int(y_max) + 1, step):
        for x in range(int(x_min), int(x_max) + 1, step):
            points.append((x, y))
    draw_points_batch(points, 2)  # Increase point size
    
    
##---------------------Midpoint Line Algorithm---------------------------#
def MidPointLine(x1, y1, x2, y2):
    points = []
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * dy - 2 * dx
    x = int(x1)  # Convert to integer
    y = int(y1)  # Convert to integer
    for i in range(x, int(x2) + 1):  # Convert x2 to integer
        points.append([i, y])
        if d > 0:
            d += incNE
            y += 1
        else:
            d += incE
    return points

def findZone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx>0 and dy>=0:
        if abs(dx) > abs(dy):
            return 0
        else:
            return 1
    elif dx<=0 and dy>=0:
        if abs(dx) > abs(dy):
            return 3
        else:
            return 2
    elif dx<0 and dy<0:
        if abs(dx) > abs(dy):
            return 4
        else:
            return 5
    elif dx>=0 and dy<0:
        if abs(dx) > abs(dy):
            return 7
        else:
            return 6
        
def convertToZone0(zone, x1, y1, x2, y2):
    if zone == 1:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    elif zone == 2:
        x1, y1 = y1, -x1
        x2, y2 = y2, -x2
    elif zone == 3:
        x1, y1 = -x1, y1
        x2, y2 = -x2, y2
    elif zone == 4:
        x1, y1 = -x1, -y1
        x2, y2 = -x2, -y2
    elif zone == 5:
        x1, y1 = -y1, -x1
        x2, y2 = -y2, -x2
    elif zone == 6:
        x1, y1 = -y1, x1
        x2, y2 = -y2, x2
    elif zone == 7:
        x1, y1 = x1, -y1
        x2, y2 = x2, -y2
    return x1, y1, x2, y2


def convertToZoneM(color, zone, points):
    s = 2
    glColor3f(color[0], color[1], color[2])
    if zone ==0:
        for x, y in points:
            draw_points(x, y, s)
    elif zone == 1:
        for x, y in points:
            draw_points(y, x, s)
    elif zone == 2:
        for x, y in points:
            draw_points(-y, x, s)
    elif zone == 3:
        for x, y in points:
            draw_points(-x, y, s)
    elif zone == 4:
        for x, y in points:
            draw_points(-x, -y, s)
    elif zone == 5:
        for x, y in points:
            draw_points(-y, -x, s)
    elif zone == 6:
        for x, y in points:
            draw_points(y, -x, s)
    elif zone == 7:
        for x, y in points:
            draw_points(x, -y, s)

#=========================================================================#

#---------------Midpoint Circle Algorithm---------------------------#

def MidPointCircle(rad):
    zone0 = []
    d_init = 1 - rad
    x_temp = 0
    while x_temp < rad :
        if d_init >= 0 :
            d_init = d_init + 2 * x_temp - 2* rad + 5 
            zone0.append((x_temp,rad))
            x_temp+=1
            rad -= 1
        else:
            d_init = d_init + 2 * x_temp +  3 
            zone0.append((x_temp,rad))
            x_temp+=1
    return zone0


def zone_converter(x,y,arr):
    all_points = [[],[],[],[],[],[],[],[]]
    for i in range(0,len(arr)):
        m = arr[i]
        for j in range(8):
            if j == 0 :
                all_points[j].append((m[1]+x,m[0]+y))
            elif j == 1:
                all_points[j].append((m[0]+x,m[1]+y))
            elif j == 2:
                all_points[j].append((-m[0]+x,m[1]+y))
            elif j == 3:
                all_points[j].append((-m[1]+x,m[0]+y))
            elif j == 4:
                all_points[j].append((-m[1]+x,-m[0]+y))
            elif j == 5:
                all_points[j].append((-m[0]+x,-m[1]+y))
            elif j == 6:
                all_points[j].append((m[0]+x,-m[1]+y))
            elif j == 7:
                all_points[j].append((m[1]+x,-m[0]+y))

    return all_points

def filled_circle_helper(x, y, rad, color):
    glColor3f(color[0], color[1], color[2])
    glBegin(GL_POINTS)

    xi, yi = 0, rad
    p = 1 - rad  # Decision parameter

    while xi <= yi:
        # Draw horizontal lines between symmetric points
        for dx in range(-xi, xi + 1):  # Top and bottom horizontal lines
            glVertex2f(x + dx, y + yi)
            glVertex2f(x + dx, y - yi)
        for dx in range(-yi, yi + 1):  # Left and right horizontal lines
            glVertex2f(x + dx, y + xi)
            glVertex2f(x + dx, y - xi)

        xi += 1
        if p < 0:
            p += 2 * xi + 1
        else:
            yi -= 1
            p += 2 * (xi - yi) + 1

    glEnd()
    
#================================================================================#


class Torpedo:
    def __init__(self, points, x, y):
        self.body = points  # List of points defining the torpedo shape
        self.inc_x = x      # Horizontal movement increment
        self.inc_y = y      # Vertical movement increment
        self.active = True   # Status of the torpedo
        
def draw_torpedo(torpedo_list):
    for tor in torpedo_list:
        if tor.active:
            # Define colors
            body_color = (0.0, 0.0, 0.0)  # Gray for the body
            fin_color = (1.0, 0.0, 0.0)   # Red for the fins

            # Draw the body of the torpedo using draw_filled_shape
            draw_filled_shape(body_color, tor.body[:4])  # Main body (first 4 points)
            
            # Draw the tail of the torpedo using draw_filled_shape
            draw_filled_shape(fin_color, [tor.body[3], tor.body[4], tor.body[0]])  # Tail (last 3 points)
            
def update_torpedoes():
    for tor in torpedo1:
        if tor.active:
            for i in range(len(tor.body)):
                tor.body[i][0] += speed_tor  # Horizontal movement
                tor.body[i][1] += tor.inc_y  # Vertical movement
            
            # Recalculate bounding box
            min_x = min(point[0] for point in tor.body)
            max_x = max(point[0] for point in tor.body)
            min_y = min(point[1] for point in tor.body)
            max_y = max(point[1] for point in tor.body)
            box_torpedo = AABB(min_x, min_y, max_x - min_x, max_y - min_y)

            # Check collision with sub22
            box_sub22 = sub22.get_bounding_box()
            
            if has_collided(box_torpedo, box_sub22):
                tor.active = False  # Deactivate torpedo immediately
                if sub22.life > 0:  # Check if life is greater than 0 before decreasing
                    sub22.life -= 1
                if sub22.life == 0:
                    sub22.control = False
                continue  # Skip further checks for this torpedo

            # Circle collision with sub22 front and back
            for circle in [sub22.circle1, sub22.circle2]:
                cx, cy = circle
                circle_radius = 50
                torpedo_radius = 35
                distance = math.sqrt((tor.body[0][0] - cx) ** 2 + (tor.body[0][1] - cy) ** 2)
                if distance <= circle_radius + torpedo_radius:
                    tor.active = False  # Deactivate torpedo immediately
                    if sub22.life > 0:  # Check if life is greater than 0 before decreasing
                        sub22.life -= 1
                    if sub22.life == 0:
                        sub22.control = False
                    break

    for tor in torpedo2:
        if tor.active:
            for i in range(len(tor.body)):
                tor.body[i][0] -= speed_tor
                tor.body[i][1] -= tor.inc_y
            
            # Recalculate bounding box
            min_x = min(point[0] for point in tor.body)
            max_x = max(point[0] for point in tor.body)
            min_y = min(point[1] for point in tor.body)
            max_y = max(point[1] for point in tor.body)
            box_torpedo = AABB(min_x, min_y, max_x - min_x, max_y - min_y)

            # Check collision with sub11
            box_sub11 = sub11.get_bounding_box()
            
            if has_collided(box_torpedo, box_sub11):
                tor.active = False
                if sub11.life > 0:  # Check if life is greater than 0 before decreasing
                    sub11.life -= 1
                if sub11.life == 0:
                    sub11.control = False
                continue

            # Circle collision with sub11 front and back
            for circle in [sub11.circle1, sub11.circle2]:
                cx, cy = circle
                circle_radius = 50
                torpedo_radius = 35
                distance = math.sqrt((tor.body[0][0] - cx) ** 2 + (tor.body[0][1] - cy) ** 2)
                if distance <= circle_radius + torpedo_radius:
                    tor.active = False
                    if sub11.life > 0:  # Check if life is greater than 0 before decreasing
                        sub11.life -= 1
                    if sub11.life == 0:
                        sub11.control = False
                    break
       
            
            
class Bubble:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.rad = 10
        self.flag = True
        
def draw_bubble():
    global bubbles
    for i in bubbles:
        if i.flag == True:
            points = MidPointCircle(i.rad)
            all_points = zone_converter(i.x,i.y,points)
            for j in all_points[1]:
                if j[1] > 230 :
                    i.flag = False
            for j in all_points:
                for k in j:
                    glColor3f(1.0, 1.0, 1.0)
                    draw_points(k[0],k[1],1)

def update_bubbles(current_time):
    global bubbles, start_time1, start_time2, sub11, sub22

    elapsed_time1 = current_time - start_time1
    elapsed_time2 = current_time - start_time2

    if elapsed_time1 > 2 and sub11.control:
        x1 = (sub11.air_duct['ap1'][0] + sub11.air_duct['ap2'][0]) / 2
        y1 = (sub11.air_duct['ap1'][1] + 5)
        bubbles.append(Bubble(x1, y1))
        start_time1 = current_time

    if elapsed_time2 > 2 and sub22.control:
        x1 = (sub22.air_duct['ap1'][0] + sub22.air_duct['ap2'][0]) / 2
        y1 = (sub22.air_duct['ap1'][1] + 5)
        bubbles.append(Bubble(x1, y1))
        start_time2 = current_time + 3

    for bubble in bubbles:
        bubble.y += 0.3
        bubble.rad += speed_rad



class rain:
    def __init__(self, x, y):
        self.x1 = x
        self.y1 = y
        self.x2 = x
        self.y2 = y + 15

    def draw(self):
        color = (0.0, 0.0, 1.0)  # Example color for rain (blue)
        draw_lines(color, self.x1, self.y1, self.x2, self.y2)

def draw_rain(rains):
    for rain_group in rains:
        for rain in rain_group:
            if -160 < rain.x1 < 130:
                if 60 < rain.x1 < 120:
                    continue  # Skip drawing for this range
                elif rain.y1 > 310:
                    rain.draw()  # Draw the rain drop
            else:
                rain.draw()  # Draw the rain drop

def generate_rain(num_drops, y):
    return [rain(random.uniform(-680, 680), y) for _ in range(num_drops)]

def create_rain_groups():
    rains = []
    rains.append(generate_rain(40, 380))
    rains.append(generate_rain(30, 405))
    rains.append(generate_rain(40, 425))
    rains.append(generate_rain(40, 450))
    rains.append(generate_rain(25, 480))
    return rains

rains = create_rain_groups()

def update_rains():
    global rains, speed_rain

    for rain in rains:
        for k in rain:
            k.y1 -= speed_rain
            k.y2 -= speed_rain
            if k.y1 < 230:
                reset_rain_position(k, rains.index(rain))

def reset_rain_position(k, index):
    positions = [
        (380, 395),
        (405, 420),
        (425, 440),
        (450, 465),
        (470, 485)
    ]
    k.y1, k.y2 = positions[index]


def draw_clouds(color, center, radius):
    glColor3f(*color)
    points = []
    x, y = 0, radius
    p = 1 - radius  # Decision parameter

    while x <= y:
        for dx in range(-x, x + 1, 2):  # Increased step size
            points.append((center[0] + dx, center[1] + y))
            points.append((center[0] + dx, center[1] - y))
        for dx in range(-y, y + 1, 2):  # Increased step size
            points.append((center[0] + dx, center[1] + x))
            points.append((center[0] + dx, center[1] - x))

        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1

    draw_points_batch(points, 2)


class submarine:
    def __init__(self, list1, list2, list3, list4, list5, list6, circle1, circle2, num):
        self.num = num
        self.main_body = {"mp1": list1[0], "mp2": list1[1], "mp3": list1[2], "mp4": list1[3]}
        self.propeller = {'pp1': list2[0], 'pp2': list2[1], 'pp3': list2[2], 'pp4': list2[3], 'pp5': list2[4]}
        self.top_body = {"tp1": list3[0], "tp2": list3[1], "tp3": list3[2], "tp4": list3[3]}
        self.air_duct = {"ap1": list4[0], "ap2": list4[1], "ap3": list4[2], "ap4": list4[3]}
        self.door = {"dp1": list5[0], "dp2": list5[1], "dp3": list5[2], "dp4": list5[3]}
        self.lower_body = {'lp1': list6[0], 'lp2': list6[1], 'lp3': list6[2], 'lp4': list6[3], 'lp5': list6[4]}
        self.circle1 = circle1
        self.circle2 = circle2
        self.gear = False
        self.control = True
        self.life = 3

    def get_bounding_box(self):
        # Only use relevant parts (main body and lower body) for collision detection
        x_coords = [
            self.main_body["mp1"][0], self.main_body["mp2"][0], 
            self.main_body["mp3"][0], self.main_body["mp4"][0],
            self.lower_body["lp1"][0], self.lower_body["lp2"][0],
            self.lower_body["lp3"][0], self.lower_body["lp4"][0],
        ]
        y_coords = [
            self.main_body["mp1"][1], self.main_body["mp2"][1], 
            self.main_body["mp3"][1], self.main_body["mp4"][1],
            self.lower_body["lp1"][1], self.lower_body["lp2"][1],
            self.lower_body["lp3"][1], self.lower_body["lp4"][1],
        ]

        # Bounding box extremes
        min_x = min(x_coords)
        max_x = max(x_coords)
        min_y = min(y_coords)
        max_y = max(y_coords)

        # Width and height
        width = max_x - min_x
        height = max_y - min_y

        # Center
        center_x = min_x + width / 2
        center_y = min_y + height / 2

        return AABB(center_x, center_y, width, height)

sub11 = submarine(list1,list2,list3,list4,list5,list6,circle1,circle2,1)
submarines.append(sub11)

sub22 = submarine(list11,list22,list33,list44,list55,list66,circle11,circle22,2)
submarines.append(sub22)

def draw_submarine(submarines):
    for sub in submarines:
        # Draw the main body
        color = (0.0, 0.0, 0.0)  # Dark green for the main body
        draw_filled_shape(color, [sub.main_body["mp1"], sub.main_body["mp2"], sub.main_body["mp3"], sub.main_body["mp4"]])
        px1 = sub.main_body["mp1"][0]
        py1 = (sub.main_body['mp1'][1] + sub.main_body['mp4'][1]) / 2
        px2 = sub.main_body['mp2'][0]
        py2 = (sub.main_body['mp2'][1] + sub.main_body['mp3'][1]) / 2
        
        color = (0.023, 0.30, 0.168) 
        draw_filled_circle(px1, py1, 25, color)
        draw_filled_circle(px2, py2, 25, color)
        
        color = (0.0, 0.0, 0.0) 
        # Draw the top body
        draw_filled_shape(color, [sub.top_body["tp1"], sub.top_body["tp2"], sub.top_body["tp3"], sub.top_body["tp4"]])

        # Draw the propeller
        draw_filled_shape(color, [sub.propeller["pp1"], sub.propeller["pp2"], sub.propeller["pp3"], sub.propeller["pp4"], sub.propeller["pp5"]])

        # Draw the air duct
        draw_filled_shape(color, [sub.air_duct["ap1"], sub.air_duct["ap2"], sub.air_duct["ap3"], sub.air_duct["ap4"]])

        # Draw the lower body in two parts
        # Square part
        draw_filled_shape(color, [sub.lower_body["lp1"], sub.lower_body["lp2"], sub.lower_body["lp3"], sub.lower_body["lp4"]])

        # Triangle part
        draw_filled_shape(color, [sub.lower_body["lp4"], sub.lower_body["lp5"], sub.lower_body["lp1"]])

        # Draw circular windows
        color = (0.729, 0.556, 0.137)
        draw_filled_circle(sub.circle1[0], sub.circle1[1], 10, color)  # First circle
        
def update_submarine_positions():
    global sub11, sub22

    if not sub11.control:
        auto_fall(sub11)
    if not sub22.control:
        auto_fall(sub22)




def boatMaker():
    boatx = 80
    boaty = 233
    boat_x1, boat_x2 = -boatx, boatx
    boat_y1, boat_y2 = boaty, boaty

    # Draw the main body of the boat using lines
    color = (0.545, 0.396, 0.275)  # Brown color for the boat
    draw_lines(color, boat_x1, boat_y1, boat_x2, boat_y2)  # Bottom line
    draw_lines(color, boat_x1 - 40, boat_y1 + 40, boat_x1, boat_y1)  # Left side
    draw_lines(color, boat_x1 - 90, boat_y1 + 70, boat_x1 - 40, boat_y1 + 40)  # Left top
    draw_lines(color, boat_x1 - 87, boat_y1 + 75, boat_x1 - 90, boat_y1 + 70)  # Left top curve
    draw_lines(color, boat_x1 - 40, boat_y1 + 55, boat_x1 - 87, boat_y1 + 75)  # Left curve
    draw_lines(color, boat_x1, boat_y1 + 55, boat_x1 - 40, boat_y1 + 55)  # Left curve
    draw_lines(color, boat_x1 + 15, boat_y1 + 40, boat_x1, boat_y1 + 55)  # Right curve
    draw_lines(color, boat_x1 + 90, boat_y1 + 40, boat_x1 + 15, boat_y1 + 40)  # Right side
    draw_lines(color, boat_x1 + 110, boat_y1 + 55, boat_x1 + 90, boat_y1 + 40)  # Right top
    draw_lines(color, boat_x1 + 180, boat_y1 + 55, boat_x1 + 110, boat_y1 + 55)  # Right top
    draw_lines(color, boat_x1 + 180, boat_y1 + 30, boat_x1 + 180, boat_y1 + 55)  # Right side

    # Connect the right side to the bottom
    draw_lines(color, boat_x2, boat_y2, boat_x1 + 180, boat_y1 + 30)  # Connect bottom right

    # Draw the upper part of the boat using lines
    color = (1.0, 0.862, 0.345)  # Yellow color for the upper part
    draw_lines(color, boatx - 20, boaty + 55, boatx - 20, boaty + 140)  # Left side
    draw_lines(color, boatx + 40, boaty + 70, boatx - 20, boaty + 140)  # Right side
    draw_lines(color, boatx - 10, boaty + 70, boatx + 40, boaty + 70)  # Top
    draw_lines(color, boatx - 10, boaty + 55, boatx - 10, boaty + 70)  # Left top

    # Draw the cabin using lines
    color = (0.333, 0.420, 0.184)  # Dark brown color for the cabin
    draw_lines(color, boatx - 108, boaty + 40, boatx - 108, boaty + 65)  # Left side
    draw_lines(color, boatx - 70, boaty + 40, boatx - 108, boaty + 65)  # Top
    draw_lines(color, boatx - 70, boaty + 65, boatx - 108, boaty + 65)  # Right top
    draw_lines(color, boatx - 108, boaty + 50, boatx - 154, boaty + 77)  # Left top
    draw_lines(color, boatx - 150, boaty + 82, boatx - 108, boaty + 57)  # Right top

    # Draw the circles on the boat
    color = (0.2, 0.2, 0.2)  # Green color for the circles
    draw_filled_circle(-boatx + 15, boaty + 20, 10, color)
    draw_filled_circle(-boatx + 55, boaty + 20, 10, color)
    draw_filled_circle(-boatx + 95, boaty + 20, 10, color)
    draw_filled_circle(-boatx + 135, boaty + 20, 10, color)

    # Draw the small circles
    color = (0.2, 0.2, 0.2)  # Black color for the small circles
    
    draw_filled_circle(-boatx + 2, boaty + 83, 7, color)
    draw_filled_circle(-boatx + 2, boaty + 83, 4, color)

        
def draw_bombs():
    global bombs, bombN
    idx = 0
    for bomb in bombs:
        if -420 <= bomb[0] <= 420 and -318 <= bomb[1] <= -213:
            bombN[idx] = False
        else:
            if bombN[idx]:
                # Draw active bombs
                color = (0.0, 0.0, 0.0)  # Red color for active bombs
                draw_filled_circle(bomb[0], bomb[1], 5, color)
                color = (0.0, 0.0, 0.0)  # Black outline for bombs
                draw_hollow_circle(bomb[0], bomb[1], 10, color)
        idx += 1
        
def update_bombs():
    global bombs, bombN, bomb_left, bomb_right, fall_speed

    dx = [1 / bomb_left[0], 1 / bomb_left[1], 1 / bomb_right[0], 1 / bomb_right[1]]

    # Update bomb positions
    for i in range(len(bombs)):
        bombs[i][0] -= dx[i]  # Horizontal movement
        bombs[i][1] -= fall_speed  # Vertical movement

    if all(bomb[1] < -300 for bomb in bombs):
        reset_bombs()

    bomb_radius = 5  # Bomb's radius
    for i, bomb in enumerate(bombs):
        check_bomb_collisions(bomb, bomb_radius, i)

def check_bomb_collisions(bomb, bomb_radius, index):
    global sub11, sub22, bombN

    bx, by = bomb
    collided = False

    # Submarine sub11 collision
    box_sub11 = sub11.get_bounding_box()
    if has_collided(AABB(bx, by, bomb_radius * 2, bomb_radius * 2), box_sub11):
        if bombN[index] and sub11.life > 0:
            sub11.life -= 1
            bombN[index] = False
            collided = True

    # Submarine sub22 collision
    if not collided:
        box_sub22 = sub22.get_bounding_box()
        if has_collided(AABB(bx, by, bomb_radius * 2, bomb_radius * 2), box_sub22):
            if bombN[index] and sub22.life > 0:
                sub22.life -= 1
                bombN[index] = False
                collided = True

    # Circle collisions for finer detection
    if not collided:
        for circle in [sub11.circle1, sub11.circle2]:
            cx, cy = circle
            circle_radius = 65  # Assuming submarine circles have this radius
            distance = math.sqrt((bx - cx) ** 2 + (by - cy) ** 2)
            if distance <= circle_radius + bomb_radius:
                if bombN[index] and sub11.life > 0:
                    sub11.life -= 1
                    bombN[index] = False
                    collided = True
                    break

    if not collided:
        for circle in [sub22.circle1, sub22.circle2]:
            cx, cy = circle
            circle_radius = 65
            distance = math.sqrt((bx - cx) ** 2 + (by - cy) ** 2)
            if distance <= circle_radius + bomb_radius:
                if bombN[index] and sub22.life > 0:
                    sub22.life -= 1
                    bombN[index] = False
                    collided = True
                    break

    if sub11.life == 0:
        sub11.control = False
    if sub22.life == 0:
        sub22.control = False
    
    
def draw_titanic():
    # Set the body color
    color_body = (0.333, 0.333, 0.333)
    
    # Draw the ship's base
    draw_lines(color_body, -200, -250, 200, -250)  # Bottom line of the ship
    draw_lines(color_body, -200, -250, -220, -230)  # Left slope
    draw_lines(color_body, 200, -250, 220, -230)  # Right slope

    # Draw the ship's deck
    draw_lines(color_body, -180, -230, 180, -230)

    # Chimney color
    color_chimney = (0.129, 0.141, 0.141)
    
    # Draw chimneys
    draw_filled_circle(-140, -200, 10, color_chimney)  # Left chimney base
    draw_lines(color_chimney, -140, -200, -140, -170)  # Left chimney body

    draw_filled_circle(0, -200, 10, color_chimney)  # Middle chimney base
    draw_lines(color_chimney, 0, -200, 0, -170)  # Middle chimney body

    draw_filled_circle(140, -200, 10, color_chimney)  # Right chimney base
    draw_lines(color_chimney, 140, -200, 140, -170)  # Right chimney body

    # Window color
    color_window = (0.647, 0.165, 0.165)
    
    # Draw windows
    for x in range(-150, 151, 30):  # Spread windows across the ship
        draw_filled_circle(x, -240, 5, color_window)


    
def auto_fall(sub): 
    if sub.main_body['mp3'][1] > -300:
        for j in sub.main_body:
            sub.main_body[j][1] -= 2
        for j in sub.propeller:
            sub.propeller[j][1] -= 2
        for j in sub.top_body:
            sub.top_body[j][1] -= 2
        for j in sub.air_duct:
            sub.air_duct[j][1] -= 2
        for j in sub.door:
            sub.door[j][1] -= 2
        for j in sub.lower_body:
            sub.lower_body[j][1] -= 2
        sub.circle1 = [sub.circle1[0], sub.circle1[1] - 2]
        sub.circle2 = [sub.circle2[0], sub.circle2[1] - 2]
    else:
        # If the submarine has fallen below the ground level
        sub.control = False  # Disable control for this submarine
        if sub.num == 1:
            global player
            player = 1  # Right submarine wins
        elif sub.num == 2:
            player = 2  # Left submarine wins
        global game_over
        game_over = True  # Set game over state



class UniqueCircle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.active = True  # Status of the health circle
        self.direction = 1  # 1 for growing, -1 for shrinking
        self.max_radius = 30  # Maximum radius
        self.min_radius = 10  # Minimum radius

def spawn_unique_circle():
    # Randomly spawn a health circle
    x = random.uniform(-300, 300)
    y = 200  # Start above the screen
    radius = 20  # Initial radius of the health circle
    unique_circles.append(UniqueCircle(x, y, radius))

def update_unique_circles():
    global unique_circles
    for circle in unique_circles:
        if circle.active:
            # Update the radius
            circle.radius += circle.direction * 1  # Change radius
            if circle.radius >= circle.max_radius or circle.radius <= circle.min_radius:
                circle.direction *= -1  # Reverse direction
            # Move the circle down
            circle.y -= 4  # Move the circle down
            if circle.y < -250:  # Deactivate if it goes off screen
                circle.active = False

def draw_unique_circles():
    global unique_circles
    for circle in unique_circles:
        if circle.active:
            draw_hollow_circle(circle.x, circle.y, int(circle.radius), (0.0, 0.0, 0.0))  # Red circle
            # Draw the health circle as a hollow red cross
            draw_hollow_cross(circle.x, circle.y, int(circle.radius), (1.0, 0.0, 0.0))  # Red color

def check_collision_with_unique_circle(submarine):
    global unique_circles
    for circle in unique_circles:
        if circle.active:
            cx, cy, radius = circle.x, circle.y, circle.radius
            booster_box = AABB(cx - radius, cy - radius, radius * 2, radius * 2)

            # Bounding box of the submarine
            sub_box = submarine.get_bounding_box()

            # Check for bounding box collision
            if has_collided(sub_box, booster_box):
                circle.active = False
                if submarine.life > 0:  
                        submarine.life += 2# Increase submarine's life

            # Additional circle-based collision detection
            for sub_circle in [submarine.circle1, submarine.circle2]:
                scx, scy = sub_circle
                sub_circle_radius = 65  # Assuming submarine circles have this radius
                distance = math.sqrt((cx - scx) ** 2 + (cy - scy) ** 2)
                if distance <= radius + sub_circle_radius:
                    circle.active = False
                    if submarine.life > 0: 
                        submarine.life += 2  # Increase submarine's life
                        break

# Utility function to draw a hollow cross
def draw_hollow_cross(x, y, size, color):
    # Draw a vertical line
    draw_lines(color, x, y - size, x, y + size)
    # Draw a horizontal line
    draw_lines(color, x - size, y, x + size, y)


class Shark:
    def __init__(self, x, y, direction):
        self.x = x  # Initial x position
        self.y = y  # Initial y position
        self.direction = direction  # 1 for right-to-left, -1 for left-to-right
        self.speed = 4  # Speed of the shark
        self.width = 50  # Width for bounding box
        self.height = 30  # Height for bounding box
        self.active = True  # Status of the shark

    def move(self):
        # Move the shark horizontally
        self.x += self.speed * self.direction


    def get_bounding_box(self):
        return AABB(self.x, self.y, self.width, self.height)

def spawn_shark():
    direction = random.choice([-1, 1])  # Randomly choose left-to-right or right-to-left
    if direction == 1:
        x = -350 
    else:
        x = 350  # Start at the left or right edge
    y = random.uniform(-200, 200)  # Random y position
    sharks.append(Shark(x, y, direction))

def update_sharks():
    for shark in sharks:
        if shark.active:
            shark.move()
            if shark.x < -400 or shark.x > 400:  # Off-screen horizontally
                shark.active = False

            # Check for collision with submarines
            for sub in submarines:
                sub_box = sub.get_bounding_box()
                shark_box = shark.get_bounding_box()

                # Bounding box collision check
                if has_collided(shark_box, sub_box):
                    if sub.life > 0: 
                            sub.life -= 1  # Decrease submarine life
                            shark.active = False  # Deactivate the shark after collision
                            continue

                # Additional circle-based collision detection
                for sub_circle in [sub.circle1, sub.circle2]:
                    scx, scy = sub_circle
                    sub_circle_radius = 65  # Submarine circle radius
                    distance = math.sqrt((shark.x - scx) ** 2 + (shark.y - scy) ** 2)
                    if distance <= sub_circle_radius + shark.width / 2:  # Shark's bounding circle radius
                        if sub.life > 0: 
                            sub.life -= 1
                            shark.active = False
                            break

def draw_shark(shark):
    if not shark.active:
        return
    
    # Colors
    shark_color = (0.2, 0.3, 0.8)  # Blue-grey
    eye_color = (1.0, 1.0, 1.0)    # White
    gill_color = (0.1, 0.2, 0.7)   # Darker blue
    
    # Flip the x-offsets based on direction
    def adjust_x(x_offset):
        return x_offset * -shark.direction
    
    # Body outline points
    body_points = [
        (shark.x + adjust_x(-40), shark.y),           # Nose
        (shark.x + adjust_x(-20), shark.y - 15),      # Bottom jaw
        (shark.x + adjust_x(20), shark.y - 10),       # Bottom body
        (shark.x + adjust_x(40), shark.y),            # Back
        (shark.x + adjust_x(20), shark.y + 10),       # Top body
        (shark.x + adjust_x(-20), shark.y + 15),      # Top jaw
        (shark.x + adjust_x(-40), shark.y)            # Back to nose
    ]
    
    # Draw body outline
    for i in range(len(body_points) - 1):
        draw_lines(shark_color,
            body_points[i][0], body_points[i][1],
            body_points[i+1][0], body_points[i+1][1]
        )
    
    # Dorsal fin
    draw_lines(shark_color, 
        shark.x + adjust_x(10), shark.y + 10, 
        shark.x + adjust_x(15), shark.y + 25)
    draw_lines(shark_color, 
        shark.x + adjust_x(15), shark.y + 25, 
        shark.x + adjust_x(25), shark.y + 10)
    
    # Tail fin
    tail_points = [
        (shark.x + adjust_x(40), shark.y),            # Base
        (shark.x + adjust_x(55), shark.y + 15),       # Top tip
        (shark.x + adjust_x(50), shark.y),            # Middle
        (shark.x + adjust_x(55), shark.y - 15),       # Bottom tip
        (shark.x + adjust_x(40), shark.y)             # Back to base
    ]
    
    # Draw tail
    for i in range(len(tail_points) - 1):
        draw_lines(shark_color,
            tail_points[i][0], tail_points[i][1],
            tail_points[i+1][0], tail_points[i+1][1]
        )
    
    # Eye (white circle with black center)
    draw_filled_circle(shark.x + adjust_x(-30), shark.y + 5, 3, eye_color)
    draw_filled_circle(shark.x + adjust_x(-30), shark.y + 5, 1, (0.0, 0.0, 0.0))
    
    # Gills (three curved lines)
    for i in range(3):
        offset = i * 4
        draw_lines(gill_color,
            shark.x + adjust_x(-15 + offset), shark.y + 5,
            shark.x + adjust_x(-15 + offset), shark.y - 5
        )
    
    # Pectoral fin
    draw_lines(shark_color, 
        shark.x + adjust_x(0), shark.y - 10, 
        shark.x + adjust_x(10), shark.y - 20)
    draw_lines(shark_color, 
        shark.x + adjust_x(10), shark.y - 20, 
        shark.x + adjust_x(20), shark.y - 10)
    


def draw_restart():
    center_x = -100  
    base_y = -350 
    icon_size = 20  
    color = (1.0, 0.0, 0.0)

    draw_lines(color, center_x - icon_size // 2, base_y, center_x + icon_size // 2, base_y)  # Horizontal line
    draw_lines(color, center_x - icon_size // 2, base_y, center_x, base_y + icon_size // 2)  # Upper slant
    draw_lines(color, center_x - icon_size // 2, base_y, center_x, base_y - icon_size // 2)  # Lower slant

def draw_pause():
    global paused
    center_x = 0  
    base_y = -350 
    icon_size = 20  
    gap = 6  
    color = (1, 0.73, 0.2)

    if not paused:
        draw_lines(color, center_x - gap, base_y + icon_size // 2, center_x - gap, base_y - icon_size // 2)
        draw_lines(color, center_x + gap, base_y + icon_size // 2, center_x + gap, base_y - icon_size // 2)
    else:
        draw_lines(color, center_x - gap, base_y + icon_size // 2, center_x - gap, base_y - icon_size // 2)
        draw_lines(color, center_x - gap, base_y + icon_size // 2, center_x + icon_size // 2, base_y)
        draw_lines(color, center_x - gap, base_y - icon_size // 2, center_x + icon_size // 2, base_y)

def draw_cancel():
    center_x = 100  
    base_y = -350  
    icon_size = 20  
    color = (1, 0, 0)
    draw_lines(color, center_x - icon_size // 2, base_y + icon_size // 2, center_x + icon_size // 2, base_y - icon_size // 2)
    draw_lines(color, center_x + icon_size // 2, base_y + icon_size // 2, center_x - icon_size // 2, base_y - icon_size // 2)



class AABB:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

def has_collided(box1, box2):
    return (box1.x < box2.x + box2.width and
            box1.x + box1.width > box2.x and
            box1.y < box2.y + box2.height and
            box1.y + box1.height > box2.y)


def handle_spawn_events(current_time):
    global last_spawn_time, spawn_interval, unique_circles, last_spawn_time_shark, sharks

    if current_time - last_spawn_time > spawn_interval:
        spawn_unique_circle()
        last_spawn_time = current_time

    update_unique_circles()
    check_collision_with_unique_circle(sub11)
    check_collision_with_unique_circle(sub22)

    draw_unique_circles()

    if current_time - last_spawn_time_shark > 15:
        spawn_shark()
        last_spawn_time_shark = current_time

    update_sharks()  # Update shark positions and check for collisions
    for shark in sharks:
        draw_shark(shark)

def reset_game():
    global game_over, paused, player, sub11, sub22, bombs, bombN, rains

    game_over = False
    paused = False
    player = None
    sub11.control = True
    sub22.control = True
    sub11.life = 3
    sub22.life = 3
    torpedo1.clear()
    torpedo2.clear()
    bubbles.clear()
    sharks.clear()
    unique_circles.clear()

    reset_submarine_positions()
    reset_bombs()
    reset_rains()  # Reset bomb directions

def reset_submarine_positions():
            global sub11, sub22

            # Reset positions of submarines
            sub11.main_body = {"mp1": [-530, 180], "mp2": [-630, 180], "mp3": [-630, 130], "mp4": [-530, 130]}
            sub11.propeller = {"pp1": [-660, 165], "pp2": [-680, 165], "pp3": [-680, 145], "pp4": [-660, 145], "pp5": [-655, 155]}
            sub11.top_body = {"tp1": [-550, 200], "tp2": [-580, 200], "tp3": [-610, 180], "tp4": [-550, 180]}
            sub11.air_duct = {"ap1": [-560, 215], "ap2": [-570, 215], "ap3": [-570, 200], "ap4": [-560, 200]}
            sub11.door = {"dp1": [-540, 165], "dp2": [-560, 165], "dp3": [-560, 145], "dp4": [-540, 145]}
            sub11.lower_body = {"lp1": [-570, 130], "lp2": [-610, 130], "lp3": [-610, 115], "lp4": [-570, 115], "lp5": [-555, 122.5]}
            sub11.circle1 = [-580, 155]
            sub11.circle2 = [-615, 155]
            
            sub22.main_body = {"mp1": [530, 180], "mp2": [630, 180], "mp3": [630, 130], "mp4": [530, 130]}
            sub22.propeller = {"pp1": [660, 165], "pp2": [680, 165], "pp3": [680, 145], "pp4": [660, 145], "pp5": [655, 155]}
            sub22.top_body = {"tp1": [550, 200], "tp2": [580, 200], "tp3": [610, 180], "tp4": [550, 180]}
            sub22.air_duct = {"ap1": [560, 215], "ap2": [570, 215], "ap3": [570, 200], "ap4": [560, 200]}
            sub22.door = {"dp1": [540, 165], "dp2": [560, 165], "dp3": [560, 145], "dp4": [540, 145]}
            sub22.lower_body = {"lp1": [570, 130], "lp2": [610, 130], "lp3": [610, 115], "lp4": [570, 115], "lp5": [555, 122.5]}
            sub22.circle1 = [580, 155]
            sub22.circle2 = [615, 155]

def reset_bombs():
    global bombs, bombN, theta, bomb_left, bomb_right
    boatx = 80
    boaty = 233
    bombs = [[-boatx + 15, boaty + 20], [-boatx + 55, boaty + 20], [-boatx + 95, boaty + 20], [-boatx + 135, boaty + 20]]
    bombN = [True, True, True, True]
    
    theta = random.randrange(-30, 30)
    bomb_left = [tan((225+theta)*(pi/180)), tan((225+theta+20)*(pi/180))]
    bomb_right = [tan((315+theta)*(pi/180)), tan((315+theta+20)*(pi/180))]
    
def reset_rains():
    global rains
    rains.clear()
    rains.append(generate_rain(40, 380))
    rains.append(generate_rain(30, 405))
    rains.append(generate_rain(40, 425))
    rains.append(generate_rain(40, 450))
    rains.append(generate_rain(25, 480))

def check_game_over_conditions():
    global game_over, player, sub11, sub22

    if (-270 < sub11.main_body['mp3'][0] < 250 and 
        sub11.main_body['mp3'][1] < -240 and 
        sub11.control):
        player = 1
        game_over = True

    if (-270 < sub22.main_body['mp3'][0] < 250 and 
        sub22.main_body['mp3'][1] < -240 and 
        sub22.control):
        player = 2
        game_over = True

    if not sub11.control and not sub22.control:
        game_over = True

def render_text(text, x, y, font, color):
    glColor3f(color[0], color[1], color[2])
    glRasterPos2f(x, y)

    for char in text:
        glutBitmapCharacter(font, ord(char))

def create_background_list():
    global background_list
    background_list = glGenLists(1)
    glNewList(background_list, GL_COMPILE)
    
    # Draw the background layers
    fill_rectangle(background_color, -680, -300, 680, 285)
    fill_rectangle(light_water_color, -680, 230, 680, 380)
    fill_rectangle(bottom_color, -685, -380, 685, -300)
    
    # Draw static clouds
    color = (0.502, 0.6, 0.667)
    static_clouds = [
        (-392, 350, 30), (-410, 337, 25), (-375, 338, 25),
        (239, 294, 35), (215, 285, 25), (260, 285, 25),
        (580, 320, 35), (555, 310, 25), (605, 310, 25),
        (-680, 290, 25), (-665, 285, 19)
    ]
    for x, y, r in static_clouds:
        draw_clouds(color, (x, y), r)
    
    glEndList()

def display():
    global submarines, bubbles, player, background_update_needed, sharks, rains
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-683, 683, -384, 384, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    if background_list is None:
            create_background_list()
            background_update_needed = False 
    glCallList(background_list)  

    if game_over == False:
        draw_torpedo(torpedo1)
        draw_torpedo(torpedo2)
        draw_unique_circles()
        draw_bubble()
        draw_bombs()
        draw_submarine(submarines)
        for shark in sharks:
            draw_shark(shark)
    if paused:
        font = GLUT_BITMAP_HELVETICA_18
        text_color = (1.0, 0.0, 0.0)  # Red color for pause text
        render_text("PAUSED", -50, 50, font, text_color)  # Display pause message
    
    boatMaker()
    draw_titanic()
    draw_rain(rains)
    draw_restart()
    draw_cancel()
    draw_pause()
    font = GLUT_BITMAP_HELVETICA_18
    text_color = (1.0, 0.7, 0.2)
     
    txt1 = "GAME OVER"
    txt2 = "RIGHT SUBMARINE(DESTROYER) HAS WON THE GAME"
    txt3 = "LEFT SUBMARINE(MARKAVA) HAS WON THE GAME"
    txt4 = 'NOBODY SUBMARINE HAS WON. RESULT : DRAW'
    txt5 = "Markava life : " + str(sub11.life)
    txt6 = "Destroyer life : " + str(sub22.life)
    render_text(txt5, -650, -360, font, text_color)
    render_text(txt6, 500, -360, font, text_color)    

    text_color = (0.0, 0.0, 0.0)
    font = GLUT_BITMAP_HELVETICA_18
    if game_over:
        if player == 1:
            render_text(txt1, -100, 50, font, text_color)
            render_text(txt2, -280, -50, font, text_color)
        elif player == 2:
            render_text(txt1 , -100, 50, font, text_color)
            render_text(txt3, -280, -50, font, text_color)
        else:
            render_text(txt1, -100, 50, font, text_color)
            render_text(txt4, -280, -50, font, text_color)           
    glutSwapBuffers()
    
def animate():
        global last_update, bubbles, speed_rad, sub11, sub22, bubbles ,start_time1,start_time2, rains, speed_rain, torpedo1, torpedo2, speed_tor, game_over,player, bombs, bombN, bomb_left, bomb_right, sub11, sub22, game_over, player
        global bomb_left, bomb_right, bombs, bombN 
        global background_update_needed
        global paused, restart_game, last_spawn_time, spawn_interval, unique_circles, last_spawn_time_shark, sharks
        

        if restart_game:
            reset_game()
            restart_game = False  # Reset the restart flag
        if paused or game_over:
            return
        if background_update_needed:
            create_background_list()  # Recreate background display list
            background_update_needed = False  # Reset the fla
        current_time = time.time()
        if current_time - last_update < 0.016:  # Cap at ~60 FPS
            return
        
        if not paused:
            handle_spawn_events(current_time)
            update_bubbles(current_time)
            update_rains()
            update_submarine_positions()
            check_game_over_conditions()
            update_bombs()
            update_torpedoes()
            draw_unique_circles()
            
        glutPostRedisplay()

def keyboardListener(key, x, y):
    global sub22, sub11, submarines, speed_sub, torpedo1, torpedo2, tor_time1, tor_time2, game_over, speed_sub1, speed_tor
    global paused, restart_game
    global background_color, light_water_color, step_size, background_update_needed

    if key == b'y':  # Transition to night mode
        background_color = (0.1, 0.2, 0.4)  # Set to dark blue for night
        light_water_color = [0.0, 0.0, 0.2]  # Darker blue for water
        background_update_needed = True  # Mark the background for update


    if key == b'u':  # Transition to day mode
        background_color = [0.0, 0.5, 1.0]  # Set to light blue for day
        light_water_color = (0.53, 0.81, 0.98)  # Light blue for water
        background_update_needed = True  # Mark the background for update

    if key==b'o':
        if sub22.gear:
            sub22.gear = False
        else:
            sub22.gear = True
    if key==b'q':
        if sub11.gear:
            sub11.gear = False
        else:
            sub11.gear = True

    if key == b'i':
            paused = not paused  # Toggle pause state

    if key == b'r':
        restart_game = True  # Set restart flag
    




    if key == b'c':
        if not game_over:
            m = sub22.circle1[0] - sub11.circle1[0]
            n = sub22.circle1[1] - sub11.circle1[1]
            n1 = (n / m) * speed_tor
            time_int1 = time.time() - tor_time1
            if time_int1 > 1.5:
                list1 = []
                for i in sub11.lower_body.keys():
                    k = sub11.lower_body[i]
                    list1.append([k[0], k[1]])  # Directly append the coordinates
                tor = Torpedo(list1, speed_tor, n1)  # Use the updated Torpedo class
                torpedo1.append(tor)
                tor_time1 = time.time()

    if key == b'p':
        if not game_over:
            m = sub11.circle1[0] - sub22.circle1[0]
            n = sub11.circle1[1] - sub22.circle1[1]
            n1 = (n / m) * speed_tor
            time_int2 = time.time() - tor_time2
            if time_int2 > 1.5:
                list1 = []
                for i in sub22.lower_body.keys():
                    k = sub22.lower_body[i]
                    list1.append([k[0], k[1]])  # Directly append the coordinates
                tor = Torpedo(list1, speed_tor, n1)  # Use the updated Torpedo class
                torpedo2.append(tor)
                tor_time2 = time.time()

    if key==b's':
        if game_over == False and paused == False:
            for sub in submarines:
                if sub.num == 1:
                    if sub.control == True:
                        if sub.main_body['mp3'][1] > -320 :  
                            if sub.gear == False:
                                if -270<sub.main_body['mp3'][0]<250 and  sub.main_body['mp3'][1] < -240 :
                                    pass
                                else:
                                    for j in sub.main_body:
                                        sub.main_body[j][1] = sub.main_body[j][1]-speed_sub
                                    for j in sub.propeller:
                                        sub.propeller[j][1] = sub.propeller[j][1]-speed_sub
                                    for j in sub.top_body:
                                        sub.top_body[j][1] = sub.top_body[j][1]-speed_sub
                                    for j in sub.air_duct:
                                        sub.air_duct[j][1] = sub.air_duct[j][1]-speed_sub
                                    for j in sub.door:
                                        sub.door[j][1] = sub.door[j][1]-speed_sub
                                    for j in sub.lower_body:
                                        sub.lower_body[j][1] = sub.lower_body[j][1]-speed_sub                    
                                    sub.circle1 = [sub.circle1[0], sub.circle1[1]-speed_sub]
                                    sub.circle2 = [sub.circle2[0], sub.circle2[1]-speed_sub]
                            else:
                                if (sub.main_body['mp3'][0] -50) > -680 and  ((sub.main_body['mp1'][1] +sub.main_body['mp3'][1]) / 2) <= 225 :              
                                    for j in sub.main_body:
                                        sub.main_body[j][1] = sub.main_body[j][1]+speed_sub1
                                        sub.main_body[j][0] = sub.main_body[j][0]-speed_sub1
                                    for j in sub.propeller:
                                        sub.propeller[j][1] = sub.propeller[j][1]+speed_sub1
                                        sub.propeller[j][0] = sub.propeller[j][0]-speed_sub1
                                    for j in sub.top_body:
                                        sub.top_body[j][1] = sub.top_body[j][1]+speed_sub1
                                        sub.top_body[j][0] = sub.top_body[j][0]-speed_sub1
                                    for j in sub.air_duct:
                                        sub.air_duct[j][1] = sub.air_duct[j][1]+speed_sub1
                                        sub.air_duct[j][0] = sub.air_duct[j][0]-speed_sub1
                                    for j in sub.door:
                                        sub.door[j][1] = sub.door[j][1]+speed_sub1
                                        sub.door[j][0] = sub.door[j][0]-speed_sub1
                                    for j in sub.lower_body:
                                        sub.lower_body[j][1] = sub.lower_body[j][1]+speed_sub1
                                        sub.lower_body[j][0] = sub.lower_body[j][0]-speed_sub1         

                                    sub.circle1 = [sub.circle1[0], sub.circle1[1]+speed_sub1]
                                    sub.circle2 = [sub.circle2[0], sub.circle2[1]+speed_sub1]
                                    sub.circle1 = [sub.circle1[0]-speed_sub1, sub.circle1[1]]
                                    sub.circle2 = [sub.circle2[0]-speed_sub1, sub.circle2[1]]                          

    if key== b'w':
        if game_over == False and paused == False:		
            for sub in submarines:
                if sub.num == 1:
                    if sub.control == True:
                        if ((sub.main_body['mp1'][1] +sub.main_body['mp3'][1]) / 2) <= 225:  
                            if sub.gear == False:
                                for j in sub.main_body:
                                    sub.main_body[j][1] = sub.main_body[j][1]+speed_sub
                                for j in sub.propeller:
                                    sub.propeller[j][1] = sub.propeller[j][1]+speed_sub
                                for j in sub.top_body:
                                    sub.top_body[j][1] = sub.top_body[j][1]+speed_sub
                                for j in sub.air_duct:
                                    sub.air_duct[j][1] = sub.air_duct[j][1]+speed_sub
                                for j in sub.door:
                                    sub.door[j][1] = sub.door[j][1]+speed_sub
                                for j in sub.lower_body:
                                    sub.lower_body[j][1] = sub.lower_body[j][1]+speed_sub
                                
                                sub.circle1 = [sub.circle1[0], sub.circle1[1]+speed_sub]
                                sub.circle2 = [sub.circle2[0], sub.circle2[1]+speed_sub]  
                            else:
                                if sub.main_body['mp1'][0] + 35 < 680: 
                                    for j in sub.main_body:
                                        sub.main_body[j][1] = sub.main_body[j][1]+speed_sub1
                                        sub.main_body[j][0] = sub.main_body[j][0]+speed_sub1
                                    for j in sub.propeller:
                                        sub.propeller[j][1] = sub.propeller[j][1]+speed_sub1
                                        sub.propeller[j][0] = sub.propeller[j][0]+speed_sub1
                                    for j in sub.top_body:
                                        sub.top_body[j][1] = sub.top_body[j][1]+speed_sub1
                                        sub.top_body[j][0] = sub.top_body[j][0]+speed_sub1
                                    for j in sub.air_duct:
                                        sub.air_duct[j][1] = sub.air_duct[j][1]+speed_sub1
                                        sub.air_duct[j][0] = sub.air_duct[j][0]+speed_sub1
                                    for j in sub.door:
                                        sub.door[j][1] = sub.door[j][1]+speed_sub1
                                        sub.door[j][0] = sub.door[j][0]+speed_sub1
                                    for j in sub.lower_body:
                                        sub.lower_body[j][1] = sub.lower_body[j][1]+speed_sub1
                                        sub.lower_body[j][0] = sub.lower_body[j][0]+speed_sub1    

                                    sub.circle1 = [sub.circle1[0], sub.circle1[1]+speed_sub1]
                                    sub.circle2 = [sub.circle2[0], sub.circle2[1]+speed_sub1]
                                    sub.circle1 = [sub.circle1[0]+speed_sub1, sub.circle1[1]]
                                    sub.circle2 = [sub.circle2[0]+speed_sub1, sub.circle2[1]]
                
    if key==b'd':
        if game_over == False and paused == False:
            for sub in submarines:
                if sub.num == 1:
                    if sub.control == True:
                        if sub.main_body['mp1'][0] + 35 < 680:  
                            if sub.gear == False:
                                if sub.main_body['mp3'][1] < -240:
                                    pass
                                else:
                                    for j in sub.main_body:
                                        sub.main_body[j][0] = sub.main_body[j][0]+speed_sub
                                    for j in sub.propeller:
                                        sub.propeller[j][0] = sub.propeller[j][0]+speed_sub
                                    for j in sub.top_body:
                                        sub.top_body[j][0] = sub.top_body[j][0]+speed_sub
                                    for j in sub.air_duct:
                                        sub.air_duct[j][0] = sub.air_duct[j][0]+speed_sub
                                    for j in sub.door:
                                        sub.door[j][0] = sub.door[j][0]+speed_sub
                                    for j in sub.lower_body:
                                        sub.lower_body[j][0] = sub.lower_body[j][0]+speed_sub      

                                    sub.circle1 = [sub.circle1[0]+speed_sub, sub.circle1[1]]
                                    sub.circle2 = [sub.circle2[0]+speed_sub, sub.circle2[1]]
                            else:
                                if sub.main_body['mp3'][1] > -320 :  
                                    for j in sub.main_body:
                                        sub.main_body[j][1] = sub.main_body[j][1]-speed_sub1
                                        sub.main_body[j][0] = sub.main_body[j][0]+speed_sub1
                                    for j in sub.propeller:
                                        sub.propeller[j][1] = sub.propeller[j][1]-speed_sub1
                                        sub.propeller[j][0] = sub.propeller[j][0]+speed_sub1
                                    for j in sub.top_body:
                                        sub.top_body[j][1] = sub.top_body[j][1]-speed_sub1
                                        sub.top_body[j][0] = sub.top_body[j][0]+speed_sub1
                                    for j in sub.air_duct:
                                        sub.air_duct[j][1] = sub.air_duct[j][1]-speed_sub1
                                        sub.air_duct[j][0] = sub.air_duct[j][0]+speed_sub1
                                    for j in sub.door:
                                        sub.door[j][1] = sub.door[j][1]-speed_sub1
                                        sub.door[j][0] = sub.door[j][0]+speed_sub1
                                    for j in sub.lower_body:
                                        sub.lower_body[j][1] = sub.lower_body[j][1]-speed_sub1
                                        sub.lower_body[j][0] = sub.lower_body[j][0]+speed_sub1        

                                    sub.circle1 = [sub.circle1[0], sub.circle1[1]-speed_sub1]
                                    sub.circle2 = [sub.circle2[0], sub.circle2[1]-speed_sub1]
                                    sub.circle1 = [sub.circle1[0]+speed_sub1, sub.circle1[1]]
                                    sub.circle2 = [sub.circle2[0]+speed_sub1, sub.circle2[1]]  
    if key==b'a':
        if game_over == False and paused == False:
            for sub in submarines:
                if sub.num == 1:
                    if sub.control == True:
                        if (sub.main_body['mp3'][0] -50) > -680:  
                            if sub.gear == False:
                                for j in sub.main_body:
                                    sub.main_body[j][0] = sub.main_body[j][0]-speed_sub
                                for j in sub.propeller:
                                    sub.propeller[j][0] = sub.propeller[j][0]-speed_sub
                                for j in sub.top_body:
                                    sub.top_body[j][0] = sub.top_body[j][0]-speed_sub
                                for j in sub.air_duct:
                                    sub.air_duct[j][0] = sub.air_duct[j][0]-speed_sub
                                for j in sub.door:
                                    sub.door[j][0] = sub.door[j][0]-speed_sub
                                for j in sub.lower_body:
                                    sub.lower_body[j][0] = sub.lower_body[j][0]-speed_sub        
                                sub.circle1 = [sub.circle1[0]-speed_sub, sub.circle1[1]]
                                sub.circle2 = [sub.circle2[0]-speed_sub, sub.circle2[1]]
                            else:
                                if sub.main_body['mp3'][1] > -320 :  
                                    for j in sub.main_body:
                                        sub.main_body[j][1] = sub.main_body[j][1]-speed_sub1
                                        sub.main_body[j][0] = sub.main_body[j][0]-speed_sub1
                                    for j in sub.propeller:
                                        sub.propeller[j][1] = sub.propeller[j][1]-speed_sub1
                                        sub.propeller[j][0] = sub.propeller[j][0]-speed_sub1
                                    for j in sub.top_body:
                                        sub.top_body[j][1] = sub.top_body[j][1]-speed_sub1
                                        sub.top_body[j][0] = sub.top_body[j][0]-speed_sub1
                                    for j in sub.air_duct:
                                        sub.air_duct[j][1] = sub.air_duct[j][1]-speed_sub1
                                        sub.air_duct[j][0] = sub.air_duct[j][0]-speed_sub1
                                    for j in sub.door:
                                        sub.door[j][1] = sub.door[j][1]-speed_sub1
                                        sub.door[j][0] = sub.door[j][0]-speed_sub1
                                    for j in sub.lower_body:
                                        sub.lower_body[j][1] = sub.lower_body[j][1]-speed_sub1
                                        sub.lower_body[j][0] = sub.lower_body[j][0]-speed_sub1   

                                    sub.circle1 = [sub.circle1[0], sub.circle1[1]-speed_sub1]
                                    sub.circle2 = [sub.circle2[0], sub.circle2[1]-speed_sub1]
                                    sub.circle1 = [sub.circle1[0]-speed_sub1, sub.circle1[1]]
                                    sub.circle2 = [sub.circle2[0]-speed_sub1, sub.circle2[1]]      

        glutPostRedisplay()

def specialKeyListener(key, x, y):
    global submarines, speed_sub, game_over
    if key==GLUT_KEY_UP:
        if game_over == False and paused == False:
            for sub in submarines:
                if sub.num == 2:
                    if sub.control == True:
                        if ((sub.main_body['mp1'][1] +sub.main_body['mp3'][1]) / 2) <= 225:  
                            if sub.gear == False:
                                for j in sub.main_body:
                                    sub.main_body[j][1] = sub.main_body[j][1]+speed_sub
                                for j in sub.propeller:
                                    sub.propeller[j][1] = sub.propeller[j][1]+speed_sub
                                for j in sub.top_body:
                                    sub.top_body[j][1] = sub.top_body[j][1]+speed_sub
                                for j in sub.air_duct:
                                    sub.air_duct[j][1] = sub.air_duct[j][1]+speed_sub
                                for j in sub.door:
                                    sub.door[j][1] = sub.door[j][1]+speed_sub
                                for j in sub.lower_body:
                                    sub.lower_body[j][1] = sub.lower_body[j][1]+speed_sub
                                
                            
                                sub.circle1 = [sub.circle1[0], sub.circle1[1]+speed_sub]
                                sub.circle2 = [sub.circle2[0], sub.circle2[1]+speed_sub]
                            else:
                                if sub.main_body['mp1'][0] - 35 > -680: 
                                    for j in sub.main_body:
                                        sub.main_body[j][1] = sub.main_body[j][1]+speed_sub1
                                        sub.main_body[j][0] = sub.main_body[j][0]-speed_sub1
                                    for j in sub.propeller:
                                        sub.propeller[j][1] = sub.propeller[j][1]+speed_sub1
                                        sub.propeller[j][0] = sub.propeller[j][0]-speed_sub1
                                    for j in sub.top_body:
                                        sub.top_body[j][1] = sub.top_body[j][1]+speed_sub1
                                        sub.top_body[j][0] = sub.top_body[j][0]-speed_sub1
                                    for j in sub.air_duct:
                                        sub.air_duct[j][1] = sub.air_duct[j][1]+speed_sub1
                                        sub.air_duct[j][0] = sub.air_duct[j][0]-speed_sub1
                                    for j in sub.door:
                                        sub.door[j][1] = sub.door[j][1]+speed_sub1
                                        sub.door[j][0] = sub.door[j][0]-speed_sub1
                                    for j in sub.lower_body:
                                        sub.lower_body[j][1] = sub.lower_body[j][1]+speed_sub1
                                        sub.lower_body[j][0] = sub.lower_body[j][0]-speed_sub1  

                                    sub.circle1 = [sub.circle1[0], sub.circle1[1]+speed_sub1]
                                    sub.circle2 = [sub.circle2[0], sub.circle2[1]+speed_sub1]
                                    sub.circle1 = [sub.circle1[0]-speed_sub1, sub.circle1[1]]
                                    sub.circle2 = [sub.circle2[0]-speed_sub1, sub.circle2[1]]                          
    
    if key== GLUT_KEY_DOWN:		
        for sub in submarines:
            if game_over == False and paused == False:
                    if sub.num == 2:
                        if sub.control == True:
                            if sub.main_body['mp3'][1] > -320 :  
                                if sub.gear == False:
                                    if -270<sub.main_body['mp3'][0]<250 and  sub.main_body['mp3'][1] < -240 :
                                        pass
                                    else:
                                        for j in sub.main_body:
                                            sub.main_body[j][1] = sub.main_body[j][1]-speed_sub
                                        for j in sub.propeller:
                                            sub.propeller[j][1] = sub.propeller[j][1]-speed_sub
                                        for j in sub.top_body:
                                            sub.top_body[j][1] = sub.top_body[j][1]-speed_sub
                                        for j in sub.air_duct:
                                            sub.air_duct[j][1] = sub.air_duct[j][1]-speed_sub
                                        for j in sub.door:
                                            sub.door[j][1] = sub.door[j][1]-speed_sub
                                        for j in sub.lower_body:
                                            sub.lower_body[j][1] = sub.lower_body[j][1]-speed_sub
                                        sub.circle1 = [sub.circle1[0], sub.circle1[1]-speed_sub]
                                        sub.circle2 = [sub.circle2[0], sub.circle2[1]-speed_sub]  
                                else:
                                    if (sub.main_body['mp3'][0] +50) < 680 and  ((sub.main_body['mp1'][1] +sub.main_body['mp3'][1]) / 2) <= 225 :   
                                        for j in sub.main_body:
                                            sub.main_body[j][1] = sub.main_body[j][1]+speed_sub1
                                            sub.main_body[j][0] = sub.main_body[j][0]+speed_sub1
                                        for j in sub.propeller:
                                            sub.propeller[j][1] = sub.propeller[j][1]+speed_sub1
                                            sub.propeller[j][0] = sub.propeller[j][0]+speed_sub1
                                        for j in sub.top_body:
                                            sub.top_body[j][1] = sub.top_body[j][1]+speed_sub1
                                            sub.top_body[j][0] = sub.top_body[j][0]+speed_sub1
                                        for j in sub.air_duct:
                                            sub.air_duct[j][1] = sub.air_duct[j][1]+speed_sub1
                                            sub.air_duct[j][0] = sub.air_duct[j][0]+speed_sub1
                                        for j in sub.door:
                                            sub.door[j][1] = sub.door[j][1]+speed_sub1
                                            sub.door[j][0] = sub.door[j][0]+speed_sub1
                                        for j in sub.lower_body:
                                            sub.lower_body[j][1] = sub.lower_body[j][1]+speed_sub1
                                            sub.lower_body[j][0] = sub.lower_body[j][0]+speed_sub1         

                                        sub.circle1 = [sub.circle1[0], sub.circle1[1]+speed_sub1]
                                        sub.circle2 = [sub.circle2[0], sub.circle2[1]+speed_sub1]
                                        sub.circle1 = [sub.circle1[0]+speed_sub1, sub.circle1[1]]
                                        sub.circle2 = [sub.circle2[0]+speed_sub1, sub.circle2[1]]
                    
    if key==GLUT_KEY_RIGHT:
        if game_over == False and paused == False:
            for sub in submarines:
                if sub.num == 2:
                    if sub.control == True:
                        if sub.main_body['mp3'][0] + 50 < 680:  
                            if sub.gear == False:
                                for j in sub.main_body:
                                    sub.main_body[j][0] = sub.main_body[j][0]+speed_sub
                                for j in sub.propeller:
                                    sub.propeller[j][0] = sub.propeller[j][0]+speed_sub
                                for j in sub.top_body:
                                    sub.top_body[j][0] = sub.top_body[j][0]+speed_sub
                                for j in sub.air_duct:
                                    sub.air_duct[j][0] = sub.air_duct[j][0]+speed_sub
                                for j in sub.door:
                                    sub.door[j][0] = sub.door[j][0]+speed_sub
                                for j in sub.lower_body:
                                    sub.lower_body[j][0] = sub.lower_body[j][0]+speed_sub    
                                sub.circle1 = [sub.circle1[0]+speed_sub, sub.circle1[1]]
                                sub.circle2 = [sub.circle2[0]+speed_sub, sub.circle2[1]]
                            else:
                                if sub.main_body['mp3'][1] > -350 :  
                                    for j in sub.main_body:
                                        sub.main_body[j][1] = sub.main_body[j][1]-speed_sub1
                                        sub.main_body[j][0] = sub.main_body[j][0]+speed_sub1
                                    for j in sub.propeller:
                                        sub.propeller[j][1] = sub.propeller[j][1]-speed_sub1
                                        sub.propeller[j][0] = sub.propeller[j][0]+speed_sub1
                                    for j in sub.top_body:
                                        sub.top_body[j][1] = sub.top_body[j][1]-speed_sub1
                                        sub.top_body[j][0] = sub.top_body[j][0]+speed_sub1
                                    for j in sub.air_duct:
                                        sub.air_duct[j][1] = sub.air_duct[j][1]-speed_sub1
                                        sub.air_duct[j][0] = sub.air_duct[j][0]+speed_sub1
                                    for j in sub.door:
                                        sub.door[j][1] = sub.door[j][1]-speed_sub1
                                        sub.door[j][0] = sub.door[j][0]+speed_sub1
                                    for j in sub.lower_body:
                                        sub.lower_body[j][1] = sub.lower_body[j][1]-speed_sub1
                                        sub.lower_body[j][0] = sub.lower_body[j][0]+speed_sub1     
                                    sub.circle1 = [sub.circle1[0], sub.circle1[1]-speed_sub1]
                                    sub.circle2 = [sub.circle2[0], sub.circle2[1]-speed_sub1]
                                    sub.circle1 = [sub.circle1[0]+speed_sub1, sub.circle1[1]]
                                    sub.circle2 = [sub.circle2[0]+speed_sub1, sub.circle2[1]]  
    if key==GLUT_KEY_LEFT:
        if game_over == False and paused == False:
            for sub in submarines:
                if sub.num == 2:
                    if sub.control == True:
                        if (sub.main_body['mp1'][0] -35) > -680:  
                            if sub.gear == False:
                                if sub.main_body['mp3'][1] < -240 and sub.main_body['mp3'][0] < 450:
                                    pass
                                else:
                                    for j in sub.main_body:
                                        sub.main_body[j][0] = sub.main_body[j][0]-speed_sub
                                    for j in sub.propeller:
                                        sub.propeller[j][0] = sub.propeller[j][0]-speed_sub
                                    for j in sub.top_body:
                                        sub.top_body[j][0] = sub.top_body[j][0]-speed_sub
                                    for j in sub.air_duct:
                                        sub.air_duct[j][0] = sub.air_duct[j][0]-speed_sub
                                    for j in sub.door:
                                        sub.door[j][0] = sub.door[j][0]-speed_sub
                                    for j in sub.lower_body:
                                        sub.lower_body[j][0] = sub.lower_body[j][0]-speed_sub   
                                    sub.circle1 = [sub.circle1[0]-speed_sub, sub.circle1[1]]
                                    sub.circle2 = [sub.circle2[0]-speed_sub, sub.circle2[1]]
                            else:
                                if sub.main_body['mp3'][1] > -320 :  
                                    for j in sub.main_body:
                                        sub.main_body[j][1] = sub.main_body[j][1]-speed_sub1
                                        sub.main_body[j][0] = sub.main_body[j][0]-speed_sub1
                                    for j in sub.propeller:
                                        sub.propeller[j][1] = sub.propeller[j][1]-speed_sub1
                                        sub.propeller[j][0] = sub.propeller[j][0]-speed_sub1
                                    for j in sub.top_body:
                                        sub.top_body[j][1] = sub.top_body[j][1]-speed_sub1
                                        sub.top_body[j][0] = sub.top_body[j][0]-speed_sub1
                                    for j in sub.air_duct:
                                        sub.air_duct[j][1] = sub.air_duct[j][1]-speed_sub1
                                        sub.air_duct[j][0] = sub.air_duct[j][0]-speed_sub1
                                    for j in sub.door:
                                        sub.door[j][1] = sub.door[j][1]-speed_sub1
                                        sub.door[j][0] = sub.door[j][0]-speed_sub1
                                    for j in sub.lower_body:
                                        sub.lower_body[j][1] = sub.lower_body[j][1]-speed_sub1
                                        sub.lower_body[j][0] = sub.lower_body[j][0]-speed_sub1      
                                    sub.circle1 = [sub.circle1[0], sub.circle1[1]-speed_sub1]
                                    sub.circle2 = [sub.circle2[0], sub.circle2[1]-speed_sub1]
                                    sub.circle1 = [sub.circle1[0]-speed_sub1, sub.circle1[1]]
                                    sub.circle2 = [sub.circle2[0]-speed_sub1, sub.circle2[1]]                    

    glutPostRedisplay()

def mouseListener(button, state, x, y):
    global restart_game, paused, game_over

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        c_X, c_y = convert_coordinate(x, y)

        restart_center_x = -100  # Updated horizontal position
        restart_base_y = -350  # Updated vertical position
        restart_icon_width = 20  # Width of the icon (icon_size)
        restart_icon_height = 20  # Height of the icon (icon_size)


        if (restart_center_x - restart_icon_width // 2 <= c_X <= restart_center_x + restart_icon_width // 2) and \
           (restart_base_y - restart_icon_height // 2 <= c_y <= restart_base_y + restart_icon_height // 2):
            restart_game = True  # Set the restart flag

        pause_center_x = 0  # Updated horizontal position
        pause_base_y = -350  # Updated vertical position
        pause_icon_width = 20  # Same size as restart icon
        pause_icon_height = 20  # Same size as restart icon

        if (pause_center_x - pause_icon_width // 2 <= c_X <= pause_center_x + pause_icon_width // 2) and \
           (pause_base_y - pause_icon_height // 2 <= c_y <= pause_base_y + pause_icon_height // 2):
            if game_over == False:
                paused = not paused

        cancel_center_x = 100  # Updated horizontal position
        cancel_base_y = -350  # Updated vertical position
        cancel_icon_width = 20  # Same size as restart icon
        cancel_icon_height = 20  # Same size as restart icon


        if (cancel_center_x - cancel_icon_width // 2 <= c_X <= cancel_center_x + cancel_icon_width // 2) and \
           (cancel_base_y - cancel_icon_height // 2 <= c_y <= cancel_base_y + cancel_icon_height // 2):
            if paused == False:
                game_over = True

            

    glutPostRedisplay()  
   

def init():
    glClearColor(0,0,0,0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(104,	1,	1,	1000.0)

glutInit()
glutInitWindowSize(W_Width, W_Height)
glutInitWindowPosition(0, 0)
glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB) 

wind = glutCreateWindow(b"Submarine Saga")
init()
glutDisplayFunc(display)	
glutIdleFunc(animate)	
glutKeyboardFunc(keyboardListener)
glutSpecialFunc(specialKeyListener)
glutMouseFunc(mouseListener)
glutMainLoop()		