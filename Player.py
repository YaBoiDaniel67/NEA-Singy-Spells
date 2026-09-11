import pygame
import numpy as np

class Player():
    def __init__(self):
      self.smoothing = 0.3
      self.smoothed_x_change = 0.0
      self.mouse_lockX, self.mouse_lockY = 0, 0
      self.speed = 0.05
      self.xPos, self.yPos = 1.1, 1.1
      self.rotation = 0
      self.turning = False

    def Movement(self, world_map, keys):
      x, y = self.xPos, self.yPos
      X_move, Y_move = 0, 0
      if keys[ord("a")]: #is key at index ord('a') currently being held down
        X_move += np.sin(self.rotation)
        Y_move -= np.cos(self.rotation)
      if keys[ord("d")]: #is key at index ord('d') currently being held down 
        X_move -= np.sin(self.rotation)
        Y_move += np.cos(self.rotation)
      if keys[ord("w")]: #is key at index ord('w') currently being held down
        X_move += np.cos(self.rotation)
        Y_move += np.sin(self.rotation)
      if keys[ord("s")]: #is key at index ord('s') currently being held down
        X_move -= np.cos(self.rotation)
        Y_move -= np.sin(self.rotation)
      length = np.sqrt(X_move ** 2 + Y_move ** 2) #gets the magnitude of the movement
      if length > 0: #if the player has moved
        X_move, Y_move = X_move / length, Y_move / length #normalises the movements
      x, y = x + X_move * self.speed, y + Y_move * self.speed
      if pygame.mouse.get_pressed()[2]:
        if self.turning == False:
            pygame.mouse.get_rel()
            pygame.event.set_grab(True)
            self.turning = True
            pygame.mouse.set_visible(False)
            self.mouse_lockX, self.mouse_lockY = pygame.mouse.get_pos()
        x_change = pygame.mouse.get_rel()[0]
        self.smoothed_x_change = (self.smoothed_x_change * self.smoothing) + x_change * (1 - self.smoothing)
        self.rotation += self.smoothed_x_change * 0.0025
        pygame.mouse.set_pos(self.mouse_lockX, self.mouse_lockY)
      else:
        self.turning = False
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
      if not (world_map[int(x - 0.1)][int(y)] or world_map[int(x + 0.1)][int(y)] or world_map[int(x)][int(y - 0.1)] or world_map[int(x)][int(y + 0.1)]): #if the player is not about to move into a wall, their position updates
        self.xPos, self.yPos = x, y
      elif not (world_map[int(self.xPos - 0.1)][int(y)] or world_map[int(self.xPos + 0.1)][int(y)] or world_map[int(self.xPos)][int(y - 0.1)] or world_map[int(self.xPos)][int(y + 0.1)]): #if the x is about to move into a wall but the y is not, the y updates
        self.yPos = y
      elif not (world_map[int(x - 0.1)][int(self.yPos)] or world_map[int(x + 0.1)][int(self.yPos)] or world_map[int(x)][int(self.yPos - 0.1)] or world_map[int(x)][int(self.yPos + 0.1)]): #if the y is about to move into a wall but the x is not, the x updates
        self.xPos = x
      #checks whether the player has moved, and adjusts value acoordingly so they move in game space