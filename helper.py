import pygame
import random
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import heapq
import cv2

def turn_image_to_binary(image, threshold):
    image = np.mean(image, axis = 2);
    image[image < threshold] = 0;
    image[image >= threshold] = 1;
    return image

def load_PIL_image(path):
    image = np.array(Image.open(path))[:, :, :3]
    return image

def L1(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
    #return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2);

WALL = 0;

def a_aristek(image, start, finish, heuristic_func):
    """
        image: (W, H) (row, col)
        start: (x, y)
        finish: (x, y)
    """
    image = np.array(image);

    recent = start
    recent_cost = 0
    potential_nodes = []
    previous_move = [[None for i in range(image.shape[1])] for i in range(image.shape[0])]
    visited = np.full(image.shape, False)

    def valid_move(position):
        for i in range(2):
            if position[i] >= image.shape[i] or position[i] < 0:
                return False;

        if image[position] == WALL or visited[position] == True:
            return False;
        return True

    ### A* algorithm ###
    visited[start] = True
    heapq.heappush(potential_nodes, (0, 0, recent));
    while(recent != finish and len(potential_nodes) != 0):
        heuristic_cost, recent_cost, recent = heapq.heappop(potential_nodes)

        next_moves = [(recent[0] - 1 + i, recent[1] - 1 + j) for i in range(3) for j in range(3) if (i != 1 or j != 1)]

        #print(next_moves)
        #break;

        # next_moves = [
        #     (recent[0], recent[1] + 1),
        #     (recent[0] + 1, recent[1]),
        #     (recent[0], recent[1] - 1),
        #     (recent[0] - 1, recent[1])
        # ]

        for next_move in next_moves:
            if valid_move(next_move):
                if recent[0] != next_move[0] and recent[1] != next_move[1]:
                    if image[next_move[0], recent[1]] == WALL or image[recent[0], next_move[1]] == WALL:
                        continue
                move_cost = (np.sqrt(2) if recent[0] != next_move[0] and recent[1] != next_move[1] else 1)
                heapq.heappush(potential_nodes, (recent_cost + move_cost + heuristic_func(recent, finish), recent_cost + move_cost, next_move));
                previous_move[next_move[0]][next_move[1]] = recent;
                visited[next_move] = True

    path = []
    if recent != finish:
        return -1, [], visited

    ### Trace Back ###
    while(recent != start):
        path = [recent] + path;
        recent = previous_move[recent[0]][recent[1]]
    path = [recent] + path

    return recent_cost, path, visited;

def buildMap(image):
  # Step 1: Gaussian Blurring
  blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
  # Step 2: Convert to Grayscale
  gray_image = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2GRAY)
  # Step 3: Canny Edge Detection
  edges = cv2.Canny(gray_image, threshold1=0, threshold2=20)
  # Step 4: Find and Draw Contours
  contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  # Create an empty black image for the contour map (black background)
  contour_map = np.zeros_like(gray_image)
  # Draw contours in white (255) on the black background
  cv2.drawContours(contour_map, contours, -1, (255), 1)  # Contour thickness = 1
  # Step 5: Morphological Operations (closing gaps in contours)
  kernel = np.ones((5, 5), np.uint8)
  morph_image = cv2.morphologyEx(contour_map, cv2.MORPH_CLOSE, kernel)
  groundMapModel = cv2.bitwise_not(morph_image)
  # Save or display the final black and white map
  return groundMapModel

def solve_for_paths(image, rescue_pos, victim_pos, fatals, rescue_resources, victim_needs):
    num_of_rescue_teams = len(rescue_pos);
    num_of_victims = len(victim_pos)
    costs_matrix = np.zeros((num_of_rescue_teams, num_of_victims))
    paths_matrix = [[None for i in range(num_of_rescue_teams)] for i in range(num_of_victims)]
    for i in range(len(rescue_pos)):
        for j in range(len(victim_pos)):
            costs_matrix[i, j], paths_matrix[i][j], _ = a_aristek(image, rescue_pos[i], victim_pos[j], L1)

    rescue_remain = [True for i in range(num_of_rescue_teams)]
    rescue_paths = [None for i in range(num_of_rescue_teams)]
    rescue_order = np.argsort(fatals)[::-1]
    for victim_index in rescue_order:
        victim_need = victim_needs[victim_index]
        rescue_cost_order = np.argsort(costs_matrix[:, victim_index].tolist());

        total_resource_for_the_victim = 0;
        for rescue_index in rescue_cost_order:
            if rescue_remain[rescue_index] == True:
                rescue_remain[rescue_index] = False
                rescue_resource = rescue_resources[rescue_index]

                rescue_paths[rescue_index] = paths_matrix[rescue_index][victim_index]

                total_resource_for_the_victim += rescue_resource
                if total_resource_for_the_victim > victim_need:
                    break;

    return rescue_paths