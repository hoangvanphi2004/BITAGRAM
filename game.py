import pygame
from pygame.locals import *
import numpy
import cv2
from PIL import Image
import helper

WIDTH, HEIGHT = 1280, 720

fatals = [7, 5, 9, 5, 1]
rescue_resources = [5, 2, 3, 4, 1]
victim_needs = [2, 4, 5, 3, 1]

class Gui():
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Visualize");

        # Load background
        self.background = numpy.array(Image.open("test.jpg"));
        self.background = cv2.resize(self.background, (WIDTH, HEIGHT))
        self.background = numpy.transpose(self.background, (1, 0, 2))
        self.background_original = numpy.array(self.background)

        self.screen.fill((0, 0, 0))
        self.screen.blit(pygame.surfarray.make_surface(self.background), (0, 0))

        # Rescue teams and victims position
        self.res = []
        self.vic = []
    
    def draw_box(self, box, colour):
        boxX, boxY = box
        pygame.draw.rect(self.screen, colour, (boxX - 2, boxY - 2, 4, 4));

    def main(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                key = chr(event.key)
                if key == 'q':
                    pygame.quit()
                    exit()
                if key == 's':
                    self.res.append([mouse_x, mouse_y]);
                    self.draw_box([mouse_x, mouse_y], colour = (0, 255, 0))
                if key == 'e':
                    self.vic.append([mouse_x, mouse_y])
                    self.draw_box([mouse_x, mouse_y], colour = (0, 0, 255))
                if key == 'r':
                    groundMapModel = helper.buildMap(self.background)
                    groundMapModel[groundMapModel == 255] = 1;
                    paths = helper.solve_for_paths(groundMapModel, self.res, self.vic, fatals, rescue_resources, victim_needs);
                    
        pygame.display.update()

if __name__ == "__main__" :
    gui = Gui()
    while True:
        gui.main()