import sys
import os
import re
import random
import math
import pygame
from pygame.locals import *
from heapq import nlargest

class Series:
    def __init__(self, n):
        self.name = n

    data = {}
    path = ""
    important = False
    def print(self):
        print(self.name)
        print(self.data)

    def setRect(self, r):
        self.rect = r

    def setColor(self, c):
        self.color = c


class Text:
    def __init__(self, r, i):
        self.image = i
        self.rect = r
    box_rect = (0,0,0,0)
    dest_width = 0
    current_width = 0
    color = ()


def get_index_from_pos(pos, width, square_w, square_h):
    if(pos[0] > width):
        return 0;
    max_per_row = math.floor(width / square_w)
    y_level = math.floor(pos[1] / square_h)
    x_level = math.floor(pos[0] / square_w)
    #print("Found position : " + str((y_level * max_per_row + x_level)))
    return int(y_level * max_per_row + x_level)


def get_dir_size_MB(dir):
    total_size = 0
    if os.path.isdir(dir):
        for item in os.listdir(dir):
            file_size = os.path.getsize(dir + "\\" + item)
            file_size = int(file_size / 1024 / 1024)
            total_size += file_size
    return int(total_size)


def normalize_to_largest(dict):
    if(dict):
        largest = max(dict.values())
        #print("Largest size is : ", largest)
        for item in dict:
            if(dict[item] != 0):
                dict[item] = dict[item] / largest
    else:
        print("Error empty dict")
    return dict


def get_season_sizes(dir):
    season_data = {}
    if os.path.isdir(dir):
        for season_dir in os.listdir(dir):
            season_data[season_dir] = get_dir_size_MB(dir + "\\" + season_dir)
    season_data = normalize_to_largest(season_data)

    return season_data

def random_color():
    return (random.randint(0,255),random.randint(0,255),random.randint(0,255))





ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
print(ROOT_DIR)

series = []

for dir in os.listdir(ROOT_DIR):
    regex = re.compile(".*\\[")

    series_name = regex.match(dir)
    if (series_name):
        temp_series = Series(series_name[0][:-2])
        temp_data = {}
        temp_series.path = dir
        if dir[0] == "~":
            temp_series.important = True

        regex = re.compile("\\[(.*)\\]")
        args = regex.findall(dir)[0].split()
        extra_args = []

        # Settings args
        temp_data["type"] = args[0].lower()
        args.pop(0)
        for arg in args:
            if (arg[-1:].lower() == "p"):
                temp_data["resolution"] = arg.upper()
                args.pop
            elif (arg[0:4].lower() == "dual" or arg[0:5].lower() == "audio"):
                temp_data["dual_audio"] = True
            elif (arg[0:4].lower() == "flac" ):
                temp_data["audio_codec"] = "flac"
            elif (arg[0:3].lower() == "aac" ):
                temp_data["audio_codec"] = "aac"
            else:
                extra_args.append(arg)
        if (extra_args):
            temp_data["additional_args"] = extra_args

        total_size = 0
        if os.path.isdir(dir):
            for season_dir in os.listdir(dir):
                total_size += get_dir_size_MB(dir + "\\" + season_dir)


            temp_data["size_mb"] = total_size
            if total_size == 0:
                print("There are no files")
            if total_size > 1024:
                print("Total size is : " + str(total_size / 1024) + "GB")
        temp_series.data = temp_data
        series.append((temp_series))

total_library_size = 0
for s in series:
    total_library_size += s.data["size_mb"]
    s.print()

print("Total library size is : " + str(total_library_size / 1024) + " GB")

# Create width and height constants
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
GRID_WIDTH = WINDOW_WIDTH * .75
INDEX_WIDTH = WINDOW_WIDTH - GRID_WIDTH

index_rect = (GRID_WIDTH, 0, INDEX_WIDTH, WINDOW_HEIGHT)

# calc square size
size_sqrt = math.ceil(math.sqrt(len(series)))

square_width = math.floor(GRID_WIDTH / size_sqrt)
square_height = math.floor(WINDOW_HEIGHT / size_sqrt)
print(size_sqrt)

# Colors
BLUE = (43, 68, 255)
BLACK = (0, 0, 0)
GREEN = (32, 238, 189)
YELLOW = (255, 230, 0)
RED = (239, 71, 74)
WHITE = (255, 255, 255)
WHITE_A = (255,255,255, 165)
DARK_GREY = (58, 58, 58)
PURPLE = (163,86,234)

# Initialise all the pygame modules
pygame.init()
# Create a game window
game_window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0 , 32)
# Set title
pygame.display.set_caption("Explorer Visualizer")


# Creating rectangles
x_pos = 0
y_pos = 0

print("GRID WIDTH : ", GRID_WIDTH)
print("square_width : ", square_width)

for s in series:
    #print("current next size : ",x_pos + square_width)
    if x_pos + square_width <= GRID_WIDTH:
        s.setRect((Rect(x_pos, y_pos, square_width, square_height)))
        x_pos += square_width
    else:
        y_pos += square_height
        x_pos = 0
        s.setRect((Rect(x_pos, y_pos, square_width, square_height)))
        x_pos += square_width
    if s.data["type"] == "bd":
        s.setColor(BLUE)
    elif s.data["type"] == "dvd":
        s.setColor(PURPLE)
    elif s.data["type"] == "batch":
        s.setColor(RED)
    elif s.data["type"] == "tv":
        s.setColor(YELLOW)
    else:
        s.setColor(random_color())

# Preload Grid

active_index = 0

#Creating text
text_list = []
bars_list = []

font = pygame.font.SysFont(None, 24)
font_title = pygame.font.SysFont(None, 36)
img = font.render(series[active_index].name, True, WHITE)
text_rect = img.get_rect(center=(GRID_WIDTH+INDEX_WIDTH/2, 40))



game_running = True
# Game loop
while game_running:
    # Loop through all active events
    for event in pygame.event.get():
        # Close the program if the user presses the 'X'
        if event.type == pygame.QUIT:
            game_running = False
        elif event.type == MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            active_index = get_index_from_pos(pos, GRID_WIDTH, square_width, square_height)
            if active_index >= len(series):
                active_index = 0

            text_list = []
            img = font_title.render(series[active_index].name, True, WHITE)
            text_rect = img.get_rect(center=(GRID_WIDTH + INDEX_WIDTH / 2, 0))
            text_rect.y = 30
            text_list.append(Text(text_rect, img))
            y_val = 80

            for key, value in series[active_index].data.items():
                img = font.render((key + " : " + str(value)), True, WHITE)
                text_rect = img.get_rect(center=(GRID_WIDTH + INDEX_WIDTH / 2, 0))
                text_rect.y = y_val
                y_val += 20
                text_list.append(Text(text_rect, img))

            bars_list = []
            y_val = 300
            for key, value in get_season_sizes(series[active_index].path).items():
                img = font.render((key), True, WHITE)
                max_width = int(INDEX_WIDTH * 3 / 4)
                text_rect = img.get_rect()
                start_pos_x = GRID_WIDTH + INDEX_WIDTH/8
                box_rect = Rect(start_pos_x, y_val, 0, 70)
                text_rect.center = box_rect.center
                text_rect.x = start_pos_x + (10)
                text_rect.width = value * max_width
                y_val += 80
                t = Text(text_rect, img)
                t.color = random_color()
                t.box_rect = box_rect
                t.dest_width = text_rect.width
                bars_list.append(t)


    # Content here
    game_window.fill((0, 0, 0))
    for s in series:
        if s.important == True:
            s.setColor(random_color())
        pygame.draw.rect(game_window, s.color, s.rect)

    s = pygame.Surface((series[active_index].rect.width, series[active_index].rect.height), pygame.SRCALPHA)  # per-pixel alpha
    s.fill(WHITE_A)  # notice the alpha value in the color
    game_window.blit(s, (series[active_index].rect.x, series[active_index].rect.y))


    #Drawing active area
    pygame.draw.rect(game_window, DARK_GREY, index_rect)
    pygame.draw.rect(game_window, series[active_index].color, (GRID_WIDTH + INDEX_WIDTH/4, 800 , INDEX_WIDTH/2, 200))

    for t in text_list:
        game_window.blit(t.image, t.rect)

    for t in bars_list:

        pygame.draw.rect(game_window, BLACK, t.box_rect, width = 5)
        pygame.draw.rect(game_window, t.color, t.box_rect)
        if(t.box_rect.width < t.dest_width):
            t.box_rect.width += 6
		
        game_window.blit(t.image, t.rect)

    # Update our display

    pygame.display.update()

# Uninitialize all pygame modules and quit the program
pygame.quit()
sys.exit()
