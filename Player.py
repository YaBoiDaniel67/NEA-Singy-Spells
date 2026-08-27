import pygame
import numpy as np

class Player():
    def __init__(self):
      self.smoothing = 0.3
      self.smoothed_x_change = 0.0
      self.mouse_lockX, self.mouse_lockY = 0, 0
      self.speed = 0.05
      self.pot_x, self.pot_y = 0, 0

    def Movement(self, xPos, yPos, world_map, player_rotation, keys, currently_turning):
      x, y = xPos, yPos
      self.pot_x, self.pot_y = 0, 0
      if keys[ord('a')]: #is key at index ord('a') currently being held down
        self.pot_x += np.sin(player_rotation)
        self.pot_y -= np.cos(player_rotation)
      if keys[ord('d')]: #is key at index ord('d') currently being held down 
        self.pot_x -= np.sin(player_rotation)
        self.pot_y += np.cos(player_rotation)
      if keys[ord('w')]: #is key at index ord('w') currently being held down
        self.pot_x += np.cos(player_rotation)
        self.pot_y += np.sin(player_rotation)
      if keys[ord('s')]: #is key at index ord('s') currently being held down
        self.pot_x -= np.cos(player_rotation)
        self.pot_y -= np.sin(player_rotation)
      length = np.sqrt(self.pot_x ** 2 + self.pot_y ** 2)
      if length > 0:
        self.pot_x, self.pot_y = self.pot_x / length, self.pot_y / length
      x, y = x + self.pot_x * self.speed, y + self.pot_y * self.speed
      if pygame.mouse.get_pressed()[2]:
        if currently_turning == False:
            pygame.mouse.get_rel()
            pygame.event.set_grab(True)
            currently_turning = True
            pygame.mouse.set_visible(False)
            self.mouse_lockX, self.mouse_lockY = pygame.mouse.get_pos()
        x_change = pygame.mouse.get_rel()[0]
        self.smoothed_x_change = (self.smoothed_x_change * self.smoothing) + x_change * (1 - self.smoothing)
        player_rotation += self.smoothed_x_change * 0.0025
        pygame.mouse.set_pos(self.mouse_lockX, self.mouse_lockY)
      else:
        currently_turning = False
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
      if not (world_map[int(x - 0.1)][int(y)] or world_map[int(x + 0.1)][int(y)] or world_map[int(x)][int(y - 0.1)] or world_map[int(x)][int(y + 0.1)]): #if the player is not about to move into a wall, their position updates
        xPos, yPos = x, y
      elif not (world_map[int(xPos - 0.1)][int(y)] or world_map[int(xPos + 0.1)][int(y)] or world_map[int(xPos)][int(y - 0.1)] or world_map[int(xPos)][int(y + 0.1)]): #if the x is about to move into a wall but the y is not, the y updates
        yPos = y
      elif not (world_map[int(x - 0.1)][int(yPos)] or world_map[int(x + 0.1)][int(yPos)] or world_map[int(x)][int(yPos - 0.1)] or world_map[int(x)][int(yPos + 0.1)]): #if the y is about to move into a wall but the x is not, the x updates
        xPos = x
      return xPos, yPos, player_rotation, currently_turning
      #checks whether the player has moved, and adjusts value acoordingly so they move in game space