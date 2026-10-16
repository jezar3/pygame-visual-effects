import pygame
import dash_vfx
import hurt_vfx
import splash_vfx
import ko_beam

pos and hit_pos as pygame.Vector2 positions in world coordinates.
facing as pygame.Vector2(1, 0) for right or pygame.Vector2(-1, 0) for left.
call only the effect where you want the action happens

---------------- call on dash, walk, or jump actions ----------------
dash_vfx.air_dash_red(pos, facing)
dash_vfx.air_dash_blue(pos, facing)
dash_vfx.air_dash_green(pos, facing)
-------------------------------------------------------------
dash_vfx.ground_dash_cement(pos, facing)
dash_vfx.ground_dash_grass(pos, facing)
dash_vfx.ground_dash_metal(pos, facing)

-------------------------------------------------------------

dash_vfx.walk_cement(pos, facing)
dash_vfx.walk_grass(pos, facing)
dash_vfx.walk_metal(pos, facing)

-------------------------------------------------------------
dash_vfx.single_jump(pos)
dash_vfx.double_jump(pos)
-------------------------------------------------------------
example:
dash_vfx.spawn_air(pos, facing, dash_vfx.AIR_RED) has dash_vfx.AIR_BLUE and dash_vfx.AIR_GREEN variants
dash_vfx.spawn_ground(pos, facing, dash_vfx.GROUND_GRASS) has dash_vfx.GROUND_CEMENT and dash_vfx.GROUND_metal variants

----------------  call when an attack hits ----------------
hurt_vfx.light_red(hit_pos, facing.x)
hurt_vfx.light_blue(hit_pos, facing.x)
hurt_vfx.light_green(hit_pos, facing.x)
-------------------------------------------------------------

angle = -22 if facing.x > 0 else 202

hurt_vfx.heavy_red(hit_pos, angle)
hurt_vfx.heavy_blue(hit_pos, angle)
hurt_vfx.heavy_green(hit_pos, angle)

-------------------------------------------------------------

Optional custom heavy-style burst. hue_shift is in degrees.

hurt_vfx.start(hit_pos, target_angle=angle, cone_width=90, hue_shift=20)

----------------  call on wall jump or water contact ----------------

splash_vfx.wall_jump(pos, side)
splash_vfx.water_splash(pos, strength=1)

side is 1 for right or -1 for left. strength scales the water splash.

---------------- call when the KO effect should start ----------------

ko_beam.start(center=pos,target_angle=-22 if facing.x > 0 else 202,cone_width=24,side=1 if facing.x > 0 else -1,hue_shift=0,)

Angles and hue_shift are in degrees

---------------- CALL ONCE PER FRAME, after gameplay updates ----------------

dash_vfx.update()
hurt_vfx.update()
splash_vfx.update()
ko_beam.update()

---------------- DRAW EVERY FRAME ----------------

Draw these onto world after drawing the scene and characters, but before copying
world to screen for the camera. SIZE is the character's world-pixel size like 16pixel

dash_vfx.draw_effects(world, SIZE)
hurt_vfx.draw(world)
splash_vfx.draw(world)
ko_beam.draw(world)
