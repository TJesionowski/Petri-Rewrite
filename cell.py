import math
import random


class Cell:
    """General class for cells"""
    FIELD_SIZE = 1200

    def __init__(self, index, position, mass, cell_type, splitMass=200):
        self.attrib = {"species": cell_type, "split_mass" : splitMass, "metabolism": 50 / splitMass, "vision_multiplier": 1}
        self.index = index
        self.position = position  # X and Y coordinates of cell as list of [x, y]
        self.mass = mass
        self.radius = math.sqrt(self.mass / math.pi) * 5  # Set radius for use in rendering and interacting with other cells and world
        self.living = True
        self.identification_number = random.randint(0, 99999999)

    def split(self, cell_list, angle):
        """Creates a new cell of the same type with a portion of the parent cell's mass"""
        new_position = [(self.position[0] + (math.cos(math.radians(angle)) * (self.radius * 4))), (self.position[1] + (math.sin(math.radians(angle)) * (self.radius * 4)))]
        cell_list.append(Cell(len(cell_list), new_position, self.mass / 3, self.attrib["species"], self.attrib["split_mass"]))
        self.mass /= 2

    def update(self, cell_list):
        """Update the position, mass, and actions of the cell"""
        self.mass -= self.mass * 0.001 * self.attrib["metabolism"]  # Cells lose one thousandth of their mass per tick

        # Update radius

        # Check for suffocation or consumption

        # Split if able

        # Die if mass below threshold

    def dist(self, other):
        """Calculate distance between two points"""
        return math.sqrt(math.pow(self.position[0] - other[0], 2) + math.pow(self.position[1] - other[1], 2))


class Plant(Cell):
    """Plant cell sub-type:
        Capable of photosynthesizing light into energy, incapable of movement and consuming other cells.
        Suffocate out neighboring cells if it overlaps the other cell's center"""

    CELL_LIST = []  # List of cells of this type

    def __init__(self, index, position, mass, splitMass=200):
        super().__init__(index, position, mass, "plant")

    def update(self):
        """Update the position, mass, and actions of the cell"""

        # If the cell is currently dead, do not update
        if not self.living:
            return

        self.mass -= self.mass * 0.001 * self.attrib["metabolism"]  # Cells lose one thousandth of their mass per tick
        self.mass += (self.calc_light() / 100) * self.mass   # Plant cells gain a certain amount of mass per update cycle, depending on distance from the light source
        self.radius = math.sqrt(self.mass / math.pi) * 2   # Set radius for use in rendering and interacting with other cells and world

        for other in Plant.CELL_LIST:
            # loop through the list of other cells to check which will suffocate
            if (self.dist(other.position) - (self.radius)) < other.radius / -10  \
               and other.radius > self.radius:
                # if this cell overlaps another cell of the same type significantly, that cell dies, as if by "suffocation"
                self.living = False

        if self.mass < self.attrib["split_mass"] / 5:  # Check if cell should still be alive
            self.living = False
        elif self.mass > self.attrib["split_mass"]:  # Check if cell should split
                self.split(random.randint(0, 360))

    def split(self, angle):
        """Creates a new cell of the same type with a portion of the parent cell's mass"""
        new_position = [(self.position[0] + (math.cos(math.radians(angle)) * (self.radius * 4))),
                        (self.position[1] + (math.sin(math.radians(angle)) * (self.radius * 4)))]
        if random.randint(1, 10) != 1:
            Plant.CELL_LIST.append(Plant(len(Plant.CELL_LIST),
                                         new_position,
                                         self.mass / 3,
                                         self.attrib["split_mass"]))
        else:
            Spore(new_position,
                  self.mass / 3,
                  "Plant",
                  self.attrib["split_mass"])
        self.mass /= 2

    def calc_light(self, dispersion_function=(lambda x: (1 / (1 + x / 200)))):
        # Calculate the amount of light reaching cell; by default the light loses 50% of its strength per 100 pixels
        """ Calculate amount of light reaching herbivorous cell"""
        distance = self.dist([Cell.FIELD_SIZE / 2,
                              Cell.FIELD_SIZE / 2])
        # Light energy falls off with distance, rate depends on function
        return dispersion_function(distance)  


class Consumer(Cell):
    """Consumer cell subclass:
        Capable of consuming other cells; moves to nearest desirable target
        Other cell is consumed if its central point is overlapped"""

    CELL_LIST = []  # List of cells of this type
    TARGET_LIST = []  # List of cells available to consume

    def __init__(self, index, position, mass, splitMass=200):
        super().__init__(index, position, mass, "herbivore")
        self.target_cell = {"index": -1, "identification_number": 0}

    def update(self):
        """Update the position, mass, and actions of the cell"""
        self.mass -= self.mass * 0.0025 * self.attrib["metabolism"]  # Cells lose 0.25% of their mass per tick
        self.radius = math.sqrt(self.mass / math.pi) * 3   # Non-plant cells have greater radii per mass

        # If current target is alive, track it, otherwise find new target to track
        if self.target_cell["index"] >= 0 \
           and self.target_cell["index"] < len(Consumer.TARGET_LIST) \
           and self.target_cell["identification_number"] == Consumer.TARGET_LIST[self.target_cell["index"]].identification_number \
           and Consumer.TARGET_LIST[self.target_cell["index"]].living:
            # Make sure that the target from the previous cycle is still alive, and if not,
            # find new target
            self.move(self.target_direction())
        else:
            self.new_target()

        # Suffocation and consumption
        for other in Consumer.CELL_LIST:
            # loop through the list of other cells to check which will suffocate
            if (self.dist(other.position) - (self.radius)) < other.radius / -10 \
               and other.radius < self.radius:
                # if this cell overlaps another cell of the same type significantly, that cell dies, as if by "suffocation"
                other.living = False

        for other in Consumer.TARGET_LIST:
            # loop through the list of other cells to check which can be consumed
            if self.dist(other.position) < (self.radius) \
               and other.radius < self.radius:
                # if this cell is touching the center of another consumable cell, that cell gets eaten
                self.mass += other.mass
                other.living = False

        if self.mass < self.attrib["split_mass"] / 5: # Check if cell should still be alive
            self.living = False
        elif self.mass > self.attrib["split_mass"]: # Check if cell should split
            self.split(self.target_direction())

    def new_target(self):
        """Find new cell to chase and attempt to consume"""

        distance_to_target = Cell.FIELD_SIZE * Cell.FIELD_SIZE
        for cell in Consumer.TARGET_LIST: # Search for most desirable target, and save it's index and id
            if cell.mass < self.mass \
               and (cell.attrib["species"] == "plant") \
               and self.dist(cell.position) < distance_to_target \
               and not cell.identification_number == self.identification_number:
                self.target_cell = {"index": cell.index, "identification_number": cell.identification_number}
                distance_to_target = self.dist(Consumer.TARGET_LIST[self.target_cell["index"]].position)

    def target_direction(self):  # Chooses target based on species of cell
        """ Movement, for cells which are capable of it, uses the following decision procedure:
                Cells check the general attractiveness of areas of the field, with a higher concentration of food making it appear better, and a higher concentration of predators making it appear worse
                Once it is within what appears to be a good area, it will "see" a target that it should move toward to consume, only ceasing its pursuit if the target is first reached by another cell or a predator nears it and makes it attempt to flee
        """
        direction = math.atan2(
            (Consumer.TARGET_LIST[self.target_cell["index"]].position[1] - self.position[1]),  # Theta = atan2(y, x)
            (Consumer.TARGET_LIST[self.target_cell["index"]].position[0] - self.position[0]))  # Broken into multiplle lines for clarity
        return direction

        return self.target_direction(Consumer.TARGET_LIST)

    def move(self, angle=0, speed=(lambda x: (1 / (math.sqrt(x) / 20)))):  # Moves the cell (Note: angle is in radians), speed is function for determining the rate at which movement slows to when mass increases
        """ If cell is herbivore, moves towards and consumes plantlike cell, if cell is omnivore, targets nearest and biggest consumable cell of any species
        """
        self.position = [(self.position[0] + (math.cos(angle) * speed(self.mass) * self.attrib["metabolism"])),
                         (self.position[1] + (math.sin(angle) * speed(self.mass) * self.attrib["metabolism"]))]  # Once direction of movement is decided, moves cell in that direction, with speed dependent on metabolic rate and mass

    def split(self, angle):
        """Creates a new cell of the same type with a portion of the parent cell's mass"""
        new_position = [(self.position[0] + (math.cos(math.radians(angle)) * (self.radius * 2))),
                        (self.position[1] + (math.sin(math.radians(angle)) * (self.radius * 2)))]
        Consumer.CELL_LIST.append(Consumer(len(Consumer.CELL_LIST),
                                           new_position,
                                           self.mass / 3,
                                           self.attrib["split_mass"]))
        self.mass /= 2

class Spore(Cell):
    """Spores, these are invisible to other cells 
    and will spawn cells after a random time interval."""

    CELL_LIST = [] # List of Plant spores
    
    def __init__(self, position, mass, species, splitMass=200):
        self.position = position
        self.mass = mass
        self.species = species
        self.split_mass = splitMass
        self.incubation_timer = random.randint(100, 2000)
        self.radius = math.sqrt(self.mass / math.pi)
        self.attrib = {}
        self.attrib["species"] = species.lower
        Spore.CELL_LIST.append(self)

    def update(self):
        self.incubation_timer = self.incubation_timer - 1
        if self.incubation_timer < 1:
            self.germinate()

    def germinate(self):
        if self.species == "Plant":
            Plant.CELL_LIST.append(Plant(len(Plant.CELL_LIST),
                                         self.position,
                                         self.mass,
                                         self.split_mass))
        elif self.species == "Consumer":
            Consumer.CELL_LIST.append(Consumer(len(Consumer.CELL_LIST),
                                               self.position,
                                               self.mass,
                                               self.split_mass))
        else:
            error("invalid cell type")
        Spore.CELL_LIST.remove(self)
        
