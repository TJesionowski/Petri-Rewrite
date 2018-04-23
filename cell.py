import math
import random

FIELD_SIZE = 1200

class Cell:
    global FIELD_SIZE

    def __init__(self, index, position, mass, cell_type="plant", splitMass=200):
        self.attrib = {"species": cell_type, "split_mass" : splitMass, "metabolism": 50 / splitMass, "vision_multiplier": 1}
        self.index = index
        self.position = position # X and Y coordinates of cell as list of [x, y]
        self.mass = mass
        self.radius = math.sqrt(self.mass/math.pi) * 5 # Set radius for use in rendering and interacting with other cells and world
        self.living = True
        self.id = random.randint(0, 99999999)
        self.target_cell = {"index": -1, "id": 0}

    def split(self, cell_list, angle):
        if self.attrib["species"] == "herbivore":
            new_position = [(self.position[0] + (math.cos(math.radians(angle)) * (self.radius * 2))), (self.position[1] + (math.sin(math.radians(angle)) * (self.radius * 2)))]
        else:
            new_position = [(self.position[0] + (math.cos(math.radians(angle)) * (self.radius * 4))), (self.position[1] + (math.sin(math.radians(angle)) * (self.radius * 4)))]
        cell_list.append(Cell(len(cell_list), new_position, self.mass / 3, self.attrib["species"], self.attrib["split_mass"]))
        self.mass /= 2

    def update(self, cell_list):

        self.mass -= self.mass * 0.001 * self.attrib["metabolism"]# Cells lose one thousandth of their mass per tick
        if self.attrib["species"] == "plant":
            self.mass += (self.calc_light() / 100) * self.mass # Plant cells gain a certain amount of mass per update cycle, depending on distance from the light source
            self.radius = math.sqrt(self.mass/math.pi) * 2 # Set radius for use in rendering and interacting with other cells and world
        else:
            self.radius = math.sqrt(self.mass/math.pi) * 3 # Non-plant cells have greater radii per mass
            self.move(self.target(cell_list))


        # Suffocation and consumption
        for other in cell_list: # loop through the list of other cells
            if self.dist(other.position) < (other.radius) and other.id != self.id and other.radius > self.radius: # if the cell is touching this cell and is not this cell, then this cell suffocates
                if other.attrib["species"] != "plant":
                    other.mass += self.mass
                self.living = False
                break

        if self.mass < self.attrib["split_mass"] / 5: # Check if cell should still be alive
            self.living = False
        elif self.mass > self.attrib["split_mass"]: # Check if cell should split
            if self.attrib["species"] == "herbivore":
                self.split(cell_list, self.target(cell_list))
            else:
                self.split(cell_list, random.randint(0, 360))

    def target(self, cell_list): # Chooses target based on species of cell, returns angle in radians pointing towards chosen target
        """ Movement, for cells which are capable of it, uses the following decision procedure:
                Cells check the general attractiveness of areas of the field, with a higher concentration of food making it appear better, and a higher concentration of predators making it appear worse
                Once it is within what appears to be a good area, it will "see" a target that it should move toward to consume, only ceasing its pursuit if the target is first reached by another cell or a predator nears it and makes it attempt to flee
        """
        direction = 0
        if self.target_cell["index"] >= 0 and self.target_cell["index"] < len(cell_list) and self.target_cell["id"] == cell_list[self.target_cell["index"]].id: # Make sure that the target from the previous cycle is still alive, and if not, find new target
            direction = math.atan2(
                (cell_list[self.target_cell["index"]].position[1] - self.position[1]), # Theta = atan2(y, x)
                (cell_list[self.target_cell["index"]].position[0] - self.position[0])) # Broken into multiplle lines for clarity
        else:
            distance = 9999
            for cell in cell_list: # Search for most desirable target, and save it's index and id
                if cell.mass < self.mass and (cell.attrib["species"] == "plant") and self.dist(cell.position) < distance and not cell.id == self.id:
                    self.target_cell = {"index": cell.index, "id": cell.id}
                    delta_x = cell_list[self.target_cell["index"]].position[1] - self.position[1]
                    delta_y = cell_list[self.target_cell["index"]].position[0] - self.position[0]
                    direction = math.atan2(delta_x, delta_y)
                    distance = self.dist(cell_list[self.target_cell["index"]].position)

        return direction

    def dist(self, other):
        """Calculate distance between two points"""
        return math.sqrt(math.pow(self.position[0] - other[0], 2) + math.pow(self.position[1] - other[1], 2))

    def move(self, angle=0, speed=(lambda x: (1 / (math.sqrt(x) / 20)))): # Moves the cell (Note: angle is in radians), speed is function for determining the rate at which movement slows to when mass increases
        """ If cell is herbivore, moves towards and consumes plantlike cell, if cell is omnivore, targets nearest and biggest consumable cell of any species
        """
        self.position = [(self.position[0] + (math.cos(angle) * speed(self.mass) * self.attrib["metabolism"])), (self.position[1] + (math.sin(angle) * speed(self.mass) * self.attrib["metabolism"]))] # Once direction of movement is decided, moves cell in that direction, with speed dependent on metabolic rate and mass

    def calc_light(self, dispersion_function=(lambda x: (1 /(1 + x / 200)))): # Calculate the amount of light reaching cell; by default the light loses 50% of its strength per 100 pixels
        """ Calculate amount of light reaching herbivorous cell"""
        distance = self.dist([FIELD_SIZE / 2, FIELD_SIZE / 2])
        light = dispersion_function(distance) # Light energy falls off with distance, rate depends on function

        return light