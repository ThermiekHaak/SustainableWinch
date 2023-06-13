"""This parameter file holds operation constants"""


# Winch operation ground handeling
coupling = 30  # [s] average_time of coupling a plane
tightening = 10 # [s] time to tighten the rope
launchtime = 30 # [s] average_time from ground to decoupling of the plane
spoolingin  = 20 # [s] time from decoupling to cable at rest on ground
spoolingout_speed = 30 / 3.6 # [m/s] average speed of car pulling the cables to the planes


# Airstrip Constants
winchfieldlenght = 1000 # [m]


# Safety parameters
max_requiredforce = 20 * 10**3 * 0.9  # Max force [N] aplied to the cable set to 90% strongest weaklink (most two-seaters)


