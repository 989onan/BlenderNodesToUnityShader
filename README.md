# BlenderNodesToUnityShader

# I'm using this with the Cats plugin, will this work?/ Will this work for me?:
Most likely yes, because models made in blender or ported from other places made in blender will work 99% of the time. This is because the material setups they use are just a simple principled BDSF or some simple node settup where not much is happening. This addon will break when the node settup uses much more complicated nodes like snap, vector rotating on X axis, black bodies, wavelength to color, and other things that usually most blender models don't use. This will actually work for some vector math equations and even splitting vectors into multiple parts and inputting vectors into color and so forth. It can replicate crazy node settups where textures change and warp based on the camera angle or a color multiplied by some strange uv map plugged into a uv map or something crazy. The issue arrises when the node settup uses nodes that use complex math in a singular node, things that depend on complex concepts like color theory, or are very blender specific. Can't do node groups, please unpack them!

**TLDR**: 99% possibility of success on usual node settups. Breaks on edge cases 99% of the time where the nodes used are very blender specific. Can't do node groups, please unpack them!

# About:
This is a simple description for now, but this is a tool I made for Blender and Unity users alike. do you hate that there are blender materials
that blender artists made that are simple, cool looking, but not for unity? Not anymore! This will generate a shader that does a "#pragma 4.0" shader 
which will look very close to the version it looks like in blender. This is not magic! It's real. 

# Alpha!?!?:
Yes. This is alpha. I wrote this over the course of a week, and has many bugs that still need to be worked out. It has gone through about 30 minutes of training and not all nodes
have been tested, and not all configurations. I (@989onan) will be making commits and trying to patch as many bugs as possible! 

# This tool is crappy! You suck!:
Yes. I know. Now if you want to actually make it better, please ask your friends that know python to help me on the journey to make this code an amazing tool for all!
Also, point out ways I can write the code for different nodes, and how I can make code that replicates what blender does in the form of Unity3D shader language.
I am kinda dumb since i'm a junior programmer, so I will try my best to implement as many nodes as I can.

# Why is "X" node not supported!?!?:
well most likely it's because it's a blender only node. How would unity make a shader that has volumetric smoke or dust which isn't particles? It can't. Exactly. This and other
similar explinations are most likely the reason.

# How to install:
1. download a zip from the releases page, or download the folder in the root of this project as a zip. Then install from file and choose the zip like any other blender addon.

# Questions?
shoot me a message! My discord is "989onan#0794"!
