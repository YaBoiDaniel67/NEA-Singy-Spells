import pygame
import numpy as np
import time

spells = {"Fireball": { #creates a dict that contain all spells and their corresponding melody ID
          "melody_ID": 0},
          "Star": {
             "melody_ID": 1}
}

def get_ray_angle(horizontal_res, pixels_per_degree, player_rotation, screenX):
   mouseX, mouseY = pygame.mouse.get_pos() #gets the mouse X coord on screen
   redundant_ray_angle = np.deg2rad((((mouseX / screenX) * horizontal_res) / pixels_per_degree) - 30) #calculates the angle of the ray the mouse is pointing on
   ray_angle = player_rotation + redundant_ray_angle #adds player rotation to this ray
   return ray_angle #returns the ray angle

class Spell():
  def __init__(self, damage, speed, x, y, ray_angle, texture, type): #intialises general variables for spell class
     self.damage = damage
     self.speed = speed
     self.x = x
     self.y = y
     self.ray_angle = ray_angle
     self.texture = texture
     self.type = type
     self.spawn_time = time.monotonic()

class Fireball(Spell):
   def spell_special(self, active_spells):
      return

class Star(Spell):
   def __init__(self, damage, speed, x, y, ray_angle, texture, type, copy):
      super().__init__(damage, speed, x, y, ray_angle, texture, type)
      self.copy = copy
      self.spawn_time = time.monotonic()

   def spell_special(self, active_spells):
      if time.monotonic() - self.spawn_time >= 3 and self.copy == False:
         active_spells.append(Star(10, 0.01, self.x, self.y, self.ray_angle - 0.524, self.texture, "projectile", True)) 
         active_spells.append(Star(10, 0.01, self.x, self.y, self.ray_angle + 0.524, self.texture, "projectile", True)) 
         self.copy = True

def find_spell(horizontal_res, pixels_per_degree, player_rotation, xPos, yPos, texture_dict, screenX, potential_melody, active_spells):
    if len(potential_melody) > 0: #if the players has sung a melody
      for spell_name, spell in spells.items(): #loops through all the spells
          if spell["melody_ID"] in potential_melody: #if that spell is the one the player sang
             match spell_name: #case statement to match the spell name to its spell
                   case "Fireball":
                     active_spells.append(Fireball(20, 0.01, xPos, yPos, get_ray_angle(horizontal_res, pixels_per_degree, player_rotation, screenX), texture_dict["Fireball"], "projectile")) #adds an instance of the fireball class to var.spells
                   case "Star":
                     active_spells.append(Star(10, 0.01, xPos, yPos, get_ray_angle(horizontal_res, pixels_per_degree, player_rotation, screenX), texture_dict["Star"], "projectile", False)) #adds an instance of the Star class to var.spells
             potential_melody.pop() #removes the value from var.potential_melody
    return active_spells, potential_melody
               

def draw_on_screen(frame, current_object, world_map, xPos, yPos, player_rotation, pixels_per_degree, vertical_res, half_vertical_res, horizontal_res, depth, active_spells):
   current_object.spell_special(active_spells)
   match current_object.type:
      case "projectile":
        current_object.x += np.cos(current_object.ray_angle) * current_object.speed #updates objects x position
        current_object.y += np.sin(current_object.ray_angle) * current_object.speed #updates objects y position
        if world_map[max(0, min(int(current_object.x), len(world_map) - 1))][max(0, min(int(current_object.y), len(world_map[0]) - 1))] != 0: #if the object if touching a wall
          active_spells.remove(current_object)
        angle_to_projectile_from_player = np.arctan2(current_object.y - yPos, current_object.x - xPos) #calculates the angle from the player to the projectile
        no_rotation_angle = angle_to_projectile_from_player - player_rotation #changes the angle so it is relative to where the player is facing
        no_rotation_angle = (no_rotation_angle + np.pi) % (2 * np.pi) - np.pi #shifts the angle between -pi and pi
        screen_column = int((np.rad2deg(no_rotation_angle) + 30) * pixels_per_degree) #calculates the column where the sprite centre should appear
        if 0 - current_object.texture.shape[0] < screen_column - (current_object.texture.shape[0] / 2) < horizontal_res: #if its on-screen
          distance = np.sqrt((current_object.x - xPos) ** 2 + (current_object.y - yPos)** 2) #calculates the distance of the projectile from the player
          height = int((vertical_res / (distance * np.cos(no_rotation_angle) + 1e-6)) * 0.2) #calculates the height of the sprite on screen
          width = height #gets the width, which is just the height
          top, bottom = max(0, half_vertical_res - height // 2), min(vertical_res, half_vertical_res + height // 2) #determines the top and bottom rows of the sprite in relations to the screen
          left, right = screen_column - width // 2, screen_column + width // 2 #determiens the left and right columns of the sprite in relation to the screen
          row = np.arange(top, bottom) #creates a numpy array containing all vertical rows to be drawn
          column = np.arange(left, right) #creates a numpy array containing all horizontal columns to be drawn
          tex_y_array = ((row - top) / height * current_object.texture.shape[1]).astype(int) #maps each screen row to a texture y row
          tex_x_array = ((column - left) / width * current_object.texture.shape[0]).astype(int) #maps each screen column to a texture x column
          for i, j in enumerate(column): #iterates over all columns where a sprite could be drawn
            if 0 <= j < horizontal_res: #if its on-screen
              if distance < depth[j]: #if it closer than the corresponding wall column
                tex_x = tex_x_array[i] #gets the texture column corresponding to this screen column
                tex_column = current_object.texture[tex_x, tex_y_array] #calculates all the colour values for this column
                visible_mask = np.all(tex_column != [1, 0, 0], axis = 1) #creates a mask to ignore the colour pre-defined as clear
                frame[j][row[visible_mask]] = tex_column[visible_mask] #applies the mask and writes the remaining values to frame
   return frame, active_spells #returns frame