import pygame
import numpy as np
import time

spells = {"Fireball": { #creates a dict that contain all spells and their corresponding melody ID
          "melody_ID": 0},
          "Star": {
             "melody_ID": 1},
          "Ground_cacti": {
             "melody_ID": 2}
}

def get_ray_angle(horizontal_res, pixels_per_degree, player_rotation, screenX):
   mouseX, mouseY = pygame.mouse.get_pos() #gets the mouse X coord on screen
   redundant_ray_angle = np.deg2rad((((mouseX / screenX) * horizontal_res) / pixels_per_degree) - 30) #calculates the angle of the ray the mouse is pointing on
   ray_angle = player_rotation + redundant_ray_angle #adds player rotation to this ray
   return ray_angle #returns the ray angle

class Spell():
  def __init__(self, damage, speed, x, y, ray_angle, texture, type, size): #intialises general variables for spell class
     self.damage = damage
     self.speed = speed
     self.x = x
     self.y = y
     self.ray_angle = ray_angle
     self.texture = texture
     self.type = type
     self.size = size
     self.spawn_time = time.monotonic()

class Fireball(Spell):
   def spell_special(self, active_spells):
      return

class Star(Spell):
   def __init__(self, damage, speed, x, y, ray_angle, texture, type, size, copy):
      super().__init__(damage, speed, x, y, ray_angle, texture, type, size)
      self.copy = copy
      self.spawn_time = time.monotonic()

   def spell_special(self, active_spells):
      if time.monotonic() - self.spawn_time >= 3 * (0.01 / self.speed) and self.copy == False:
         active_spells.append(Star(self.damage, self.speed, self.x, self.y, self.ray_angle - 0.524, self.texture, "projectile", self.size, True)) #sends of a star slightly left of the current one
         active_spells.append(Star(self.damage, self.speed, self.x, self.y, self.ray_angle + 0.524, self.texture, "projectile", self.size, True)) #sends of a star slightly right of the current one
         self.copy = True #sets copy to true so it doesnt spawn any more copies

class Invis_Projectile(Spell):
   def __init__(self, damage, speed, x, y, ray_angle, texture, type, size, ground_object_lifespan, ground_object, ground_object_texture, spacing):
      super().__init__(damage, speed, x, y, ray_angle, texture, type, size)
      self.spawnX, self.spawnY = x, y
      self.ground_object_lifespan = ground_object_lifespan
      self.ground_object = ground_object
      self.ground_object_texture = ground_object_texture
      self.spacing = spacing
      self.last_spawn_distance = 0

   def spell_special(self, active_spell):
      if np.sqrt((self.spawnX - self.x) ** 2 + (self.spawnY - self.y) ** 2) - self.last_spawn_distance >= self.spacing:
         self.last_spawn_distance = np.sqrt((self.spawnX - self.x) ** 2 + (self.spawnY - self.y) ** 2)
         active_spell.append(self.ground_object(self.damage, 0, self.x, self.y, self.ray_angle, self.ground_object_texture, "ground_object", self.size, self.ground_object_lifespan))

class ground_cactus(Spell):
   def __init__(self, damage, speed, x, y, ray_angle, texture, type, size, lifespan):
      super().__init__( damage, speed, x, y, ray_angle, texture, type, size)
      self.lifespan = lifespan
      self.spawn_time = time.monotonic()

   def spell_special(self, active_spell):
      return


def find_spell(horizontal_res, pixels_per_degree, player_rotation, xPos, yPos, texture_dict, screenX, potential_melody, active_spells):
    if len(potential_melody) > 0: #if the players has sung a melody
      for spell_name, spell in spells.items(): #loops through all the spells
          if spell["melody_ID"] in potential_melody: #if that spell is the one the player sang
             match spell_name: #case statement to match the spell name to its spell
                   case "Fireball":
                     active_spells.append(Fireball(20, 0.1, xPos, yPos, get_ray_angle(horizontal_res, pixels_per_degree, player_rotation, screenX), texture_dict["Fireball"], "projectile", 1)) #adds an instance of the fireball class to var.spells
                   case "Star":
                     active_spells.append(Star(10, 0.05, xPos, yPos, get_ray_angle(horizontal_res, pixels_per_degree, player_rotation, screenX), texture_dict["Star"], "projectile", 0.5, False)) #adds an instance of the Star class to var.spells
                   case "Ground_cacti":
                     active_spells.append(Invis_Projectile(10, 0.05, xPos, yPos, get_ray_angle(horizontal_res, pixels_per_degree, player_rotation, screenX), texture_dict["Invis_texture"], "projectile", 0.5, 10, ground_cactus, texture_dict["cactus"], 0.5))
             potential_melody.pop() #removes the value from var.potential_melody
    return active_spells, potential_melody

def sort_spell_list(playerX, playerY, active_spells):
   if len(active_spells) <= 1: #if the list it split down into one element, or the original input had 1 element
      return active_spells #returns this version of the list
   left_list = active_spells[:len(active_spells) // 2] #creates a sublist that contains the elft half of list elements and the middle value
   right_list = active_spells[len(active_spells) // 2:] #creates a sublist that contains the right half of list elements
   sorted_left = sort_spell_list(playerX, playerY, left_list) #calls the subroutine on this split up left list
   sorted_right = sort_spell_list(playerX, playerY, right_list) #calls the subroutine on this split up right list

   sorted_spells = []
   left_count, right_count = 0, 0
   while left_count < len(sorted_left) and right_count < len(sorted_right): #while there are still values to compare in both lists
      if np.sqrt((sorted_left[left_count].x - playerX) ** 2 + (sorted_left[left_count].y - playerY) ** 2) >= np.sqrt((sorted_right[right_count].x - playerX) ** 2 + (sorted_right[right_count].y - playerY) ** 2): #if the item at index left count in sorted left is closer to the plyaer than the one in sorted right
         sorted_spells.append(sorted_left[left_count]) #adds that item to sorted spell
         left_count += 1 #adds 1 to left count so next index is checked next run
      else:
         sorted_spells.append(sorted_right[right_count]) #adds the item in sorted right at index right count to sorted spells
         right_count += 1 #adds 1 to the right index so next index is checked next run
   while left_count < len(sorted_left): #runs until all of sorted left has been checked
       sorted_spells.append(sorted_left[left_count]) #adds the item in sorted left at index left count to sorted spells
       left_count +=1 #adds 1 to the left index so next index is checked next run
   while right_count < len(sorted_right): #runs until all of sorted right has been checked
       sorted_spells.append(sorted_right[right_count]) #adds the item in sorted right at index right count to sorted spells
       right_count += 1 #adds 1 to the right index so next index is checked next run
   return sorted_spells
   
               

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
          height = int((vertical_res / (distance * np.cos(no_rotation_angle) + 1e-6)) * current_object.size) #calculates the height of the sprite on screen
          min(height, vertical_res)
          width = int((horizontal_res / (distance * np.cos(no_rotation_angle) + 1e-6)) * current_object.size) #gets the width of the sprite on screen
          min(width, horizontal_res)
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
                visible_mask = ~np.all(tex_column == [1, 0, 0], axis = 1) #creates a mask to ignore the colour pre-defined as clear
                frame[j][row[visible_mask]] = tex_column[visible_mask] #applies the mask and writes the remaining values to frame
      case "ground_object":
         if time.monotonic() - current_object.spawn_time >= current_object.lifespan:
            active_spells.remove(current_object)
         angle_to_object_from_player = np.arctan2(current_object.y - yPos, current_object.x - xPos) #calculates the angle from the player to the object
         no_rotation_angle = angle_to_object_from_player - player_rotation #changes the angle so it is relative to where the player is facing
         no_rotation_angle = (no_rotation_angle + np.pi) % (2 * np.pi) - np.pi #shifts the angle between -pi and pi
         screen_column = int((np.rad2deg(no_rotation_angle) + 30) * pixels_per_degree) #calculates the column where the sprite centre should appear
         distance = np.sqrt((current_object.x - xPos) ** 2 + (current_object.y - yPos)** 2) #calculates the distance of the object from the player
         height = int((vertical_res / (distance * np.cos(no_rotation_angle) + 1e-6)) * current_object.size) #calculates the height of the sprite on screen
         height = min(height, vertical_res) #clamps the height so it doesnt include of-screen bits
         width = int((horizontal_res / (distance * np.cos(no_rotation_angle) + 1e-6)) * current_object.size) #gets the width
         width = min(width, horizontal_res) #clamps the width so it doesnt include off-screen bits
         if -width < screen_column < horizontal_res + width: #if its on-screen
          bottom = half_vertical_res + height #determines the top and bottom rows of the sprite in relations to the screen
          top = half_vertical_res
          left, right = screen_column - width // 2, screen_column + width // 2 #determiens the left and right columns of the sprite in relation to the screen
          row = np.arange(max(0, top), min(vertical_res, bottom)) #creates a numpy array containing all vertical rows to be drawn
          column = np.arange(left, right) #creates a numpy array containing all horizontal columns to be drawn
          tex_y_array = ((row - max(0, top)) / height * current_object.texture.shape[1]).astype(int) #maps each screen row to a texture y row
          tex_x_array = ((column - left) / width * current_object.texture.shape[0]).astype(int) #maps each screen column to a texture x column
          for i, j in enumerate(column): #iterates over all columns where a sprite could be drawn
            if 0 <= j < horizontal_res: #if its on-screen
              if distance < depth[j]: #if it closer than the corresponding wall column
                tex_x = tex_x_array[i] #gets the texture column corresponding to this screen column
                tex_column = current_object.texture[tex_x, tex_y_array] #calculates all the colour values for this column
                visible_mask = ~np.all(tex_column == [1, 0, 0], axis = 1) #creates a mask to ignore the colour pre-defined as clear
                frame[j][row[visible_mask]] = tex_column[visible_mask] #applies the mask and writes the remaining values to frame
         
   return frame, active_spells #returns frame