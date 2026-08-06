import numpy as np
import pygame
import Graphics.Texture_load as textures
import Variables as var

def RayCast(display, xPos, yPos, frame, player_rotation):
    for i in range(var.horizontal_res): #loops through the amount of pixels horizontally across the screen
        x, y = xPos, yPos #creates a local copy of the player x and y coords
        player_redundant_ray_angle = np.deg2rad((i / var.pixels_per_degree) - 30) #calculates the angle for the current ray
        ray_angle = player_rotation + player_redundant_ray_angle #calculates the angle of each ray + the players current rotation to get a resultant angle of rotation for the ray
        sin, cos, correctional_cos = np.sin(ray_angle), np.cos(ray_angle), np.cos(player_redundant_ray_angle) #saves the sin and cosine values of ray_angle so they dont have be constatnly recalculated, correctional_cos is used to correct the fish-eye distortion caused by raycasting
        frame[i][:] = textures.sky[int(np.rad2deg(ray_angle) % 359)][:] #calculates how far round in deg (0 - 359) this sky column is, maps this frame index to a given pixel column in the sky bitmap
        while var.world_map[int(x)][int(y)] == 0: #repeats until a wall is found
            x, y = x + 0.01 * cos, y + 0.01 * sin #adds scaled direction vector values to x and y so it moves along the same line (the current ray)
        distance = abs((x - xPos) / cos) #calculates the distance of said wall from the player - distance is always positive
        height = int(var.vertical_res / (distance * correctional_cos + 0.0001)) #calculates the height of the wall (how many available wall pixels / how far away the wall is * correctional_cos to correct fish eye distortion, add small value to prevent division by 0)
        half_height = int(height / 2) #saved to variable to prevent unnecessary, repetative calculations
        pix_x = int((x % 1) * 100) #calculates the x coord of the pixel on the bitmap (size 100 x 100)
        if x % 1 > 0.99 or x % 1 < 0.01: #checks if non-int parts of x are near a whole number
            pix_x =  int((y % 1) * 100) #if x is near a whole number, the horizontal coord needs to be the y coord
        wall_top = max(0, var.halfvertical_res - half_height) #calculates the top of the wall
        wall_bottom = min(var.vertical_res, var.halfvertical_res + half_height) #calculate the bottom of the wall
        visible_height = wall_bottom - wall_top #calculates the height of a given wall that is on screen
        pix_column = np.arange(height) #creates an array of vertical points within wall
        shading = 0.2 + (height / var.halfvertical_res) #calculates the darkening of the wall, proportional to distance
        if shading > 1:
            shading = 1 #corrects shading for very close up walls
        pix_y = ((pix_column / height) * (textures.wall.shape[1])).astype(int) #creates a decimal between 0 and 1, scales that to fit the wall texture, and saves the int of that. Creates a list of the specific texture points for this slice
        cut_wall_texture = max(0, half_height - var.halfvertical_res) #calculates how much of the texture is cut off the top of the screen
        frame[i][wall_top : wall_bottom] = shading * textures.wall[pix_x][pix_y[cut_wall_texture : cut_wall_texture + visible_height]] #sets the RGB colour values of the specific column, using the wall bitmap
        pix_column = np.arange(var.halfvertical_res - half_height + 1)  #creates an array of all pixels vertically across screen where floor needs to be filled
        distance = (var.halfvertical_res / (var.halfvertical_res - pix_column)) / correctional_cos #creates an array of eahc pixels distance from the player
        x, y = xPos + cos * distance, yPos + sin * distance #creates arrays of the x and y position of each pixel
        pix_x, pix_y = ((x % 1) * 100).astype(int), ((y % 1) * 100).astype(int) #calculates eahc pixel from the texture that is mapped to each specific point in the array, using the non-integer part of the x and y coords (for texture size 100 x 100 pixels)
        shading = 0.2 + 0.8 * (1 - (pix_column / var.halfvertical_res)) #calculates the amount of shade applied, so further away pixels appear darker, adding to sense of depth
        frame[i][var.vertical_res - pix_column - 1] = shading[:, None] * textures.floor[pix_x, pix_y] #sets colour of the pixels using the RGB values of the pixel location on the floor bitmap
    display.blit(pygame.transform.scale(pygame.surfarray.make_surface(frame), (var.screenX, var.screenY)), (0, 0)) #draws the values stored in frame to the screen