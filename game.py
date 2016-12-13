import simplegui, math, urllib2, time

RENDER_DEBUG = False
COLLISION_DEBUG = False

def pyth(sidea, sideb):
    return (sidea ** 2) + (sideb ** 2) ##no sqrt for efficiency

class TileMap:
    
    def __init__(self, url):
        self.csv_data = urllib2.urlopen(url).read()
        
        self.map_data = []
        
        lineno = 0
        last = None
        for char in self.csv_data:
            if lineno == len(self.map_data):
                self.map_data.append([])
                
            if char == "\n":
                lineno += 1
            elif char == "-" or char == ",":
                pass
            else:
                num = int(char)
                if last == "-":
                    num *= -1
                self.map_data[lineno].append(num)
            last = char
        self.textures = []
        
        self.texture_size = (32, 32)
        self.map_size = (len(self.map_data[0]), len(self.map_data))
        
        return self
    
    # Location is in block units, not pixels
    def is_inaccessible(self, location):
        # If a block occupies these places
        left = False
        right = False
        top = False
        bottom = False
        if location[0] == 0:
            left = False
        elif location[0] >= self.map_size[0]:
            right = False
        else:
            left = self.map_data[location[0] - 1][location[1]] > -1
            right = self.map_data[location[0] + 1][location[1]] > -1
        if location[1] == 0:
            top = False
        elif location[1] >= self.map_size[1]:
            bottom = False
        else:
            top = self.map_data[location[0]][location[1] - 1] > -1
            bottom = self.map_data[location[0]][location[1] + 1] > -1
        return not left and not right and not top and not bottom
    
class GameObject:
    
    def __init__(self, sprite):
        self.location = (0, 0) # Location of the anchor
        self.velocity = (0, 0)
        self.scale = (1, 1)
        self.anchor = (0.5, 0.5)
        self.size = (sprite.get_width(), sprite.get_height())
        self.rotation = 0
        self.fixed = False
        self.sprite = sprite
        self.name = ""
        return self
    
    def check_anchor(self):
        # Check that our anchor isn't broken
        assert (self.anchor[0] >= 0.0 and self.anchor[0] <= 1.0 and
                self.anchor[1] >= 0.0 and self.anchor[1] <= 1.0)
        
    # Location of the center of the game object in the game world
    def center_location(self):
        self.check_anchor()
        scaled_size = self.scaled_size()
        x = self.location[0] - (scaled_size[0] * (self.anchor[0] - 0.5))
        y = self.location[1] - (scaled_size[1] * (self.anchor[1] - 0.5))
        return (x, y)
        
    def scaled_size(self):
        return (self.size[0] * self.scale[0], self.size[1] * self.scale[1])
    
    def scaled_bounds(self):
        center_location = self.center_location()
        scaled_size = self.scaled_size()
        half_scaled_size = (scaled_size[0] / 2, scaled_size[1] / 2)
        
         ##scaling fix: +/- the entire scaled_size, not half of it.
        top_left = (center_location[0] - half_scaled_size[0],
                    center_location[1] - half_scaled_size[1])
        
        top_right = (center_location[0] + half_scaled_size[0],
                    center_location[1] - half_scaled_size[1])
        
        bottom_left = (center_location[0] - half_scaled_size[0],
                    center_location[1] + half_scaled_size[1])
        
        bottom_right = (center_location[0] + half_scaled_size[0],
                    center_location[1] + half_scaled_size[1])
        
        return (top_left, top_right, bottom_left, bottom_right)

class Game:
    
    games = []
    last_time = 0
    last_readout = 0
    updates = 0
    
    def checkCollisions(obj1, objects):
        obj1_bounds = obj1.scaled_bounds()
        obj1_o = obj1_bounds[0]
        obj1_s = obj1.scaled_size()
        
        if COLLISION_DEBUG and RENDER_DEBUG:
            print "OBJECT: \t" + obj1.name
            print "TOP_LEFT:\t" + str(obj1_bounds[0])
            print "TOP_RIGHT:\t" + str(obj1_bounds[1])
            print "BOTTOM_LEFT:\t" + str(obj1_bounds[2])
            print "BOTTOM_RIGHT:\t" + str(obj1_bounds[3])
            print "SCALED_SIZE:\t" + str(obj1_s)
            print

        
        for obj2 in objects:
            
            if objects.index(obj1) == objects.index(obj2):
                continue
           
            obj2_bounds = obj2.scaled_bounds()
            obj2_o = obj2_bounds[0]
            obj2_s = obj2.scaled_size() 
            
            if COLLISION_DEBUG and RENDER_DEBUG:
                print "OBJECT 2:\t" + obj2.name
                print "TOP_LEFT:\t" + str(obj2_bounds[0])
                print "TOP_RIGHT:\t" + str(obj2_bounds[1])
                print "BOTTOM_LEFT:\t" + str(obj2_bounds[2])
                print "BOTTOM_RIGHT:\t" + str(obj2_bounds[3])
                print "SCALED_SIZE:\t" + str(obj2_s)
                print

            if ((obj2_o[0] < obj1_o[0] + obj1_s[0] and
                 obj2_o[0] + obj2_s[0] > obj1_o[0]) and 
                (obj2_o[1] < obj1_o[1] + obj1_s[1] and 
                 obj2_o[1] + obj2_s[1] > obj1_o[1])):
                
                    # Find distances between shape1's edge and shape2's opposite edge
                    edge_differences = [
                        [obj2_o[0] - (obj1_o[0] + obj1_s[0]), 0, 0], # Left
                        [(obj2_o[0] + obj2_s[0]) - obj1_o[0], 0, 0], # Right               
                        [0, obj2_o[1] - (obj1_o[1] + obj1_s[1]), 0], # Top
                        [0, (obj2_o[1] + obj2_s[1]) - obj1_o[1], 0] # Bottom                        
                    ]
                    
                    if COLLISION_DEBUG:
                        print "----------------------------------"
                        print "POSSIBLE DIFFERENCES"
                        print "Left:\t" + str(edge_differences[0])
                        print "Right:\t" + str(edge_differences[1])
                        print "Top:\t" + str(edge_differences[0])
                        print "Bottom:\t" + str(edge_differences[1])                        
                        print
                        
                    ##use pythagoras to find final vector magnitudes and append them in (for later sorting)    
                    edge_differences[0][2] = pyth(edge_differences[0][0],edge_differences[0][1])
                    edge_differences[1][2] = pyth(edge_differences[1][0],edge_differences[1][1])
                    edge_differences[2][2] = pyth(edge_differences[2][0],edge_differences[2][1])
                    edge_differences[3][2] = pyth(edge_differences[3][0],edge_differences[3][1])
                    
                    edge_differences = sorted(edge_differences,key=lambda l:l[2]) ##sort by final vector length
                    
                    if COLLISION_DEBUG:
                        print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
                        print "SORTED DIFFERENCES"
                        print "0:\t" + str(edge_differences[0])
                        print "1:\t" + str(edge_differences[1])
                        print "2:\t" + str(edge_differences[0])
                        print "3:\t" + str(edge_differences[1])                        
                        print                
                        
                    mtv = (edge_differences[0]) ##pick smallest one
                    
                    if COLLISION_DEBUG:
                        print "Obj1:\t" + obj1.name + "\t" + "Obj2:\t" + obj2.name
                        print "Chosen Vector:\t" + str(mtv)
                        print

                    # Return collision boolean and translation vector
                        
                    return True, mtv or (0,0)
                
        return False, (0, 0)
    
    def physics(self, object):
        
        ## If you apply gravity before collision check, nonfixed objects can't push eachother.
        ## If you apply it after, nonfixed objects can push eachother into the platform below.
        ## Not sure how to fix.
        
        # Apply gravity and velocities
        object.velocity = (object.velocity[0] + self.gravity[0],
                           object.velocity[1] + self.gravity[1])
        object.location = (object.location[0] + object.velocity[0],
                           object.location[1] + object.velocity[1])
                        
        # Check collisions
        doesCollide, mtv = Game.checkCollisions(object, self.objects)
        if doesCollide:
            if abs(mtv[0]) > 0: ##remove x vel. if collides on x axis
                object.velocity = (0, object.velocity[1])
            if abs(mtv[1]) > 0: ##remove y vel. if collides on y axis (doesn't affect grav)
                object.velocity = (object.velocity[0], 0)                
            object.location = (object.location[0] + mtv[0], object.location[1] + mtv[1])
            
    def draw(canvas):
        Game.now_time = int(time.time())
        
        if Game.now_time > Game.last_time:
            Game.last_readout = Game.updates
            Game.updates = 0
        else:
            Game.updates += 1
        
        Game.last_time = Game.now_time
        
        for gameData in Game.games:
            game = gameData[0]
            canvas_for_game = gameData[1]
            if True: #canvas_for_game is canvas: FIXME: Always false
                game.internalDraw(canvas)
                
    def internalDraw(self, canvas):
        
        # Draw game objects
        for object in self.objects:
            # Perform physics
            if not object.fixed:
                self.physics(object)
            
            # Center the camera on this object if necessary
            if (object in self.objects and self.camera_center_object in self.objects and
                self.objects.index(object) == self.objects.index(self.camera_center_object)):
                # Set it to the center of the player
                center_point = object.center_location()
                center_point = (center_point[0] - (self.canvas_size[0] / 2),
                                center_point[1] - (self.canvas_size[1] / 2))
                
                max_camera_location = (self.world_size[0] - self.canvas_size[0],
                                       self.world_size[1] - self.canvas_size[1])
                
                # Put it back in the bounds of the world if necessary
                center_point = (0 if center_point[0] < 0 else center_point[0],
                                0 if center_point[1] < 0 else center_point[1])
                center_point = ((max_camera_location[0] if center_point[0] > max_camera_location[0]
                                 else center_point[0]),
                                (max_camera_location[1] if center_point[1] > max_camera_location[1]
                                 else center_point[1]))
                
                self.camera_location = (int(center_point[0]),
                                        int(center_point[1]))
                
            # Draw the sprite
            sprite = object.sprite
            source_center = (object.size[0] / 2, object.size[1] / 2)
            source_size = object.size
            center_dest = object.center_location()
            dest_size = object.scaled_size()
            dest_size = (int(dest_size[0]),
                         int(dest_size[1]))
            rotation = object.rotation
            
            # Shift the destination by the camera offset
            center_dest = (int(center_dest[0] - self.camera_location[0]),
                           int(center_dest[1] - self.camera_location[1]))
            
            if RENDER_DEBUG:
                print "Drawing image:"
                print "Source center:\t\t" 		+ str(source_center)
                print "Anchor:\t\t\t"			+ str(object.anchor)
                print "Source size:\t\t" 		+ str(source_size)
                print "Center destination:\t" 	+ str(center_dest)
                print "Destination size:\t" 	+ str(dest_size)
                print "Rotation:\t\t" 			+ str(rotation)
                print
            
            # Determine if any part of the texture will be on the screen
            lower_limit = (self.camera_location[0] - dest_size[0],
                           self.camera_location[1] - dest_size[1])
            upper_limit = (lower_limit[0] + self.canvas_size[0] + dest_size[0],
                           lower_limit[1] + self.canvas_size[1] + dest_size[1])
            
            #print center_dest[1], lower_limit[1]
            if True:#(center_dest[1] >= lower_limit[1] and center_dest[1] < upper_limit[1]):
                canvas.draw_image(sprite,
                                  source_center,
                                  source_size,
                                  center_dest,
                                  dest_size,
                                  rotation)
            else:
                pass#print lower_limit, upper_limit, center_dest
        self.custom_draw(canvas)
        
        # Draw FPS
        if self.show_fps:
            canvas.draw_text(str(Game.last_readout), (40, 40), 36, 'Blue')
    
    def load_map(self, tile_map):
        # Make sure that the map isn't bigger than the world
        map_pixel_size = (tile_map.texture_size[0] * tile_map.map_size[0],
                          tile_map.texture_size[1] * tile_map.map_size[1])
        assert map_pixel_size[0] <= self.world_size[0] and map_pixel_size[1] <= self.world_size[1]
        
        # Populate the game world
        for row_index in range(0, tile_map.map_size[1]):
            row = tile_map.map_data[row_index]
            for column_index in range(0, tile_map.map_size[0]):
                tile_number = row[column_index]
                if tile_number > -1:
                    texture = tile_map.textures[tile_number]
                    
                    tile_object = GameObject(texture)
                    tile_object.anchor = (0, 0)
                    tile_object.fixed = True
                    tile_object.location = (column_index * tile_map.texture_size[0],
                                            row_index * tile_map.texture_size[1])
                    
                    self.objects.append(tile_object)
                    
    def __init__(self, frame, custom_draw, canvas_size, world_size):
        # The world can't be smaller than the canvas
        assert (world_size[0] >= canvas_size[0] and
                world_size[1] >= canvas_size[1])
        
        self.objects = []
        self.custom_draw = custom_draw
        self.gravity = (0, 0.4)
        self.fixed = False
        
        self.canvas_size = canvas_size
        self.world_size = world_size
        
        self.camera_location = (0, 0) # The location that the camera has scrolled to
        self.camera_center_object = None # To be set to an object later on
        
        self.show_fps = True
        Game.games.append((self, frame))
        frame.set_draw_handler(Game.draw)
        return self
    
# Handler to draw on canvas
def draw(canvas):
    pass

ASSETS = "https://raw.githubusercontent.com/ahscpc/codeskulptor-game-engine/master/assets/"
CANVAS_SIZE = (640, 480)
GAME_SIZE = (1600, 980)

frame = simplegui.create_frame("Home", CANVAS_SIZE[0], CANVAS_SIZE[1])
frame.set_canvas_background("White")

PLAYER_SPEED = 4
JUMP_VELOCITY = -12

def keydown_handler(key):
    if key == simplegui.KEY_MAP["a"] or key == simplegui.KEY_MAP["left"]:
        player.velocity = (-PLAYER_SPEED, player.velocity[1])
    if key == simplegui.KEY_MAP["d"] or key == simplegui.KEY_MAP["right"]:
        player.velocity = (PLAYER_SPEED, player.velocity[1])
    if key == simplegui.KEY_MAP["d"] or key == simplegui.KEY_MAP["up"] or key == simplegui.KEY_MAP["space"]:
        player.velocity = (player.velocity[0], JUMP_VELOCITY)

def keyup_handler(key):
    if key == simplegui.KEY_MAP["a"] or key == simplegui.KEY_MAP["left"]:
        if player.velocity[0] == -PLAYER_SPEED:
            player.velocity = (0, player.velocity[1])
    if key == simplegui.KEY_MAP["d"] or key == simplegui.KEY_MAP["right"]:
        if player.velocity[0] == PLAYER_SPEED:
            player.velocity = (0, player.velocity[1]) 

frame.set_keydown_handler(keydown_handler)
frame.set_keyup_handler(keyup_handler)

game = Game(frame, draw, CANVAS_SIZE, GAME_SIZE)

images = {
    "stick_figure" 	: simplegui.load_image(ASSETS + "sprites/objects/stick.png"),
    "pink_rect" 	: simplegui.load_image(ASSETS + "sprites/objects/pink.png"),
    "dirt" 			: simplegui.load_image(ASSETS + "sprites/terrain/dirt.png"),
    "grass" 		: simplegui.load_image(ASSETS + "sprites/terrain/grass.png"),
    "stone" 		: simplegui.load_image(ASSETS + "sprites/terrain/stone.png"),
    }

player = None

def test_multiple_objects():
    test = GameObject(images["pink_rect"])
    test.name = "test"
    test.scale = (1, 1.0)
    test.location = (300, 0)
    test.velocity = (-1, 0)
    game.objects.append(test)

    test2 = GameObject(images["pink_rect"])
    test2.name = "test2"
    test2.scale = (0.3, 0.5)
    test2.location = (0, 0)
    test2.velocity = (3, 0)
    game.objects.append(test2)

    test3 = GameObject(images["pink_rect"])
    test3.name = "test3"
    test3.scale = (0.1, 0.1)
    test3.location = (275, -100)
    test3.velocity = (-.5, 0)
    game.objects.append(test3)

    platform = GameObject(images["pink_rect"])
    platform.location = (300, 300)
    platform.name = "platform"
    platform.fixed = True
    platform.scale = (3.0, 1.0)
    game.objects.append(platform)

def test_platformer():
    global player
    player = GameObject(images["stick_figure"])
    player.scale = (1.5, 1.5)
    player.name = "player"
    game.objects.append(player)
    game.camera_center_object = player
    
    floor = GameObject(images["pink_rect"])
    floor.fixed = True
    floor.location = (0, GAME_SIZE[1])
    floor.scale = (GAME_SIZE[0] / 100, 0.25)
    floor.anchor = (0, 1)
    #game.objects.append(floor)
    
    platform = GameObject(images["pink_rect"])
    platform.fixed = True
    platform.location = (200, 850)
    platform.scale = (4, 0.25)
    platform.anchor = (0, 1)
    #game.objects.append(platform)

def test_map():
    tile_map = TileMap(ASSETS + "tilemaps/csv/test.csv")
    tile_map.textures = [images["dirt"], images["grass"], images["stone"]]
    game.load_map(tile_map)
    
test_platformer()
test_map()

frame.start()
