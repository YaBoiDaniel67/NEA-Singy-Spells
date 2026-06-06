import numpy as np
import pygame
import Graphics.Texture_load as textures
import Variables as var

def RayCast(display, xPos, yPos, frame, player_rotation):
    for i in range(var.horizontal_res): #loops through the amount of pixels horizontally across the screen
        x, y = xPos, yPos #creates a local copy of the player x and y coords
        player_redundant_ray_angle = np.deg2rad(i / var.scale_factor - 30) #calculates the angle for the current ray
        ray_angle = player_rotation + player_redundant_ray_angle #calculates the angle of each ray + the players current rotation to get a resultant angle of rotation for the ray
        sin, cos, correctional_cos = np.sin(ray_angle), np.cos(ray_angle), np.cos(player_redundant_ray_angle) #saves the sin and cosine values of ray_angle so they dont have be constatnly recalculated, correctional_cos is used to correct the fish-eye distortion caused by raycasting
        #this is done by dividing by the cosine of the difference between the current column angle and the middle angle
        frame[i][:] = textures.sky[int(np.rad2deg(ray_angle) % 359)][:] #calcualtes the angle in degrees between 0 and 360, maps this to a given pixel column in the sky bitmap
        while var.world_map[int(x)][int(y)] == 0: #repeats until a wall is found
            x, y = x + 0.01 * cos, y + 0.01 * sin #adds a bit to the x and y coords, multiplied by sin and cos so it moves in the same direction it was
        distance = abs((x - xPos) / cos) #calculates the distance of said wall from the player
        height = int(var.halfvertical_res / (distance * correctional_cos + 0.0001)) #calculates the height of the wall
        pix_x = int(x % 1 * 100) #calculates the x coord of the pixel on the bitmap
        if x % 1 < 0.02 or x % 1 > 0.98:
            pix_x =  int(y % 1 * 100) #if x is near a whole number, the horizontal coord needs to be the y coord
        pix_y = np.linspace(0, 100, height * 2) #gives all the y coords of the pixels in an ordered sequence
        shading = 0.2 + (height/var.halfvertical_res) #calculates the darkening of the wall
        if shading > 1:
            shading = 1 #corrects colours for very close up walls
        for current_y_pixel in range(height * 2 - 1):
            if var.halfvertical_res- height + current_y_pixel >= 0 and var.halfvertical_res- height + current_y_pixel < 2 * var.halfvertical_res: #if the pixel is within the height of the wall
              frame[i][var.halfvertical_res - height + current_y_pixel] = shading * textures.wall[pix_x][int(pix_y[current_y_pixel])] #sets the RGB colour values of the specific pixel, using the wall bitmap
        for j in range(var.halfvertical_res - height + 1): #loops through amount of pixels vertically across the screen, until it meets either the bottom of a wall or halfvres
            distance = (var.halfvertical_res/(var.halfvertical_res - j)) / correctional_cos #calculates the distance of the point from the player - division by correctional_cosine fixes distortion
            x, y = xPos + cos * distance, yPos + sin * distance #calculates the x and y postion of the given pixel
            pix_x, pix_y = int(x % 1 * 100), int(y % 1 * 100) #calculates pixel from the texture that is mapped to the specific point, using the non-integer part of the x and y coords. timsed by 2 so that player appears larger (for texture size 100 x 100 pixels)
            shading = 0.2 + 0.8 * (1 - j / var.halfvertical_res) #calculates the amount of shade applied, so further away pixels appear darker, adding to sense of depth
            frame[i][var.halfvertical_res * 2 - j - 1] = shading * textures.floor[pix_x][pix_y] #sets colour of the pixel using the RGB values of the pixel location on the floor bitmap
    display.blit(pygame.transform.scale(pygame.surfarray.make_surface(frame), (var.screenX, var.screenY)), (0, 0)) #draws the values stored in frame to the screen