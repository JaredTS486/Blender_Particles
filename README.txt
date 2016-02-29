This script calculates the force vectors acting on a "particle" (basically a sphere) due to the mass of objects adjacent to the particle relative to itself. The object is moved slightly due to this and then a keyframe is inserted into blender for that object. The script should have about 5000 keyframes, where each object in the scene is calculated and moved for each frame. Below are some instructions.

To use this script just copy it into the Blender scripting window / view and then click on RUN SCRIPT.

The script will load a user interface into the 3D View window area towards the bottom of the scroll area on the right.

The interface allows you to create a number of particles adjusting the visual look of each particle.

Velocity vectors are drawn out from the center of the particle and can be moved in the 3D view to change the main particles velocity. The velocity vector is also moved during the animation to show the relative acceleration change due to the mass of other objects in the scene.

You can select random boolean check boxes for each particles when creating them between the range set in the window relative to that particles random value (position, mass, velocity)

Each object also has a mass and certain variables that are used in the calculation most of which can be changed.

Make sure to OPEN THE BLENDER CONSOLE, a progress bar will appear there giving you a rough idea of how long the calculations will take. When ready to calculate just click on CALCULATE NOW towards the top of the object window.

** I ran a calculation of about 500 object which took about 2-3 hours on an i7 CPU, 5-10 object should take minutes**

You may also save and reset positions and velocity vectors of each object in case you mess up a particular set up.

** TO DO ** 
Runge Kutta 4th order is on its way as soon as i get more time to go over the math, the code is partially there now.

Set up a default solar system identical to our own centered around the sun -> need to get ratios of distance in blender to match to the real world distances.

Particles have no collision set up just yet, working on inelastic and elastic and good methods in blender to make those transitions as smooth as possible and still academically correct.

The mass of each object does have a limit at the moment. To high of a number goes over the limit and causes an error. Still looking for a good implementation of scientific notation for the masses of each object.

Let me know what you think.


