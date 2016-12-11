# CodeSkulptor runs Python programs in your browser.
# Click the upper left button to run this simple demo.

# CodeSkulptor runs in Chrome 18+, Firefox 11+, and Safari 6+.
# Some features may work in other browsers, but do not expect
# full functionality.  It does NOT run in Internet Explorer.

import simplegui

RENDER_DEBUG = False
COLLISION_DEBUG = True

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
        
        if COLLISION_DEBUG:
            print "Collision rect:"
            print "TOP_LEFT:\t" + str(obj1_bounds[0])
            print "TOP_RIGHT:\t" + str(obj1_bounds[1])
            print "BOTTOM_LEFT:\t" + str(obj1_bounds[2])
            print "BOTTOM_RIGHT:\t" + str(obj1_bounds[3])
            print
            
        obj1_loc = obj1_bounds[0]
        obj1_s = obj1.scaled_size()
        
        for obj2 in objects:
            if object is obj2:
                # We can't collide with ourself
                continue
            obj2_bounds = obj2.scaled_bounds()
            obj2_loc = obj2_bounds[0]
            obj2_s = obj2.scaled_size()
            
            # Check if colliding (boolean)
            if obj1_loc[0] < obj2_loc[0] + obj2_s[0] and obj1_loc[0] + obj1_s[0] > obj2_loc[0] and obj1_loc[1] < obj2_loc[1] + obj2_s[1] and obj1_loc[1] + obj1_s[1] > obj2_loc[1]:
                
                # Find translation vector 
                # Find distances between shape1's edge and shape2's opposite edge
                edge_differences = [
                    obj1_loc[0] - (obj2_loc[0] + obj2_s[0]), # Left
                    obj1_loc[0] + obj1_s[0] - obj2_loc[0], # Right
                    obj1_loc[1] - (obj2_loc[1] + obj2_s[1]), # Top
                    obj1_loc[1] + obj1_s[1] - obj2_loc[1], # Bottom
                ]
                edge_differences = sorted(edge_differences)
                mtv = edge_differences =[0]
                
                if COLLISION_DEBUG:
                    print "Collision!"
                    print "MTV:\t" + str(mtv)
                    print
                    
                # Return collision boolean and translation vector
                return True, mtv
        return False, (0, 0)

    def physics(self, object):
        # Apply gravity
        object.location = (object.location[0] + self.gravity[0],
                           object.location[1] + self.gravity[1])
        
        # Check collisions
        doesCollide, mtv = Game.checkCollisions(object, self.objects)
        if doesCollide:
            object.location = (object.location[0] + mtv[0], object.location[1] + mtv[1])
    
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
game.objects.append(test)

platform = GameObject(test_sprite)
platform.location = (100, 200)
platform.fixed = True
platform.scale = (4.0, 0.5)
game.objects.append(platform)

frame.start()
