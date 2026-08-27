import pygame
import time

class Button():
   def __init__(self, screenX, screenY, surface, blit_surface, x_ratio, y_ratio, width_ratio, height_ratio, text):
      self.x = x_ratio * screenX #calculates how far along the screen this button is
      self.y = y_ratio * screenY #calculates how far along the screen this button is
      self.width, self.height = width_ratio * screenX, height_ratio * screenX #calculates the width and height of this button
      self.surface = surface
      self.blit_surface = blit_surface
      self.x_ratio = x_ratio
      self.y_ratio = y_ratio
      self.width_ratio = width_ratio
      self.height_ratio = height_ratio
      self.last_press = time.monotonic()
      self.text = text
      if self.text: #if any text was inputted during button creation
        self.text_font = pygame.font.SysFont(None, int(self.height / 4)) #intialises the font
        self.rendered_text = self.text_font.render(self.text, True, (0, 0, 0)) #renders this font with the inputted text

   def draw_to_screen(self):
      self.blit_surface.blit(pygame.transform.scale(self.surface, (self.width, self.height)), (self.x - self.width / 2, self.y - self.height / 2)) #draws the button to screen
      if self.text: #if this button has any text
         self.blit_surface.blit(self.rendered_text, (self.x - self.text_font.size(self.text)[0] / 2, self.y)) #draws the text to screen

   def check_pressed(self):
      pressed = False #sets pressed to false
      if pygame.mouse.get_pressed()[0] == True and time.monotonic() - self.last_press > 0.1: #if the button has been pressed and this button has not been pressed recently
        mouseX, mouseY = pygame.mouse.get_pos() #gets the x and y mouse positions
        if self.x - self.width / 2 <= mouseX <= self.x - self.width / 2 + self.width and self.y - self.height / 2 <= mouseY <= self.y - self.height / 2 + self.height: #if the x and y are both witihn the button texture
           pressed = True #sets pressed to true
           self.last_press = time.monotonic() #resets last press
      return pressed

   def resize(self, screenX, screenY): #used when screen hcnages size to resacle buttons
      self.width = screenX * self.width_ratio #re-initlaises base size and position variables
      self.height = screenX * self.height_ratio
      self.x = screenX * self.x_ratio
      self.y = screenY * self.y_ratio
      if self.text:
        self.text_font = pygame.font.SysFont(None, int(self.height / 4))
        self.rendered_text = self.text_font.render(self.text, True, (0, 0, 0))