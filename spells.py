import pygame
import numpy as np
import Variables as var
import Graphics.Texture_load as texture

spells = {"Fireball": { #creates a dict that contain all spells and their corresponding melody ID
          "melody_ID": 1
          }
}

def get_ray_angle():
   mouseX, mouseY = pygame.mouse.get_pos() #gets the mouse X coord on screen
   redundant_ray_angle = np.deg2rad(((mouseX / var.screenX * var.horizontal_res) / var.pixels_per_degree) - 30)
   projectile_angle = var.player_rotation + redundant_ray_angle
   return projectile_angle

class Fireball:
  def __init__(self):
     self.damage = 20.0
     self.speed = 0.01
     self.x = var.xPos
     self.y = var.yPos
     self.ray_angle = get_ray_angle()
     self.texture = texture.Fireball

def find_spell():
    if len(var.potential_melody) > 0:
      for spell_name, spell in spells.items():
          if spell["melody_ID"] in var.potential_melody:
             cast_spell(spell_name)

def cast_spell(spell_name):
   match spell_name:
      case "Fireball":
         spawn_fireball()
   print(var.potential_melody.pop())

def spawn_fireball():
   var.projectiles.append(Fireball())

def draw_on_screen(frame, current_object):
   angle_to_projectile_from_player = np.arctan2(current_object.y - var.yPos, current_object.x - var.xPos) #calculates the angle from the player to the projectile
   redundant_angle = angle_to_projectile_from_player - var.player_rotation #changes the angle so it is relative to where the player is facing
   redundant_angle = (redundant_angle + np.pi) % (2 * np.pi) - np.pi #shifts the angle between -pi and pi
   screenX = int((np.rad2deg(redundant_angle) + 30) * var.pixels_per_degree) #calculates the column where the sprite centre should appear
   if 0 <= screenX - current_object.texture.shape[0] / 2 < var.horizontal_res: #if its on-screen
    distance = np.sqrt((current_object.x - var.xPos) ** 2 + (current_object.y - var.yPos)** 2) #calculates the distance of the projectile from the player
    height = int((var.vertical_res / (distance * np.cos(redundant_angle) + 1e-6)) * 0.2) #calculates the height of the sprite on screen
    width = height #gets the width, which is just the height
    top, bottom = max(0, var.halfvertical_res - height // 2), min(var.vertical_res, var.halfvertical_res + height // 2) #determines the top and bottom rows of the sprite in relations to the screen
    left, right = screenX - width // 2, screenX + width // 2 #determiens the left and right columns of the sprite in relation to the screen
    row = np.arange(top, bottom) #creates a numpy array containing all vertical rows to be drawn
    column = np.arange(left, right) #creates a numpy array containing all horizontal columns to be drawn
    tex_y_array = ((row - top) / height * current_object.texture.shape[1]).astype(int) #maps each screen row to a texture y row
    tex_x_array = ((column - left) / width * current_object.texture.shape[0]).astype(int) #maps each screen column to a texture x column
    for i, j in enumerate(column): #iterates over all columns where sprite could be drawn
       if 0 <= j < var.horizontal_res: #if its on-screen
         if distance < var.depth[j]: #if it closer than the corresponding wall column
            tex_x = tex_x_array[i] #gets the texture column corresponding to this screen column
            tex_column = current_object.texture[tex_x, tex_y_array] #calculates all the colour values for this column
            visible_mask = np.all(tex_column != [1, 0, 0], axis = 1) #creates a mask to ignore the colour pre-defined as clear
            frame[j][row[visible_mask]] = tex_column[visible_mask] #applies the mask and writes the remaining values to frame
   return frame #returns frame