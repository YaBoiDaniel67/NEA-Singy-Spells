import pygame

class Button():
   def __init__(self, screenX, screenY, surface, blit_surface, x_ratio, y_ratio, width_ratio, height_ratio, text):
      self.x = x_ratio * screenX
      self.y = y_ratio * screenY
      self.width, self.height = width_ratio * screenX, height_ratio * screenX
      self.surface = surface
      self.blit_surface = blit_surface
      self.x_ratio = x_ratio
      self.y_ratio = y_ratio
      self.width_ratio = width_ratio
      self.height_ratio = height_ratio
      self.text = text
      if self.text:
        self.text_font = pygame.font.SysFont(None, int(self.height / 4))
        self.rendered_text = self.text_font.render(self.text, True, (0, 0, 0))

   def draw_to_screen(self):
      self.blit_surface.blit(pygame.transform.scale(self.surface, (self.width, self.height)), (self.x - self.width / 2, self.y - self.height / 2))
      if self.text:
         self.blit_surface.blit(self.rendered_text, (self.x - self.text_font.size(self.text)[0] / 2, self.y))

   def check_pressed(self):
      pressed = False
      if pygame.mouse.get_pressed()[0] == True:
        mouseX, mouseY = pygame.mouse.get_pos()
        if self.x - self.width / 2 <= mouseX <= self.x - self.width / 2 + self.width and self.y - self.height / 2 <= mouseY <= self.y - self.height / 2 + self.height:
           pressed = True
      return pressed

   def resize(self, screenX, screenY):
      self.width = screenX * self.width_ratio
      self.height = screenX * self.height_ratio
      self.x = screenX * self.x_ratio
      self.y = screenY * self.y_ratio