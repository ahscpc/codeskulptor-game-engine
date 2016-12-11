# CodeSkulptor runs Python programs in your browser.
# Click the upper left button to run this simple demo.

# CodeSkulptor runs in Chrome 18+, Firefox 11+, and Safari 6+.
# Some features may work in other browsers, but do not expect
# full functionality.  It does NOT run in Internet Explorer.

import simplegui, math

RENDER_DEBUG = False
COLLISION_DEBUG = False

def pyth(sidea, sideb):
    return (sidea ** 2) + (sideb ** 2) ##no sqrt for efficiency
    
class GameObject:
    
    def __init__(self, sprite):
        self.location = (0, 0)
        self.velocity = (0, 0)
        self.scale = (1, 1)
        self.anchor = (0.5, 0.5)
        self.size = (sprite.get_width(), sprite.get_height())
        self.rotation = 0
        self.fixed = False
        self.sprite = sprite
        self.name = "name"
        return self
    
    def spriteCenter(self):
        return (self.size[0] / 2, self.size[1] / 2)
    
    def scaled_center(self):
        scaled_size = self.scaled_size()
        return (scaled_size[0] / 2, scaled_size[0] / 2)
    
    def scaled_location_center(self):
        scaled_center = self.scaled_center()
        
        centerX = self.location[0] + scaled_center[0]
        centerY = self.location[1] + scaled_center[1]
        return (centerX, centerY)
        
    def scaled_size(self):
        return (self.size[0] * self.scale[0], self.size[1] * self.scale[1])
    
    def anchoredLocation(self):
        scaled_size = self.scaled_size()
        scaled_center = self.scaled_center()
        centerX = self.location[0] + scaled_center[0] - (scaled_size[0] * self.anchor[0])
        centerY = self.location[1] + scaled_center[1] - (scaled_size[1] * self.anchor[1])
        return (centerX, centerY)
    
    def scaled_bounds(self):
        scaled_location_center = self.scaled_location_center()
        scaled_size = self.scaled_size()
        half = (scaled_size[0] / 2, scaled_size[1] / 2)
        
        top_left = (scaled_location_center[0] - half[0],
                    scaled_location_center[1] - half[1])
        
        top_right = (scaled_location_center[0] + half[0],
                    scaled_location_center[1] - half[1])
        
        bottom_left = (scaled_location_center[0] - half[0],
                    scaled_location_center[1] + half[1])
        
        bottom_right = (scaled_location_center[0] + half[0],
                    scaled_location_center[1] + half[1])
        
        return (top_left, top_right, bottom_left, bottom_right)

class Game:
    
    games = []
        
    def checkCollisions(obj1, objects):
        obj1_bounds = obj1.scaled_bounds()
        obj1_o = obj1_bounds[0]
        obj1_s = obj1.scaled_size()
        
        if COLLISION_DEBUG:
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
            
            if COLLISION_DEBUG:
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
                        print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
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
                        print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
                        print "Collision!"
                        print "Obj1:\t" + obj1.name + "\t" + "Obj2:\t" + obj2.name
                        print "Chosen Vector:\t" + str(mtv)
                        print

                    # Return collision boolean and translation vector
                        
                    return True, mtv or (0,0)
                
        return False, (0, 0)
    
    def physics(self, object):

        # Check collisions (DO THIS BEFORE APPLYING GRAVITY)
        doesCollide, mtv = Game.checkCollisions(object, self.objects)
        if doesCollide:
            object.location = (object.location[0] + mtv[0], object.location[1] + mtv[1])
            
        # Apply gravity
        object.location = (object.location[0] + self.gravity[0] + object.velocity[0],
                           object.location[1] + self.gravity[1] + object.velocity[1])
                        

    def draw(canvas):
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
            
            # Draw the sprite
            
            sprite = object.sprite
            source_center = object.spriteCenter()
            source_size = object.size
            center_dest = object.anchoredLocation()
            dest_size = object.scaled_size()
            rotation = object.rotation
            
            if RENDER_DEBUG:
                print "Drawing image:"
                print "Source center:\t\t" 		+ str(source_center)
                print "Anchor:\t\t\t"			+ str(object.anchor)
                print "Source size:\t\t" 		+ str(source_size)
                print "Center destination:\t" 	+ str(center_dest)
                print "Destination size:\t" 	+ str(dest_size)
                print "Rotation:\t\t" 			+ str(rotation)
                print
                
            canvas.draw_image(sprite,
                              source_center,
                              source_size,
                              center_dest,
                              dest_size,
                              rotation)
            
        self.customDraw(canvas)
        
    def __init__(self, frame, customDraw):
        self.objects = []
        self.customDraw = customDraw
        self.gravity = (0, 4)
        self.fixed = False
        
        Game.games.append((self, frame))
        frame.set_draw_handler(Game.draw)
        return self
    
# Handler to draw on canvas
def draw(canvas):
    pass

# Create a frame and assign callbacks to event handlers
frame = simplegui.create_frame("Home", 640, 480)
frame.set_canvas_background("White")

game = Game(frame, draw)

test_sprite = simplegui.load_image("https://i.sli.mg/ZCoVVl.png")
test = GameObject(test_sprite)
test.name = "test"
test.scale = (1.0, 1.0)
test.location = (50, 0)
test.velocity = (3, 0)
game.objects.append(test)

test2 = GameObject(test_sprite)
test2.name = "test2"
test2.scale = (1.0, 1.0)
test2.location = (350, 0)
game.objects.append(test2)


platform = GameObject(test_sprite)
platform.location = (300, 300)
platform.name = "platform"
platform.fixed = True
platform.scale = (1, 1)
game.objects.append(platform)

frame.start()
