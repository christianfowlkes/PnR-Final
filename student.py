import pigo
import time  # import just in case students need
import random

# setup logs
import logging
LOG_LEVEL = logging.INFO
LOG_FILE = "/home/pi/PnR-Final/log_robot.log"  # don't forget to make this file!
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)


class Piggy(pigo.Pigo):
    """Student project, inherits teacher Pigo class which wraps all RPi specific functions"""

    def __init__(self):
        """The robot's constructor: sets variables and runs menu loop"""
        print("I have been instantiated!")
        # Our servo turns the sensor. What angle of the servo( ) method sets it straight?
        self.MIDPOINT = 100

        # YOU DECIDE: How close can an object get (cm) before we have to stop?
        self.SAFE_STOP_DIST = 35
        self.HARD_STOP_DIST = 25
        # YOU DECIDE: What left motor power helps straighten your fwd()?
        self.LEFT_SPEED = 140
        # YOU DECIDE: What left motor power helps straighten your fwd()?
        self.RIGHT_SPEED = 145
        # This one isn't capitalized because it changes during runtime, the others don't
        self.turn_track = 0
        # Our scan list! The index will be the degree and it will store distance
        self.scan = [None] * 180
        self.set_speed(self.LEFT_SPEED, self.RIGHT_SPEED)
        # let's use an event-driven model, make a handler of sorts to listen for "events"
        if __name__ == "__main__":
            while True:
                self.stop()
                self.menu()

    def menu(self):
        """Displays menu dictionary, takes key-input and calls method"""
        # This is a DICTIONARY, it's a list with custom index values
        # You may change the menu if you'd like to add an experimental method
        menu = {"n": ("Navigate forward", self.nav),
                "d": ("Dance", self.dance),
                "o": ("Obstacle count", self.obstacle_count),
                "c": ("Calibrate", self.calibrate),
                "t": ("Test", self.skill_test),
                "s": ("Check status", self.status),
                "h": ("Open House", self.open_house),
                "q": ("Quit", quit_now)}


        # loop and print the menu...
        for key in sorted(menu.keys()):
            print(key + ":" + menu[key][0])
        # store the user's answer
        ans = raw_input("Your selection: ")
        # activate the item selected
        menu.get(ans, [None, error])[1]()

    def skill_test(self):
        """demonstrates two nav skills"""
        choice = raw_input("Left/Right or Turn Until Clear?")

        if "l" in choice:
            self.wide_scan(count=3)  # scan the area
            # picks left or right

            # create two variables, left_total and right_total
            left_total = 0
            right_total = 0
            # loop from self.MIDPOINT - 60 to self.MIDPOINT
            for angle in range((self.MIDPOINT - 60), self.MIDPOINT):
                if self.scan[angle]:
                    #  add up the numbers to right_total
                    right_total += self.scan[angle]
            # loop from self.MIDPOINT to self.MIDPOINT + 60
            for angle in range(self.MIDPOINT, (self.MIDPOINT + 60)):
                if self.scan[angle]:
                    # add up the numbers to left_total
                    left_total += self.scan[angle]
            # if right is bigger:
                # turn right
            if right_total > left_total:
                self.encR(6)
                self.encF(6)
            # if left is bigger:
                # turn left
            if left_total > right_total:
                self.encL(6)
                self.encF(6)

        else:
            # turn until its clear
            while not self.is_clear():
                self.encR(5)


    def open_house(self):

        """reacts to dist measurement in a cute way"""
        while True:
            if self.dist() < 20:
                self.set_speed(200, 200)
                self.encB(5)
                self.encF(10)
                for x in range(3):
                    self.servo(self.MIDPOINT + 40)
                    self.servo(self.MIDPOINT - 40)
                self.stop()
            time.sleep(.1)

    # YOU DECIDE: How does your GoPiggy dance?
    def dance(self):
        """executes a series of methods that add up to a compound dance"""
        if not self.safe_to_dance():
            print("\n----NOT SAFE TO DANCE----\n")
            return False
        if self.safe_to_dance():
            print("\n---- LET'S DANCE ----\n")
        ##### WRITE YOUR FIRST PROJECT HERE
        for x in range(2):
            self.shuffle_forward()
            self.swang()
            self.nae_nae()
            self.boo()
            self.x_up()


    def safe_to_dance(self):
        """circles around and check for any obstacle"""
        # check for problems
        for x in range(4):
            if not self.is_clear():  # this makes the robot move backward and shake its head in a no motion
                self.servo(75)
                self.servo(125)
                self.encB(15)
                return False
            self.encR(10)   # this should make the robot turn bigger turns
        # if we find no problems:
        return True


    def shuffle_forward(self):
        """This command makes the robot do a shuffle forward"""
        for x in range(2):
            self.encR(3)
            self.encF(3)
            self.encL(3)
            self.encF(3)


    def swang(self):
        """This command makes the robot swing in a backward motion, making a swanging motion"""
        for x in range(3):
            self.encB(4)
            self.encR(2)
            self.encB(4)
            self.encL(2)


    def nae_nae(self):
        """This command makes the robot do the nae nae """
        for x in range(3):
            self.encR(5)
            self.encB(5)
            self.encL(5)


    def boo(self):
        """This command makes the robot back up and then do a surprise spring forward BOO! """
        self.set_speed(200,200)
        self.encB(5)
        self.encF(30)
        for x in range(3):
            self.servo(80)
            self.servo(140)
            self.servo(80)

    # This dance is from Ricky
    def x_up(self):
        """supposed to make an X formation"""
        for x in range(4):
            self.encB(9)
            self.encR(2)
            self.encF(9)
            self.encL(2)
            self.encB(9)
            self.encL(2)
            self.encF(9)
            self.encR(2)
            self.x_up()


    def obstacle_count(self):
        """scans and estimates the number of obstacles within sight"""
        self.wide_scan()
        found_something = False
        counter = 0
        for ang, distance in enumerate(self.scan):
            if distance and distance < 100 and not found_something:
                found_something = True
                counter += 1
                print("Object # %d found, chief" % counter)
            if distance and distance > 100 and found_something:
                found_something = False
        print("\n----I SEE %d OBJECTS----\n" % counter)

    def safety_check(self):
        """subroutine of the dance method"""
        self.servo(self.MIDPOINT)  # look straight ahead
        for loop in range(4):
            if not self.is_clear():
                print("NOT GOING TO DANCE")
                return False
            print("Check #%d" % (loop + 1))
            self.encR(12)  # figure out 90 deg
        print("Safe to dance!")
        return True

    def nav(self):
        """auto pilots and attempts to maintain original heading"""
        logging.debug("Starting the nav method")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        print("-------- [ Press CTRL + C to stop me ] --------\n")
        print("-----------! NAVIGATION ACTIVATED !------------\n")

        error_count = 0
        # this stops the robot if he gets caught in a loop ten times in a row
        while True:
            if self.is_clear():
                self.cruise()
                error_count = 0
            else:
                error_count += 1
                if error_count == 10:
                    raw_input("Ay Miley, what's good")
                self.choose_path()

    def cruise(self):
        """ drive straight while path is clear """
        # make sure I'm looking forward

        angle = self.MIDPOINT

        self.servo(angle)

        self.fwd()
        # this loop checks the robots surroundings while cruising
        while self.dist() > self.SAFE_STOP_DIST:
            if angle == self.MIDPOINT:
                angle = self.MIDPOINT - 29
            elif angle == self.MIDPOINT - 29:
                angle = self.MIDPOINT + 29
            elif angle == self.MIDPOINT + 29:
                angle = self.MIDPOINT
            self.servo(angle)
            time.sleep(.01)

        self.stop()

    # the robot should chose the path with the greatest distance
    def choose_path(self):
        """averages distance on either side of midpoint and turns"""
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        self.encB(3)
        self.wide_scan(count=5)
        maxLeft = 0
        maxRight = 0
        avgRight = 0
        avgLeft = 0

        for x in range(self.MIDPOINT-60, self.MIDPOINT):
            if self.scan[x]:
                avgRight += self.scan[x]
                if self.scan[x] > maxRight:
                    maxRight = self.scan[x]
        avgRight /= 60
        print('The average dist on the right is '+str(avgRight)+'cm')  # tells how far object is on the right
        logging.info('The average dist on the right is ' + str(avgRight) + 'cm')

        for x in range(self.MIDPOINT, self.MIDPOINT+60):
            if self.scan[x]:
                avgLeft += self.scan[x]
                if self.scan[x] > maxLeft:
                    maxLeft = self.scan[x]
        avgLeft /= 60
        print('The average dist on the left is ' + str(avgLeft) + 'cm')  # tells how far object is on the left
        logging.info('The average dist on the left is ' + str(avgLeft) + 'cm')

        if self.is_clear_in_front():
            print(" THIS WAS A WASTE. IT WAS CLEAR IN FRONT THIS WHOLE TIME \n")
            self.cruise()
        elif maxRight > maxLeft:
            self.encR(4)
        elif maxLeft > maxRight:
            self.encL(4)
        # if right is bigger turn to the right
        elif avgRight > avgLeft:
            self.encR(4)
        else:  # if left is bigger turn to the left
            self.encL(4)

    def is_clear_in_front(self):
        """ This checks to see if the front way is clear """
        for ang in range(self.MIDPOINT - 30, self.MIDPOINT + 30):
            if self.scan[ang] and self.scan[ang] < self.SAFE_STOP_DIST:
                return False
        return True

# detects an error
def error():
    """records general, less specific error"""
    logging.error("ERROR-404 not found")
    print('ERROR')

# shuts down the app
def quit_now():
    """shuts down app"""
    raise SystemExit

##################################################################
######## The app starts right here when we instantiate our GoPiggy


try:
    g = Piggy()
except (KeyboardInterrupt, SystemExit):
    pigo.stop_now()
except Exception as ee:
    logging.error(ee.__str__())
