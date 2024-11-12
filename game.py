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
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Visualize");

        # Load background
        self.background = numpy.array(Image.open("test.jpg"));
        self.background = cv2.resize(self.background, (WIDTH, HEIGHT))
        self.background = numpy.transpose(self.background, (1, 0, 2))
        self.background_original = numpy.array(self.background)
        self.background_with_paths = numpy.array(self.background)

        self.screen.fill((0, 0, 0))
        self.screen.blit(pygame.surfarray.make_surface(self.background), (0, 0))

        self.fatals = [7, 5, 9, 5, 1]
        self.rescue_resources = [5, 2, 3, 4, 1]
        self.victim_needs = [2, 4, 5, 3, 1]

        # Rescue teams and victims position
        self.res = []
        self.vic = []

        # Resulting path    
        self.paths = []

        # Time controller
        self.time_unit = 0;
        self.start_time_window = time.time();
        self.time_window = 0.05;
        self.start_draw_time = -1;

    def draw_box(self, box, colour):
        boxX, boxY = box
        pygame.draw.rect(self.screen, colour, (boxX - 2, boxY - 2, 4, 4));
    
    def draw_paths(self):
        for path in self.paths:
            if path is not None:
                for cell in path:
                    self.draw_box([cell[0], cell[1]], colour = (255, 0, 255))

    def draw_res_vic(self):
        for single_res in self.res:
            self.draw_box([single_res[0], single_res[1]], colour = (0, 255, 0))
        for single_vic in self.vic:
            self.draw_box([single_vic[0], single_vic[1]], colour = (0, 0, 255))

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
                            single_vic_index = self.vic.index(self.res[single_res_index])

                            if self.victim_needs[single_vic_index] > self.rescue_resources[single_res_index]:
                                self.victim_needs[single_vic_index] -= self.rescue_resources[single_res_index];
                                del self.res[single_res_index]
                                del self.rescue_resources[single_res_index]
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
                if key == 's':
                    self.res.append([mouse_x, mouse_y]);
                    self.paths.append(None)
                if key == 'e':
                    self.vic.append([mouse_x, mouse_y])
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

def main_loop(queue):
    pygame.init()

    algo_thres = Process(target=algo, args=(queue, ), daemon=True);
    algo_thres.start()
    
    gui = Gui()
    
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
            print(res, vic, fatals, rescue_resources, victim_needs)
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
            print("start")
            res = numpy.array(res);
            vic = numpy.array(vic);

            # print(res, vic)
            # res = numpy.concatenate([res[:, 1:], res[:, :1]], axis = 1).tolist();
            # vic = numpy.concatenate([vic[:, 1:], vic[:, :1]], axis = 1).tolist();
            #print(res.shape, vic.shape)

            paths = helper.solve_for_paths(groundMapModel, res, vic, fatals, rescue_resources, victim_needs);
            print("end")
            queue.put([False, paths])
            is_running_algo = False
            print("ye")

if __name__ == "__main__": 
    queue = Queue()
    main_loop_thread = Process(target=main_loop, args=(queue, ));
    main_loop_thread.start()
