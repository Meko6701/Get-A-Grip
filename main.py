ip_address = 'localhost'  # Enter your IP Address here
project_identifier = 'P2B'  # Enter the project identifier i.e. P2A or P2B
# --------------------------------------------------------------------------------
import sys

sys.path.append('../')
from Common.simulation_project_library import *

hardware = False
QLabs = configure_environment(project_identifier, ip_address, hardware).QLabs
arm = qarm(project_identifier, ip_address, QLabs, hardware)
potentiometer = potentiometer_interface()
# --------------------------------------------------------------------------------
# STUDENT CODE BEGINS
# ---------------------------------------------------------------------------------

import time, random  # imports necessary modules that are used in the code

'''Assigned: Malek'''


def clave_information(
        item_ID):  # This takes an item ID number and identifies the corresponding autoclave positions and colours for ease of use in other functions
    global clave_position
    global clave_colour
    if item_ID <= 3:
        clave_position = 1  # Defines small objects based on the defining factor of their autocave position number
    else:
        clave_position = 2  # Defines large objects based on the defining factor of their autoclave position number
    if item_ID == 1 or item_ID == 4:
        clave_colour = "red"
    elif item_ID == 2 or item_ID == 5:
        clave_colour = "green"
    else:
        clave_colour = "blue"
    # The above if statements set the global variable to a colour based on the ID


'''Assigned: Malek'''


# Pick-up function written below, which takes the item ID and grabs the object and brings it to the home position, gripping according to its size:
def pick_up(clave_num):
    arm.move_arm(0.575, 0.05, 0.034)
    time.sleep(2)
    if clave_num == 1:  # Accounts gripping amount for the smaller objects
        arm.control_gripper(40)
    else:  # Accounts gripping amount for the larger objects size
        arm.control_gripper(25)
    time.sleep(2)
    arm.move_arm(0.406, 0.0, 0.483)  # Goes to home position


'''Assigned: Alexander'''


# Rotate Arm function defined below, which allows for the movement of the arm via the right potentiometer given the colour of an autoclave (it stops when the correct autoclave is rotated to)
def rotate_arm(colour):
    rot_values = []

    for i in range(101):
        rot_values.append(
            3.498 * i - 174.9)  # This assigns a relative degree value for every potentiometer value (0-100) which goes into the above list, based on the linear equation given by the linear relation y=3.498x-174.9, where y is the degrees and x is the potentiometer value

    while potentiometer.right() != 0.5:  # Since the Q-Labs tends to glitch with the potentiometer slider, this waits until the slider is set to 0 for all of the rotations to be correct in accordance with the equation/list
        time.sleep(1)

    initial_pos = potentiometer.right()

    while arm.check_autoclave(colour) == False:
        if potentiometer.right() != initial_pos:
            arm.rotate_base(rot_values[int(potentiometer.right() * 100)] - (rot_values[int(initial_pos * 100)]))
            initial_pos = potentiometer.right()
    # This loop runs until the correct autoclave is pointed to, and essentially rotates when there is a change in potentiometer value (as the slider moves)

    global pos_at_rot
    pos_at_rot = arm.effector_position()
    # This assigns that rotated position's coordinates to a global variable that will be used in other parts of the code


'''Assigned: Alexander'''


# Drop off function defined below, which drops off the object into the autoclave given the colour (clave_type) and position # (clave_size)
def drop_off(clave_type, clave_size):
    reset = 0  # Creates a reset variable that is to be used later to prevent unnecessary repetition; this is used after the verification of the correct position is false
    arm.activate_autoclaves()
    initial_pos = potentiometer.left()
    while potentiometer.left() == initial_pos or potentiometer.left() <= 0.5:  # While the threshold of the left potentiometer is invalid, the program waits. It also waits for the user to change the potentiometer value to prevent it moving somewhere unnecessarily since there would be no time between runs to change it.
        time.sleep(1)
    if potentiometer.left() > 0.5 and potentiometer.left() < 1:  # Accounts for position 1, moves to coordinates based on each colour
        if arm.check_autoclave("blue") == True:
            arm.move_arm(0.0, 0.617, 0.281)
        elif arm.check_autoclave("red") == True:
            arm.move_arm(-0.576, 0.221, 0.281)
        else:
            arm.move_arm(0.0, -0.617, 0.281)
        time.sleep(2)
        if clave_size == 2:  # If the slider is moved for position 1 but the object is large, it moves back and reruns the function, letting the user change the potentiometer to the correct value
            arm.move_arm(pos_at_rot[0], pos_at_rot[1], pos_at_rot[2])
            arm.deactivate_autoclaves()  # This is deactivated to avoid a repeat in activation when the function is run again
            drop_off(clave_type, clave_size)
            reset = 1  # Changes the reset variable, indicating that the arm had to rerun the function again
        if reset != 1:
            arm.control_gripper(
                -40)  # If the position is correct and no reset had to be performed, the object is dropped
    elif potentiometer.left() == 1:  # Accounts for position 2, opening the autoclave drawer for the given colour and moving the object to the correct coordinates
        arm.open_autoclave(clave_type, True)
        if clave_type == "blue":
            arm.move_arm(-0.0, 0.383, 0.15)
        elif clave_type == "red":
            arm.move_arm(-0.355, 0.144, 0.15)
        else:
            arm.move_arm(0.0, -0.383, 0.15)
        time.sleep(2)
        if clave_size == 1:  # If the slider is moved for position 2 but the object is small, this moves the arm back, closes the drawer, and reruns the function
            arm.move_arm(pos_at_rot[0], pos_at_rot[1], pos_at_rot[2])
            time.sleep(1)
            arm.open_autoclave(clave_type, False)
            arm.deactivate_autoclaves()
            drop_off(clave_type, clave_size)
            reset = 1  # Reset variable updated to indicate a reset was performed
        if reset != 1:  # If no reset was necessary, the object and position are correct, and so the arm releases the object
            arm.control_gripper(-25)
    time.sleep(2)


'''Assigned: Alexander'''


# Return home function defined below, which moves the arm back to its initial rotated position, closes the drawer if necessary, and goes back to the home position (given an autoclave colour; the pos_at_rot is the same for either size object)
def return_home(clave_type):
    arm.move_arm(pos_at_rot[0], pos_at_rot[1], pos_at_rot[
        2])  # This is used instead of arm.home() immediately as it prevents the arm from knocking into anything as it gradually moves back in multiple directions
    time.sleep(0.5)  # Gives some time for the drawer to close to avoid collisions with the arm
    if potentiometer.left() == 1:
        arm.open_autoclave(clave_type, False)  # Closes the autoclave drawer if the object is large
    arm.deactivate_autoclaves()
    arm.home()


'''Assigned: Malek'''


# Continue or terminate function defined below, given a list of objects
def continue_or_terminate(inventory):
    if len(inventory) == 0:  # If there are no items left in the inventory (0 items in list), this returns False (terminate)
        return False
    else:  # If not (there are still items in the list), it returns True (continue)
        return True


'''Assigned: Both'''
# Global variables defined below, which are set as empty here but are accessed elsewhere and used in other parts of code
pos_at_rot = 0, 0, 0  # Defines position of arm at a given rotation
clave_colour = ""  # Defines the colour of the object/autoclave as a string
clave_position = 0  # Defines the position of the autoclave/size of object (1 or 2, small or large) as an integer


# Main function defined below
def main():
    global clave_colour
    global clave_position
    cage = [1, 2, 3, 4, 5, 6]  # List of objects created

    while continue_or_terminate(
            cage) == True:  # This runs while the continue_or_terminate function says it should continue
        cage_num = random.choice(cage)  # Sets a variable to a random item from the cage list
        cage.remove(cage_num)  # After picking the object, it removes it from the list
        arm.spawn_cage(cage_num)  # This spawns the chosen cage
        clave_information(
            cage_num)  # This updates the global variables with the correct information for the given object

        pick_up(clave_position)
        rotate_arm(clave_colour)
        drop_off(clave_colour, clave_position)
        return_home(clave_colour)
        # All functions that are run above are used for the entire procedure given the autoclave colours and positions. The continue_or_terminate function is run within the while loop, which by order of code technically happens after all of these are run through.

# ---------------------------------------------------------------------------------
# STUDENT CODE ENDS
# ---------------------------------------------------------------------------------




