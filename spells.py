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

def get_ray_angle(horizontal_res, pixels_per_degree, player_rotation, screenX, fov):
   mouseX, mouseY = pygame.mouse.get_pos() #gets the mouse X coord on screen
   redundant_ray_angle = np.deg2rad((((mouseX / screenX) * horizontal_res) / pixels_per_degree) - fov/2) #calculates the angle of the ray the mouse is pointing on
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
     self.type = "Spell"
     self.spell_type = type
     self.size = size
     self.spawn_time = time.monotonic()

  def detect_hit(self, enemy_list, on_screen_objects):
     for i in range(len(enemy_list)):
        if np.sqrt((self.x - enemy_list[i].x) ** 2 + (self.y - enemy_list[i].y) ** 2) < self.size / 2 + enemy_list[i].size / 2:
           enemy_list[i].take_damage(self.damage, enemy_list, on_screen_objects)
           break

class Fireball(Spell):
   def special(self, on_screen_objects):
      return

class Star(Spell):
   def __init__(self, damage, speed, x, y, ray_angle, texture, type, size, copy):
      super().__init__(damage, speed, x, y, ray_angle, texture, type, size) #initialises all variables from the spell class
      self.copy = copy
      self.spawn_time = time.monotonic()

   def special(self, on_screen_objects):
      if time.monotonic() - self.spawn_time >= 3 * (0.01 / self.speed) and self.copy == False:
         on_screen_objects.append(Star(self.damage, self.speed, self.x, self.y, self.ray_angle - 0.524, self.texture, "projectile", self.size, True)) #sends of a star slightly left of the current one
         on_screen_objects.append(Star(self.damage, self.speed, self.x, self.y, self.ray_angle + 0.524, self.texture, "projectile", self.size, True)) #sends of a star slightly right of the current one
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

   def special(self, on_screen_objects):
      if np.sqrt((self.spawnX - self.x) ** 2 + (self.spawnY - self.y) ** 2) - self.last_spawn_distance >= self.spacing:
         self.last_spawn_distance = np.sqrt((self.spawnX - self.x) ** 2 + (self.spawnY - self.y) ** 2)
         on_screen_objects.append(self.ground_object(self.damage, 0, self.x, self.y, self.ray_angle, self.ground_object_texture, "ground_object", self.size, self.ground_object_lifespan))

class ground_cactus(Spell):
   def __init__(self, damage, speed, x, y, ray_angle, texture, type, size, lifespan):
      super().__init__( damage, speed, x, y, ray_angle, texture, type, size)
      self.lifespan = lifespan
      self.spawn_time = time.monotonic()

   def special(self, on_screen_objects):
      return


def find_spell(horizontal_res, pixels_per_degree, player, texture_dict, screenX, potential_melody, on_screen_objects, fov):
    if len(potential_melody) > 0: #if the player has sung a melody
      for spell_name, spell in spells.items(): #loops through all the spells
          if spell["melody_ID"] in potential_melody: #if that spell is the one the player sang
             match spell_name: #case statement to match the spell name to its spell
                   case "Fireball":
                     on_screen_objects.append(Fireball(20, 0.1, player.xPos, player.yPos, get_ray_angle(horizontal_res, pixels_per_degree, player.rotation, screenX, fov), texture_dict["Fireball"], "projectile", 1)) #adds an instance of the fireball class to var.spells
                   case "Star":
                     on_screen_objects.append(Star(10, 0.05, player.xPos, player.yPos, get_ray_angle(horizontal_res, pixels_per_degree, player.rotation, screenX, fov), texture_dict["Star"], "projectile", 0.5, False)) #adds an instance of the Star class to var.spells
                   case "Ground_cacti":
                     on_screen_objects.append(Invis_Projectile(10, 0.05, player.xPos, player.yPos, get_ray_angle(horizontal_res, pixels_per_degree, player.rotation, screenX, fov), texture_dict["Invis_texture"], "projectile", 0.5, 10, ground_cactus, texture_dict["cactus"], 0.5))
             potential_melody.pop() #removes the value from var.potential_melody
    return on_screen_objects, potential_melody