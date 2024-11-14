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

def BFS(image, start):
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
    cost_matrix = [[1e9 for i in range(image.shape[1])] for i in range(image.shape[0])]
    visited = np.full(image.shape, False)

    def valid_move(position):
        for i in range(2):
            if position[i] >= image.shape[i] or position[i] < 0:
                return False;

        if image[position] == WALL or visited[position] == True:
            return False;
        return True

    ### BFS algorithm ###
    visited[start] = True
    heapq.heappush(potential_nodes, (0, recent));
    while(len(potential_nodes) != 0):
        recent_cost, recent = heapq.heappop(potential_nodes)
        cost_matrix[recent[0]][recent[1]] = min(cost_matrix[recent[0]][recent[1]], recent_cost)

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
                heapq.heappush(potential_nodes, (recent_cost + move_cost, next_move))
                previous_move[next_move[0]][next_move[1]] = recent;
                visited[next_move] = True

    # ### Trace Back ###
    # while(recent != start):
    #     path = [recent] + path;
    #     recent = previous_move[recent[0]][recent[1]]
    # path = [recent] + path

    return cost_matrix, previous_move;

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
    #print(image.shape)
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
        return 1e9, [], visited

    ### Trace Back ###
    while(recent != start):
        path = [recent] + path;
        recent = previous_move[recent[0]][recent[1]]
    path = [recent] + path

    return recent_cost, path, visited;

def theta_aristek(image, start, finish, heuristic):
    parent = np.array([[None for i in range(image.shape[1])] for i in range(image.shape[0])])
    gScore = np.array([[1e9 for i in range(image.shape[1])] for i in range(image.shape[0])])
    
    class custom_heap:
        def __init__(self):
            self.list = []
        def __contains__(self, item):
            return (item in self.list)
        def pop(self):
            return heapq.heappop(self.list)[1]
        def insert(self, node, distance):
            heapq.heappush(self.list, (distance, node))
        def empty(self):
            return (len(self.list) == 0)
    
    open = custom_heap()

    def c(p1, p2):
        return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def main(start, goal):
        # This main loop is the same as A*
        gScore[start] = 0
        parent[start] = start
        # Initializing open and closed sets. The open set is initialized 
        # with the start node and an initial cost
        
        open.insert(start, gScore[start] + heuristic(start, goal))
        # gScore[node] is the current shortest distance from the start node to node
        # heuristic(node) is the estimated distance of node from the goal node
        # there are many options for the heuristic such as Euclidean or Manhattan 

        def valid_move(position):
            for i in range(2):
                if position[i] >= image.shape[i] or position[i] < 0:
                    return False;

            if image[position] == WALL or visited[position] == True:
                return False;
            return True

        visited = np.full(image.shape, False)
        visited[start] = True
        while open.empty() == False:
            s = open.pop()
            if s == goal:
                return gScore[s], reconstruct_path(s)
            visited[s] = True
            next_moves = [
                (s[0], s[1] + 1),
                (s[0] + 1, s[1]),
                (s[0], s[1] - 1),
                (s[0] - 1, s[1])
            ]

            for neighbor in next_moves:
                if valid_move(neighbor):
                    if visited[neighbor] == False:
                        update_vertex(s, neighbor, goal)
        return 1e9, None
                
        
    def update_vertex(s, neighbor, goal):
        # This part of the algorithm is the main difference between A* and Theta*
        if line_of_sight(parent[s], neighbor):
            # If there is line-of-sight between parent[s] and neighbor
            # then ignore s and use the path from parent[s] to neighbor 
            if gScore[parent[s]] + c(parent[s], neighbor) < gScore[neighbor]:
                # c(s, neighbor) is the Euclidean distance from s to neighbor
                gScore[neighbor] = gScore[parent[s]] + c(parent[s], neighbor)
                parent[neighbor] = parent[s]
                open.insert(neighbor, gScore[neighbor] + heuristic(neighbor, goal))
        else:
            # If the length of the path from start to s and from s to 
            # neighbor is shorter than the shortest currently known distance
            # from start to neighbor, then update node with the new distance
            if gScore[s] + c(s, neighbor) < gScore[neighbor]:
                gScore[neighbor] = gScore[s] + c(s, neighbor)
                parent[neighbor] = s
                open.insert(neighbor, gScore[neighbor] + heuristic(neighbor, goal))
        
    def reconstruct_path(s):
        total_path = [s]
        # This will recursively reconstruct the path from the goal node 
        # until the start node is reached
        if parent[s] != s:
            total_path = reconstruct_path(parent[s]) + total_path
        return total_path
        
    def line_of_sight(node1, node2):
        x0 = node1[0];
        y0 = node1[1];
        x1 = node2[0];
        y1 = node2[1];
        dx = abs(x1 - x0);
        dy = -abs(y1 - y0);

        sX = -1;
        sY = -1;
        if(x0 < x1):
            sX = 1;

        if(y0 < y1):
            sY = 1;


        e = dx + dy;
        while(True):
            point = (int(x0), int(y0));
            if(image[point] == WALL):
                return False;

            if(x0 == x1 and y0 == y1):
                return True;

            e2 = 2 * e;
            if(e2 >= dy):
                if(x0 == x1):
                    return True;
                e += dy;
                x0 += sX;

            if(e2 <= dx):
                if(y0 == y1):
                    return True;
                e += dx;
                y0 += sY;
    cost, path = main(start=start, goal=finish)
    real_paths = []
    def draw_bigger(first_axis, second_axis, swap = False):
        # first_axis always longer than second axis
        line_path = []
        for x in range(first_axis[0], first_axis[1], 1 if first_axis[0] < first_axis[1] else -1):
            y = int(second_axis[0] + (x - first_axis[0]) / (first_axis[1] - first_axis[0]) * (second_axis[1] - second_axis[0]))
            if swap:
                line_path.append((y, x));
            else:
                line_path.append((x, y));

        return line_path
    def line(p1, p2):
        if(abs(p1[0] - p2[0]) > abs(p1[1] - p2[1])):
            return draw_bigger((p1[0], p2[0]), (p1[1], p2[1]), swap = False);
        else:
            return draw_bigger((p1[1], p2[1]), (p1[0], p2[0]), swap = True);
    if path != None:        
        for index in range(len(path) - 1):
            pre_point = path[index]
            nex_point = path[index + 1]
            # print("!!!")
            # print(pre_point, nex_point)
            # print(line(pre_point, nex_point))
            real_paths = real_paths + line(pre_point, nex_point)
        real_paths.append(path[len(path) - 1])
    else:
        real_paths = None
    return cost, real_paths, None

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

def solve_for_path_with_BFS(image, rescue_pos, victim_pos, fatals, rescue_resources, victim_needs):
    rescue_pos = [tuple(single_rescue_pos) for single_rescue_pos in rescue_pos]
    victim_pos = [tuple(single_victim_pos) for single_victim_pos in victim_pos]
    num_of_rescue_teams = len(rescue_pos);
    num_of_victims = len(victim_pos)
    costs_matrix = np.zeros((num_of_rescue_teams, num_of_victims))
    paths_matrix = [[None for i in range(num_of_victims)] for i in range(num_of_rescue_teams)]

    def trace_back(recent, start, previous_move):
        ### Trace Back ###
        path = []
        while(recent != start):
            path = [recent] + path;
            recent = previous_move[recent[0]][recent[1]]
        path = [recent] + path
        
        return path
    
    for i in range(len(rescue_pos)):
        costs_matrix_of_rescure_team, previous_move = BFS(image, rescue_pos[i])
        for j in range(len(victim_pos)):
            costs_matrix[i, j] = costs_matrix_of_rescure_team[victim_pos[j][0]][victim_pos[j][1]]
            paths_matrix[i][j] = trace_back(victim_pos[j], rescue_pos[i], previous_move)
            # if algorithm == "theta_aristek":
            #     costs_matrix[i, j], paths_matrix[i][j], _ = theta_aristek(image, rescue_pos[i], victim_pos[j], L1)
            # else:
            #     costs_matrix[i, j], paths_matrix[i][j], _ = a_aristek(image, rescue_pos[i], victim_pos[j], L1)

    #print(costs_matrix, paths_matrix)
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

def solve_for_paths(image, rescue_pos, victim_pos, fatals, rescue_resources, victim_needs, algorithm = "theta_aristek"):
    rescue_pos = [tuple(single_rescue_pos) for single_rescue_pos in rescue_pos]
    victim_pos = [tuple(single_victim_pos) for single_victim_pos in victim_pos]
    num_of_rescue_teams = len(rescue_pos);
    num_of_victims = len(victim_pos)
    costs_matrix = np.zeros((num_of_rescue_teams, num_of_victims))
    paths_matrix = [[None for i in range(num_of_victims)] for i in range(num_of_rescue_teams)]

    for i in range(len(rescue_pos)):
        for j in range(len(victim_pos)):
            if algorithm == "theta_aristek":
                costs_matrix[i, j], paths_matrix[i][j], _ = theta_aristek(image, rescue_pos[i], victim_pos[j], L1)
            else:
                costs_matrix[i, j], paths_matrix[i][j], _ = a_aristek(image, rescue_pos[i], victim_pos[j], L1)

            print(i, j, costs_matrix[i, j])

    #print(costs_matrix, paths_matrix)
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

def paths_for_return(image, rescue_pos, assembly_area):
    rescue_pos = [tuple(single_rescue_pos) for single_rescue_pos in rescue_pos]
    assembly_area = [tuple(assembly_area[0])]
    num_of_rescue_teams = len(rescue_pos);
    paths_matrix = [None for i in range(num_of_rescue_teams)]

    for i in range(len(rescue_pos)):
        _, paths_matrix[i], __ = theta_aristek(image, rescue_pos[i], assembly_area[0], L1)

    return paths_matrix