"""
Kayden Zhao, June 13th, 2024, Mario But Worse.
"""

# Import Libraries
import arcade
import random
import time

# Global variables
PLAYER_SCALING = 0.1
FLOOR_SCALING = 1.115
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
GRAVITY = 1.5
PLAYER_JUMP_SPEED = 15
MOVEMENT_SPEED = 0.5
MOB_MOVESPEED = 1.5
LEFT_VIEWPOINT_MARGIN = 500
RIGHT_VIEWPOINT_MARGIN = 900
BOTTOM_VIEWPOINT_MARGIN = 100
TOP_VIEWPOINT_MARGIN = 100
POWER_BOX_SCALING = 0.125
MAX_SPEED = 8.0
ACCELERATION = 0.75
RIGHT_FACING = 0
LEFT_FACING = 1
DEAD_ZONE = 0.1
FORCE_ON_GROUND = 7500
FORCE_IN_AIR = 900
FRICTION = 10.0
PLAYER_MAX_HORIZONTAL_SPEED = 450
PLAYER_MAX_VERTICAL_SPEED = 1600


class InstructionView(arcade.View):
    """ View to show instructions """

    def __init__(self):

        super().__init__()
        self.texture = arcade.load_texture("mario_title-screen.png")

    def on_show_view(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

        # Reset the viewport, necessary if we have a scrolling game, and we need
        # to reset the viewport back to the start, so we can see what we draw.
        arcade.set_viewport(0, self.window.width, 0, self.window.height)

    def on_draw(self):
        """ Draw this view """
        self.clear()
        self.texture.draw_sized(SCREEN_WIDTH/2,  SCREEN_HEIGHT/2, SCREEN_WIDTH, SCREEN_HEIGHT)
        arcade.draw_text("(Press Enter)", 1150, 325, font_size=25, font_name="Super Mario Bros. NES")

    def on_key_press(self, key, modifiers):
        """ If the user presses the enter button, start the game. """
        if key == arcade.key.ENTER:
            game_view = MyGame()
            game_view.setup()
            self.window.show_view(game_view)


class GameOverView(arcade.View):
    """ View to show when game is over """

    def __init__(self):
        """ This is run once when we switch to this view """
        super().__init__()

        # Reset the viewport, necessary if we have a scrolling game, and we need
        # to reset the viewport back to the start, so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """ Draw this view """
        self.clear()
        arcade.draw_text("Game Over", 850, SCREEN_HEIGHT//2, arcade.color.WHITE, 25,
                         font_name="Super Mario Bros. NES")
        arcade.draw_text("Click Enter to restart", 1200, 100, arcade.color.WHITE, 25,
                         font_name="Super Mario Bros. NES")

    def on_key_press(self, key, modifiers):
        """ If the user presses the enter button, start the game. """
        if key == arcade.key.ENTER:
            game_view = MyGame()
            game_view.setup()
            self.window.show_view(game_view)


class MyGame(arcade.View):

    def __init__(self):
        # Call the parent class initializer
        super().__init__()

        # Holds moving sprites
        self.goomba_list = arcade.SpriteList()
        self.goomba_lists = arcade.SpriteList()
        self.chain_list = arcade.SpriteList()
        self.koopa_list = arcade.SpriteList()
        self.cloud_list = arcade.SpriteList()

        # Holds environment
        self.hill_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()

        # Set up the player info and physics engine
        self.player_sprite = None
        self.physics_engine = None

        # Variables for environment
        self.power_box = None
        self.coin = None
        self.stair_brick_sprite = None
        self.stair = None
        self.pipe_sprite = None
        self.hidden_block = None
        self.cloud_sprite = None
        self.castle_sprite = None
        self.flag_sprite = None
        self.castle_wall = None
        self.border_start = None
        self.border_end = None

        # Mobs Variables, Time, Shell, Confetti and Peach
        self.goomba_sprite = None
        self.koopa_sprite = None
        self.chain_chomper = None
        self.chain_chomper2 = None
        self.time = 400
        self.total_time = 400
        self.score = 0
        self.lives = 3
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.shell = None
        self.confetti = False
        self.princess_peach = None
        self.sink_peach = None

        # Set camera sliding variables
        self.view_bottom = 0
        self.view_left = 0

        # Set the background color
        arcade.set_background_color((105, 136, 256, 255))

    def setup(self):

        # Sets the PymunkPhysicsEngine
        self.physics_engine = arcade.PymunkPhysicsEngine(gravity=(0, -1800), damping=0.25)
        """
        This physics engine is mainly used for importing sprites. Normally you would create a space with pymunk.Space(),
        and there would be bodies and shapes. Though that is not applicable for sprites and only bodies/shapes as pymunk 
        has built in functions to draw bodies.
        """

        # Creates border so player doesn't go off the map (start)
        self.border_start = arcade.Sprite("sprites/87ceeb.png", 5)
        self.border_start.center_x = -400
        self.border_start.center_y = 100
        self.border_start.height = 100000
        self.border_start.visible = False
        self.wall_list.append(self.border_start)

        # Border at end
        self.border_end = arcade.Sprite("sprites/87ceeb.png", 5)
        self.border_end.position = 8350, 100
        self.border_end.height = 100000
        self.border_end.visible = False
        self.wall_list.append(self.border_end)

        # Makes Flag
        self.flag_sprite = arcade.Sprite("sprites/flag.png", 0.25)
        self.flag_sprite.center_x = 7300
        self.flag_sprite.center_y = 470
        self.flag_sprite.height = 350

        # Creates Castle at the end
        self.castle_sprite = arcade.Sprite("sprites/castle.png", 0.8)
        self.castle_sprite.center_x = 7700
        self.castle_sprite.center_y = 396

        # Makes Player go inside in the castle
        self.castle_wall = arcade.Sprite("sprites/castle_wall.png", 0.8)
        self.castle_wall.center_x = 7762
        self.castle_wall.center_y = 327

        # Creates two rotating chompers that instant kill you.
        self.chain_chomper = arcade.Sprite("sprites/Chain_Chomp_SMB3.png", 0.1)
        self.chain_chomper.center_x = 1490
        self.chain_chomper.center_y = 295
        self.chain_chomper2 = arcade.Sprite("sprites/Chain_Chomp_SMB3.png", 0.1)
        self.chain_chomper2.center_x = 1260
        self.chain_chomper2.center_y = 295
        self.chain_list.append(self.chain_chomper2)
        self.chain_list.append(self.chain_chomper)

        # Confetti
        self.confetti = arcade.Sprite("sprites/confetti.png", 1)
        self.confetti.position = 7300, 800
        self.confetti.visible = False
        self.cloud_list.append(self.confetti)

        # Creates Peach
        self.princess_peach = arcade.Sprite("sprites/peach.png", 0.1)
        self.princess_peach.position = 7200, 1500

        # Creates Clouds
        for i in range(25):
            cloud = arcade.Sprite("sprites/cloud.png", 0.15)
            cloud_placed_successfully = False
            while not cloud_placed_successfully:
                cloud.center_x = random.randrange(8000)
                cloud.center_y = random.randint(750, 1000)
                cloud.width = 140

                wall_hit_list = arcade.check_for_collision_with_list(cloud, self.wall_list)

                # See if the cloud is hitting another cloud
                cloud_hit_list = arcade.check_for_collision_with_list(cloud, self.cloud_list)

                if len(wall_hit_list) == 0 and len(cloud_hit_list) == 0:
                    cloud_placed_successfully = True
                # Add the cloud to the lists
            self.cloud_list.append(cloud)

        # Creates Player Sprite
        self.player_sprite = arcade.Sprite("player/mario.png", PLAYER_SCALING, hit_box_algorithm='Detailed')
        self.player_sprite.center_x = 7000
        self.player_sprite.center_y = 300
        self.player_list.append(self.player_sprite)
        # Adds player to physics engine with parameters such as
        self.physics_engine.add_sprite(self.player_sprite, moment_of_inertia=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED, elasticity=0,
                                       mass=2, collision_type="player", max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED
                                       )

        # Creates Green Pipes
        coordinate_pipe = [[1900, 295], [2800, 295], [5700, 295], [6500, 295]]
        for coordinate in coordinate_pipe:
            wall = arcade.Sprite("sprites/pipe.png", 0.5)
            wall.position = coordinate

            self.wall_list.append(wall)

        # Creates Bricks + Lists
        coordinate_brick = [[600, 400], [656, 400], [712, 400], [1360, 500], [1385, 500], [1410, 500], [2336, 380],
                            [2352, 380], [2368, 380], [2384, 380], [2410, 380], [3500, 400], [3556, 400], [3650, 550],
                            [3678, 550], [3706, 550], [3724, 550], [3742, 550], [3762, 550], [3790, 550], [3818, 550],
                            [2320, 380], [2304, 380], [3950, 550], [3978, 550], [4006, 550], [4022, 400], [6000, 400],
                            [6056, 400], [6084, 400], [2288, 380]]
        # Loops through list of coordinates and creates a brick on the specific coordinates.
        for coordinate in coordinate_brick:
            wall = arcade.Sprite("sprites/brick.png", 0.035)
            wall.position = coordinate
            self.wall_list.append(wall)

        # Creates a hidden block which is invisible at first
        self.hidden_block = arcade.Sprite("sprites/Hidden_Block.png", 0.1)
        self.hidden_block.center_y = 565
        self.hidden_block.center_x = 2425
        self.hidden_block.visible = False

        # Makes a shell for Koopa
        self.shell = arcade.Sprite("sprites/shell.png", 0.095)
        self.shell.center_x = 7000
        self.shell.center_y = 290
        self.wall_list.append(self.shell)
        # Adds shell to physics engine
        self.physics_engine.add_sprite(self.shell)

        goomba_list = [[4300, 293], [4350, 293], [3100, 293], [3400, 293], [1800, 293], [2100, 293], [300, 293],
                       [1250, 450]]

        # Create Goomba
        for cords in goomba_list:
            self.goomba_sprite = arcade.Sprite("sprites/download.png", 0.08)
            self.goomba_sprite.position = cords
            self.goomba_sprite.change_x = -1
            self.goomba_lists.append(self.goomba_sprite)
        # Add all goombas to physics engine
        self.physics_engine.add_sprite_list(self.goomba_lists, collision_type="goomba")

        # Creates Koopa Troopa
        self.koopa_sprite = arcade.Sprite("sprites/turtle_koopa_super_mario_bros_icon_232948.png", 0.15)
        self.koopa_sprite.center_x = 6000
        self.koopa_sprite.center_y = 300
        self.koopa_list.append(self.koopa_sprite)
        # Add Koopa to physics engine
        self.physics_engine.add_sprite_list(self.koopa_list, collision_type="koopa")

        coordinate_box = [[628, 400], [684, 400], [656, 550], [400, 400], [3528, 400], [4022, 550], [6028, 400]]
        # Loops through lists of cords and creates a power box on each coordinate.
        for coordinate in coordinate_box:
            wall = arcade.Sprite('sprites/images (1).png', POWER_BOX_SCALING)
            wall.position = coordinate
            self.wall_list.append(wall)

        coordinate_stair = ([[1140, 285], [1165, 285], [1190, 285], [1215, 285], [1240, 285], [1165, 310], [1190, 310],
                             [1215, 310], [1240, 310], [1190, 335], [1215, 335], [1240, 335], [1215, 360], [1240, 360],
                             [1240, 385], [1525, 285], [1525, 310], [1525, 335], [1525, 360], [1525, 385], [1550, 285],
                             [1550, 310], [1550, 335], [1550, 360], [1575, 285], [1575, 310], [1575, 335], [1600, 285],
                             [1600, 310], [1625, 285], [1600, 310], [5100, 285], [5125, 285], [5150, 285], [5175, 285],
                             [5200, 285], [5125, 310], [5150, 310], [5175, 310], [5200, 310], [5150, 335], [5175, 335],
                             [5200, 335], [5175, 360], [5200, 360], [5345, 285], [5370, 285], [5395, 285], [5420, 285],
                             [5345, 310], [5345, 335], [5345, 360], [5370, 310], [5370, 335], [5395, 310], [6650, 285],
                             [6675, 285], [6700, 285], [6725, 285], [6750, 285], [6775, 285], [6700, 335], [6675, 310],
                             [6800, 285], [6825, 285], [6825, 310], [6825, 335], [6825, 360], [6825, 385], [6825, 410],
                             [6825, 435], [6825, 460], [6800, 310], [6800, 335], [6800, 360], [6800, 385], [6800, 410],
                             [6800, 435], [6775, 310], [6775, 335], [6775, 360], [6775, 385], [6775, 410], [6750, 310],
                             [6750, 335], [6750, 360], [6750, 385], [6725, 310], [6725, 335], [6725, 360], [6700, 310],
                             [6850, 285], [6850, 310], [6850, 335], [6850, 360], [6850, 385], [6850, 410], [6850, 435],
                             [6850, 460], [7300, 285]])
        # Loops through list and creates each part of the stair.
        for coordinate in coordinate_stair:
            wall = arcade.Sprite("sprites/stair.png", 0.20)
            wall.position = coordinate
            self.wall_list.append(wall)

        # Sets cords for floor
        coordinate_list = [[-852, 130], [-371, 130], [110, 130], [250, 130], [780, 130], [1310, 130], [1840, 130],
                           [3430, 130], [4110, 130], [4470, 130], [5600, 130], [6050, 130], [5750, 130], [6250, 130],
                           [6750, 130], [7250, 130], [7750, 130], [2900, 130], [2800, 130], [4945, 130],]

        for coordinate in coordinate_list:
            # Creates Floor
            wall = arcade.Sprite(
                "sprites/floor.png", FLOOR_SCALING
            )
            wall.position = coordinate
            self.wall_list.append(wall)
        # Adds all walls to Physics Engine
        self.physics_engine.add_sprite_list(self.wall_list, body_type=arcade.PymunkPhysicsEngine.STATIC,
                                            collision_type="wall", elasticity=0)

        hill_list = [[100, 335], [5550, 335], [4500, 335], [800, 335], [3000, 335]]
        # Creates hills in the background
        for coord in hill_list:
            wall = arcade.Sprite("sprites/hill.png", 0.25)
            wall.position = coord
            wall.height = 120
            self.hill_list.append(wall)

        # Function for collision
        def collide(player_sprite, _other_sprite, _arbiter, _space, _data):
            """
            :param player_sprite: Player
            :param _other_sprite: Mob/Sprite
            :param _arbiter: Summarizes the colliding sprites and stores all their data.
            :param _space: Basic Unit of Simulation. Allows rigid bodies to be added and move forward in space.
            :param _data: Data for both shapes
            :return: True -> Engine allows collisions. False -> Engine ignores collisions.
            """

            # Checks if Player is in the air.
            if player_sprite.center_y > 296:
                # Removes the sprite from all lists
                self.score += 100
                self.physics_engine.apply_impulse(player_sprite, (0, 5000))
                _other_sprite.remove_from_sprite_lists()
            else:
                view = GameOverView()
                self.window.show_view(view)

            # Tells function to stop.
            return True

        # Handles collision between two given sprites and assigns one of the four callback functions to collide func.
        self.physics_engine.add_collision_handler("player", "goomba", begin_handler=collide)
        self.physics_engine.add_collision_handler("player", "koopa", begin_handler=collide)

    def on_key_press(self, key, modifiers):
        """
        :param key: Holds input key from keyboard
        :param modifiers: Keys that modifies behavior of keyboard
        """
        # Makes the player jump if up arrow is pressed
        if key == arcade.key.UP:
            if self.physics_engine.is_on_ground(self.player_sprite):
                impulse = (0, 1000)
                self.physics_engine.apply_impulse(self.player_sprite, impulse)
        # Moves player left if left key is pressed
        if key == arcade.key.LEFT:
            self.left_pressed = True
        # Moves player right if right key is pressed
        if key == arcade.key.RIGHT:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        """
        :param key: Holds input key from keyboard
        :param modifiers: Keys that modifies behavior of keyboard
        """
        # Stops player if right or left key is released
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0
            self.right_pressed = False
            self.left_pressed = False
        # Stops player if up key is released
        if key == arcade.key.UP:
            self.up_pressed = False

    def on_update(self, delta_time):
        # Checks if player is on ground.
        is_on_ground = self.physics_engine.is_on_ground(self.player_sprite)

        # Accelerates player is left or right key is pressed
        if self.left_pressed:
            if is_on_ground:
                # Moves character when on ground
                self.physics_engine.apply_force(self.player_sprite, (-FORCE_ON_GROUND, 0))
            else:
                # Moves character slower when in the air
                self.physics_engine.apply_force(self.player_sprite, (-FORCE_IN_AIR, 0))
            # Set friction to zero when moving
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.right_pressed:
            if is_on_ground:
                # Moves character when on ground
                self.physics_engine.apply_force(self.player_sprite, (FORCE_ON_GROUND, 0))
            else:
                # Moves character slower when in the air
                self.physics_engine.apply_force(self.player_sprite, (FORCE_IN_AIR, 0))

            # Set friction to zero when moving
            self.physics_engine.set_friction(self.player_sprite, 0)
        else:
            # Player's feet are not moving. Therefore, up the friction so we stop.
            self.physics_engine.set_friction(self.player_sprite, FRICTION)

        # Time
        self.total_time -= delta_time
        seconds = int(self.total_time) % 100000
        self.time = seconds

        # Moves chain chomper
        if self.chain_chomper.center_x == 1490:
            self.chain_chomper.change_x = -2.5
        if self.chain_chomper.center_x == 1260:
            self.chain_chomper.change_x = 2.5
        # Allows chain chompers to rotate
        self.chain_chomper.change_angle = 10
        self.chain_chomper.update()
        # Moves second chain chomper
        if self.chain_chomper2.center_x == 1260:
            self.chain_chomper2.change_x = 2.5
        if self.chain_chomper2.center_x == 1490:
            self.chain_chomper2.change_x = -2.5
        # Rotates other chain chomper
        self.chain_chomper2.change_angle = 10
        self.chain_chomper2.update()

        # If hits chain chomper, instant death.
        chompy = arcade.check_for_collision_with_list(self.player_sprite, self.chain_list)
        if chompy:
            view = GameOverView()
            self.window.show_view(view)

        # Makes confetti if player reaches end and adds Peach to the physics engine, so she falls down.
        flag = arcade.check_for_collision(self.player_sprite, self.flag_sprite)
        if flag:
            self.confetti.visible = True
            self.physics_engine.add_sprite(self.princess_peach, body_type=arcade.PymunkPhysicsEngine.DYNAMIC)
        # Checks for collision with hidden block
        self.hidden_block.update()
        collide = arcade.check_for_collision(self.player_sprite, self.hidden_block)
        # Reveals hidden block if hit
        if collide:
            self.player_sprite.change_y = 0
            self.hidden_block.visible = True

        # Camera
        changed = False
        # Moves camera right if not enough pixels are to the right of the player and border
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPOINT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True
        # Moves camera left if not enough pixels are to the left of the player and border
        left_boundary = self.view_left + LEFT_VIEWPOINT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True
        # Moves camera down if not enough pixels are to the down of the player and border
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPOINT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True
        # Actually moves the camera
        if changed:
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)

        # Updates Physics Engine
        self.physics_engine.step()

        # If time runs out or player falls off map, player loses
        if self.time == 0 or self.player_sprite.center_y < 150:
            time.sleep(0.5)
            view = GameOverView()
            self.window.show_view(view)

    def on_draw(self):
        # Draws everything needed
        self.clear()

        self.princess_peach.draw()
        self.castle_sprite.draw()
        self.hill_list.draw()
        # Moving mobs and player
        self.player_list.draw()
        self.koopa_list.draw()
        self.goomba_lists.draw()
        self.chain_list.draw()

        # Environment
        self.wall_list.draw(pixelated=True)
        self.hidden_block.draw()
        self.cloud_list.draw()
        self.castle_wall.draw()
        self.flag_sprite.draw()

        # Lives
        output = f"Lives: {self.lives}"
        output2 = self.score
        output3 = self.time
        # Draws text like score, time and lives and SHELL
        arcade.draw_text(output, self.view_left + 1300, 1000, arcade.color.WHITE, 15, font_name="Super Mario Bros. NES")
        arcade.draw_text("Mario", self.view_left + 200, 1000, arcade.color.WHITE, 15, font_name="Super Mario Bros. NES")
        arcade.draw_text(output2, self.view_left + 225, 970, arcade.color.WHITE, 15, font_name="Super Mario Bros. NES")
        arcade.draw_text(output3, self.view_left + 1680, 970, arcade.color.WHITE, 15, font_name="Super Mario Bros. NES")
        arcade.draw_text("Time", self.view_left + 1650, 1000, arcade.color.WHITE, 15, font_name="Super Mario Bros. NES")
        arcade.draw_text("Shell Playtime", 7000, 500, arcade.color.WHITE, 15, font_name="Super Mario Bros. NES")


def main():
    """ Main function """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, fullscreen=True)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
