import numpy as np
import time

def sort_object_list(playerX, playerY, on_screen_objects): #a merge sort
   if len(on_screen_objects) <= 1: #if the list is split down into one element, or the original input had 1 element
      return on_screen_objects #returns this version of the list
   left_list = on_screen_objects[:len(on_screen_objects) // 2] #creates a sublist that contains the elft half of list elements and the middle value
   right_list = on_screen_objects[len(on_screen_objects) // 2:] #creates a sublist that contains the right half of list elements
   sorted_left = sort_object_list(playerX, playerY, left_list) #calls the subroutine on this split up left list
   sorted_right = sort_object_list(playerX, playerY, right_list) #calls the subroutine on this split up right list

   sorted_objects = []
   left_count, right_count = 0, 0
   while left_count < len(sorted_left) and right_count < len(sorted_right): #while there are still values to compare in both lists
      if np.sqrt((sorted_left[left_count].x - playerX) ** 2 + (sorted_left[left_count].y - playerY) ** 2) >= np.sqrt((sorted_right[right_count].x - playerX) ** 2 + (sorted_right[right_count].y - playerY) ** 2): #if the item at index left count in sorted left is closer to the plyaer than the one in sorted right
         sorted_objects.append(sorted_left[left_count]) #adds that item to sorted objects
         left_count += 1 #adds 1 to left count so next index is checked next run
      else:
         sorted_objects.append(sorted_right[right_count]) #adds the item in sorted right at index right count to sorted objects
         right_count += 1 #adds 1 to the right index so next index is checked next run
   while left_count < len(sorted_left): #runs until all of sorted left has been checked
       sorted_objects.append(sorted_left[left_count]) #adds the item in sorted left at index left count to sorted objects
       left_count +=1 #adds 1 to the left index so next index is checked next run
   while right_count < len(sorted_right): #runs until all of sorted right has been checked
       sorted_objects.append(sorted_right[right_count]) #adds the item in sorted right at index right count to sorted objects
       right_count += 1 #adds 1 to the right index so next index is checked next run
   return sorted_objects
   
               

def draw_on_screen(frame, current_object, world_map, xPos, yPos, player_rotation, pixels_per_degree, vertical_res, half_vertical_res, horizontal_res, depth, active_spells, fov, player):
   current_object.special(active_spells)
   match current_object.type:
     case "Spell":
      match current_object.spell_type:
       case "projectile":
        current_object.x += np.cos(current_object.ray_angle) * current_object.speed #updates objects x position
        current_object.y += np.sin(current_object.ray_angle) * current_object.speed #updates objects y position
        current_map_index =  world_map[max(0, min(int(current_object.x), len(world_map) - 1))][max(0, min(int(current_object.y), len(world_map[0]) - 1))]
        if current_map_index != 0: #if the object if touching a wall
          match current_map_index:
             case 1:
                active_spells.remove(current_object)
             case 2:
              world_map[max(0, min(int(current_object.x), len(world_map) - 1))][max(0, min(int(current_object.y), len(world_map[0]) - 1))] = 0
        angle_to_projectile_from_player = np.arctan2(current_object.y - yPos, current_object.x - xPos) #calculates the angle from the player to the projectile
        no_rotation_angle = angle_to_projectile_from_player - player_rotation #changes the angle so it is relative to where the player is facing
        no_rotation_angle = (no_rotation_angle + np.pi) % (2 * np.pi) - np.pi #shifts the angle between -pi and pi
        screen_column = int((np.rad2deg(no_rotation_angle) + fov/2) * pixels_per_degree) #calculates the column where the sprite centre should appear
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
         screen_column = int((np.rad2deg(no_rotation_angle) + fov/2) * pixels_per_degree) #calculates the column where the sprite centre should appear
         distance = np.sqrt((current_object.x - xPos) ** 2 + (current_object.y - yPos)** 2) #calculates the distance of the object from the player
         height = int((vertical_res / (distance * np.cos(no_rotation_angle) + 1e-6)) * current_object.size) #calculates the height of the sprite on screen
         height = min(height, int(vertical_res * current_object.size)) #clamps the height so it doesnt include of-screen bits
         width = int((horizontal_res / (distance * np.cos(no_rotation_angle) + 1e-6)) * current_object.size) #gets the width
         width = min(width, int(horizontal_res * current_object.size)) #clamps the width so it doesnt include off-screen bits
         if -width < screen_column < horizontal_res + width: #if its on-screen
          drop = min(int(vertical_res / (2 * distance * np.cos(no_rotation_angle))), half_vertical_res)
          bottom = half_vertical_res + drop #determines the top and bottom rows of the sprite in relations to the screen
          top = half_vertical_res - height + drop
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

     case "enemy":
         current_object.update_animation()
         current_object.attack(player)
         current_object.move(player, world_map)
         angle_to_object_from_player = np.arctan2(current_object.y - yPos, current_object.x - xPos) #calculates the angle from the player to the object
         no_rotation_angle = angle_to_object_from_player - player_rotation #changes the angle so it is relative to where the player is facing
         no_rotation_angle = (no_rotation_angle + np.pi) % (2 * np.pi) - np.pi #shifts the angle between -pi and pi
         screen_column = int((np.rad2deg(no_rotation_angle) + fov/2) * pixels_per_degree) #calculates the column where the sprite centre should appear
         distance = np.sqrt((current_object.x - xPos) ** 2 + (current_object.y - yPos)** 2) #calculates the distance of the object from the player
         height = int((vertical_res / (distance * np.cos(no_rotation_angle) + 1e-6)) * current_object.size) #calculates the height of the sprite on screen
         height = min(height, int(vertical_res * current_object.size)) #clamps the height so it doesnt include of-screen bits
         width = int((horizontal_res / (distance * np.cos(no_rotation_angle) + 1e-6)) * current_object.size) #gets the width
         width = min(width, int(horizontal_res * current_object.size)) #clamps the width so it doesnt include off-screen bits
         if -width < screen_column < horizontal_res + width: #if its on-screen
          drop = min(int(vertical_res / (2 * distance * np.cos(no_rotation_angle))), half_vertical_res)
          bottom = half_vertical_res + drop #determines the top and bottom rows of the sprite in relations to the screen
          top = half_vertical_res - height + drop
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
   return frame, active_spells, world_map #returns frame