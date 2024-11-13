import pygame
from pygame.locals import *
import numpy
import cv2
from PIL import Image
import helper as helper
from multiprocessing import Process, Queue
import time
import sys
import matplotlib.pyplot as plt

#WIDTH, HEIGHT = 1280, 720
WIDTH, HEIGHT = 640, 480

# fatals = [7, 5, 9, 5, 1]
# rescue_resources = [5, 2, 3, 4, 1]
# victim_needs = [2, 4, 5, 3, 1]
# is_running_algo = False

# fatals = [7, 5, 9, 5, 1]
# rescue_resources = [5, 2, 3, 4, 1]
# victim_needs = [2, 4, 5, 3, 1]

# fatals = [7, 1]
# rescue_resources = [5, 9]
# victim_needs = [4, 6]

# fatals = [7]
# rescue_resources = [5]
# victim_needs = [4]

class Gui():
    def __init__(self, image_link, victim_position, fatals, victim_needs, rescue_position, rescue_resources, assembly_area):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Visualize");
        self.font = pygame.font.Font('freesansbold.ttf', 10)

        # Load background
        self.background = numpy.array(Image.open(image_link));
        self.background = cv2.resize(self.background, (WIDTH, HEIGHT))
        self.background = numpy.transpose(self.background, (1, 0, 2))
        self.background_original = numpy.array(self.background)
        self.background_with_paths = numpy.array(self.background)

        self.screen.fill((0, 0, 0))
        self.screen.blit(pygame.surfarray.make_surface(self.background), (0, 0))

        self.fatals = fatals
        self.rescue_resources = rescue_resources
        self.return_rescure_resources = []
        self.return_res = []
        self.victim_needs = victim_needs

        # Rescue teams and victims position
        self.res = rescue_position
        self.vic = victim_position
        self.assembly_area = assembly_area

        

        # Resulting path    
        self.paths = [None for i in self.res]

        # Time controller
        self.time_unit = 0;
        self.start_time_window = time.time();
        self.time_window = 0.05;
        self.start_draw_time = -1;

    def draw_box(self, box, colour, thickness):
        boxX, boxY = box
        pygame.draw.rect(self.screen, colour, (boxX - thickness, boxY - thickness, thickness * 2, thickness * 2));
    
    def draw_text(self, box, text):
        boxX, boxY = box
        text = self.font.render(text, True, (0, 255, 255))
        textRect = text.get_rect()
        textRect.bottomleft = (boxX + 10, boxY - 10)
        self.screen.blit(text, textRect)

    def draw_paths(self):
        for path in self.paths:
            if path is not None:
                for cell in path:
                    self.draw_box([cell[0], cell[1]], colour = (255, 0, 255), thickness = 2)

    def draw_res_vic(self):
        for index_single_vic, single_vic in enumerate(self.vic):
            self.draw_box([single_vic[0], single_vic[1]], colour = (0, 0, 255), thickness = 5) 
            self.draw_text([single_vic[0], single_vic[1]], f"fatals: {self.fatals[index_single_vic]}")
            self.draw_text([single_vic[0], single_vic[1] + 10], f"victim needs: {self.victim_needs[index_single_vic]}")
        for index_single_res, single_res in enumerate(self.res):
            self.draw_box([single_res[0], single_res[1]], colour = (0, 255, 0), thickness = 5)
            self.draw_text([single_res[0], single_res[1]], f"rescue resources: {self.rescue_resources[index_single_res]}")

    def main(self, queue):
        self.screen.blit(pygame.surfarray.make_surface(self.background), (0, 0))
        self.draw_paths()   
        self.draw_res_vic();
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if time.time() - self.start_time_window > self.time_window:
            self.time_unit = self.time_unit + 1;
            self.start_time_window = time.time()

            if not self.start_draw_time == -1:
                index = self.time_unit - self.start_draw_time
                #print(index)

                for single_res_index in range(len(self.res)):
                    if self.paths[single_res_index] is not None: 
                        if index < len(self.paths[single_res_index]):
                            self.res[single_res_index] = list(self.paths[single_res_index][index])
                        else:
                            
                            #print(self.res, self.vic, self.fatals, self.rescue_resources, self.victim_needs)
                            single_vic_index = self.vic.index(self.res[single_res_index])

                            # Del rescure team
                            if self.victim_needs[single_vic_index] > self.rescue_resources[single_res_index]:
                                self.victim_needs[single_vic_index] -= self.rescue_resources[single_res_index];

                                # self.return_res.append(self.res[single_res_index])
                                # self.return_rescure_resources.append(self.rescue_resources[single_res_index])
                                
                                del self.res[single_res_index]
                                del self.rescue_resources[single_res_index]
                                
                            # Del victim
                            elif self.victim_needs[single_vic_index] < self.rescue_resources[single_res_index]:
                                self.rescue_resources[single_res_index] -= self.victim_needs[single_vic_index]
                                del self.victim_needs[single_vic_index]
                                del self.fatals[single_vic_index]
                                del self.vic[single_vic_index]
                            else:
                                del self.res[single_res_index]
                                del self.vic[single_vic_index]
                                del self.fatals[single_vic_index]
                                del self.rescue_resources[single_res_index]
                                del self.victim_needs[single_vic_index]

                            #print(self.res, self.vic, self.fatals, self.rescue_resources, self.victim_needs)
                            queue.put([True, 
                                numpy.array(self.background),
                                self.res,
                                self.vic,
                                self.fatals,
                                self.rescue_resources,
                                self.victim_needs
                               ])
                            self.start_draw_time = -1
                            break;
                     
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                key = chr(event.key)
                if key == 'q':
                    pygame.quit()
                    sys.exit()
                # if key == 's':
                #     self.res.append([mouse_x, mouse_y]);
                #     self.paths.append(None)
                # if key == 'e':
                #     self.vic.append([mouse_x, mouse_y])
                if key == 'r':
                    queue.put([True, 
                            numpy.array(self.background),
                            self.res,
                            self.vic,
                            self.fatals,
                            self.rescue_resources,
                            self.victim_needs
                               ])
                    self.start_draw_time = -1
        pygame.display.update()

def main_loop(queue, image_link, victim_position, fatals, victim_needs, rescue_position, rescue_resources, assembly_area):
    pygame.init()

    algo_thres = Process(target=algo, args=(queue, ), daemon=True);
    algo_thres.start()
    
    gui = Gui(image_link, victim_position, fatals, victim_needs, rescue_position, rescue_resources, assembly_area)
    
    while True:
        #print("->")
        try:
            receiver = queue.get_nowait()
            #print("main loop keep loop !!!")
        except:
            gui.main(queue)
            continue;
        if len(receiver) == 7:
            #print("main loop keep loop !!!")
            queue.put(receiver)
            continue
        else:
            paths = receiver[1]
            gui.paths = paths
            gui.start_draw_time = gui.time_unit
        gui.main(queue)
    
def algo(queue):
    is_running_algo = False
    while True:
        try:
            receiver = queue.get_nowait()
            #print("algo have received!!!")
        except:
            continue;

        if len(receiver) == 7:
            is_running_algo, background, res, vic, fatals, rescue_resources, victim_needs = receiver
            #print(res, vic, fatals, rescue_resources, victim_needs)
        else:
            queue.put(receiver)
            continue

        if is_running_algo:
            # print(background.shape)
            groundMapModel = helper.buildMap(background)
            #print(groundMapModel)
            groundMapModel = numpy.repeat(groundMapModel.reshape(groundMapModel.shape[0], groundMapModel.shape[1], 1), 3, axis=2)
            #print(groundMapModel)
            groundMapModel = helper.turn_image_to_binary(groundMapModel, 1)
            # #print(groundMapModel)
            #print("start")
            if len(receiver) == 7:
                res = numpy.array(res);
                vic = numpy.array(vic);

                # print(res, vic)
                # res = numpy.concatenate([res[:, 1:], res[:, :1]], axis = 1).tolist();
                # vic = numpy.concatenate([vic[:, 1:], vic[:, :1]], axis = 1).tolist();
                #print(res.shape, vic.shape)

                paths = helper.solve_for_paths(groundMapModel, res, vic, fatals, rescue_resources, victim_needs);
                #print("end")
                queue.put([False, paths])
            is_running_algo = False
            #print("ye")

def run(image_link, victim_position, fatals, victim_needs, rescue_position, rescue_resources, assembly_area):
    """
        Run finding path algorithm
        Args:
            image_link: Link to the background image
            victim_position: Position of victims, data type: 2d list, shape (number of victims, position)
            fatals: Measure how bad the victim get injured, data type: 1d list, shape (number of victims)
            victim_needs: Measure how many rescue resources the victim need, data type: 1d list, shape (number of victims)
            rescue_position: Position of rescue teams, data type: 2d list, shape (number of rescue teams, position)
            rescue_resources: Measure how many rescue resources the rescue team have, data type: 1d list, shape (number of rescue teams)
            assembly_area: Position of the area which the rescue team must bring to when there are no space left in the boat: 1d list, shape (position)
    """
    queue = Queue()
    main_loop_thread = Process(target=main_loop, args=(queue, image_link, victim_position, fatals, victim_needs, rescue_position, rescue_resources, [assembly_area]));
    main_loop_thread.start()

if __name__ == '__main__':
    run("test.jpg", [[20, 20], [60, 60]], [7, 1], [4, 6], [[100, 50], [400, 400]], [5, 9], [20, 600])
