import math
import random


class Cell:
    """General class for cells"""
    CELL_LIST = []
    FIELD_SIZE = 1000

    def __init__(self, position, mass, color="brown", split_mass=200):
        self.metabolism = 50 / split_mass
        self.position = position  # X and Y coordinates of cell as list of [x, y]
        self.mass = mass
        self.radius = math.sqrt(self.mass / math.pi) * 5  # Set radius for use in rendering and interacting with other cells and world
        self.color = color
        self.split_mass = split_mass
        Cell.CELL_LIST.append(self)

        # Check for bounds
        self.check_bounds()

    def check_bounds(self):
        if self.position[0] > Cell.FIELD_SIZE \
           or self.position[1] > Cell.FIELD_SIZE \
           or self.position[0] < 0 \
           or self.position[1] < 0:
            self.die()

    def update(self):
        """Update the position, mass, and actions of the cell"""
        self.mass -= self.mass * 0.001 * self.metabolism  # Cells lose one thousandth of their mass per tick

        # Update radius

        # Check for suffocation or consumption

        # Split if able

        # Die if mass below threshold

    def dist(self, other_position):
        """Calculate distance between two points"""
        return math.sqrt(math.pow(self.position[0] - other_position[0],
                                  2) \
                         + math.pow(self.position[1] - other_position[1],
                                    2))

    def die(self):
        if self in Cell.CELL_LIST:
            Cell.CELL_LIST.remove(self)


class Plant(Cell):
    """Plant cell sub-type:
        Capable of photosynthesizing light into energy, incapable of movement and consuming other cells.
        Suffocate out neighboring cells if it overlaps the other cell's center"""

    CELL_LIST = []  # List of cells of this type

    def __init__(self, position, mass):
        # Plants are green and have a split mass of 200
        Plant.CELL_LIST.append(self)
        super().__init__(position, mass, "green", 200)

    def die(self):
        """Death is simply getting removed from all lists"""
        # 1 in 10 chance to spawn a spore
        if random.randint(1, 10) == 1:
            Spore(self.position,
                  self.mass / 3,
                  "Plant")
        super().die()
        if self in Plant.CELL_LIST:
            Plant.CELL_LIST.remove(self)

    def update(self):
        """Update the position, mass, and actions of the cell"""

        # Cells lose one thousandth of their mass per tick
        self.mass -= self.mass * 0.001 * self.metabolism

        # Plant cells gain a certain amount of mass per update cycle, depending on distance from the light source
        self.mass += (self.calc_light() / 100) * self.mass

        # Set radius for use in rendering and interacting with other cells and world
        self.radius = math.sqrt(self.mass / math.pi) * 2

        for other in Plant.CELL_LIST:
            # loop through the list of other cells to check which will suffocate
            if (self.dist(other.position) - (self.radius)) < 0  \
               and other.radius > self.radius:
                # if this cell overlaps another cell of the same type significantly, that cell dies, as if by "suffocation"
                self.die()

        # Check if cell should still be alive
        if self.mass < self.split_mass / 5:
            self.die()
        # Check if cell should split
        elif self.mass > self.split_mass:
                self.split(random.randint(0, 360))

    def split(self, angle):
        """Creates a new cell of the same type with a portion of the parent cell's mass"""

        # new cell spawns 4 cell radii away form the parent cell
        new_position = [(self.position[0] + (math.cos(math.radians(angle)) * (self.radius * 4))),
                        (self.position[1] + (math.sin(math.radians(angle)) * (self.radius * 4)))]

        # child cells have a third of their parent cells mass
        Plant(new_position,
              self.mass / 3)

        # cells lose half their mass when splitting
        self.mass /= 2
        self.check_bounds()

    def calc_light(self):
        # Calculate the amount of light reaching cell; by default the light loses 50% of its strength per 100 pixels
        """ Calculate amount of light reaching herbivorous cell"""
        distance = self.dist([Cell.FIELD_SIZE / 2,
                              Cell.FIELD_SIZE / 2])
        # Light energy falls off with distance
        return 1 / (1 + distance / 180)


class Spore(Cell):
    """Spores, these are invisible to other cells
    and will spawn cells after a random time interval."""

    CELL_LIST = []  # List of Plant spores

    def __init__(self, position, mass, species):
        """Spores are black, do not split, and have a far smaller radius"""
        Spore.CELL_LIST.append(self)
        super().__init__(position, mass, "black", 1)
        self.incubation_timer = random.randint(100, 2000)
        self.radius = math.sqrt(self.mass / math.pi)
        self.species = species
        if self.species == "Plant":
            self.color = "green"
        elif self.species == "Consumer":
            self.color = "blue"
        elif self.species == "Predator":
            self.color = "red"

    def die(self):
        super().die()
        Spore.CELL_LIST.remove(self)

    def update(self):
        self.incubation_timer = self.incubation_timer - 1
        if self.incubation_timer < 1:
            self.germinate()

    def germinate(self):
        if self.species == "Plant":
            Plant(self.position,
                  self.mass)
        elif self.species == "Consumer":
            Consumer(self.position,
                     self.mass)
        elif self.species == "Predator":
            Predator(self.position,
                     self.mass)
        self.die()


class Consumer(Cell):
    """Consumer cell subclass:
        Capable of consuming other cells; moves to nearest desirable target
        Other cell is consumed if its central point is overlapped"""

    CELL_LIST = []  # List of cells of this type

    def __init__(self, position, mass):
        # Consumers are blue and have a split mass of 400

        Consumer.CELL_LIST.append(self)
        super().__init__(position, mass, "blue", 400)
        self.target_cell = self
        self.new_target()

    def die(self):
        """Death is simply getting removed from all lists"""
        # 1 in 10 chance to spawn a spore
        if random.randint(1, 6) == 1:
            Spore(self.position,
                  self.mass / 3,
                  "Consumer")
        Consumer.CELL_LIST.remove(self)
        super().die()

    def update(self):
        """Update the position, mass, and actions of the cell"""

        # Cells lose 0.0025% of their mass per tick
        self.mass -= self.mass * 0.0035 * self.metabolism

        # Non-plant cells have greater radii per mass
        self.radius = math.sqrt(self.mass / math.pi) * 3

        # Check whether any predators are nearby, if so, set self.hunter to the cell so that evasive action may be taken
        self.hunter = self.check_predators()

        # If current target is alive, track it, otherwise find new target to track
        if self.target_cell in Plant.CELL_LIST:  # Make sure that the target from the previous cycle is still alive, and if not find new target
            if self.hunter != -1:
                self.move(-self.target_direction(self.hunter))
            self.move(self.target_direction(self.target_cell))
        else:
            self.new_target()
            if self.hunter != -1:
                self.move(-self.target_direction(self.hunter))
            self.move(self.target_direction(self.target_cell))

        # consumption
        for other in Plant.CELL_LIST:
            # loop through the list of other cells to check which can be consumed
            if self.dist(other.position) < (self.radius) and other.radius < self.radius:
                # if this cell is touching the center of another consumable cell, that cell gets eaten
                self.mass += other.mass
                other.die()

        # for other in Consumer.CELL_LIST:
        #     # loop through the list of other cells to check which will suffocate
        #     if (self.dist(other.position) - (self.radius)) < other.radius / -10  and other.radius > self.radius:
        #         # if this cell overlaps another cell of the same type significantly, that cell dies, as if by "suffocation"
        #         self.die()

        if self.mass < self.split_mass / 5:  # Check if cell should still be alive
            self.die()
        elif self.mass > self.split_mass:  # Check if cell should split
            self.new_target()
            self.split(self.target_direction(self.target_cell))

    def new_target(self):
        """Find new cell to chase and attempt to consume"""

        distance_to_target = Cell.FIELD_SIZE * Cell.FIELD_SIZE
        for cell in Plant.CELL_LIST:  # Search for most desirable target, and save it's index and id
            if cell.mass < self.mass \
               and self.dist(cell.position) < distance_to_target:
                self.target_cell = cell
                distance_to_target = self.dist(self.target_cell.position)

    def target_direction(self, target_cell):  # Chooses target based on species of cell
        """ Movement, for cells which are capable of it, uses the following decision procedure:
                Cells check the general attractiveness of areas of the field, with a higher concentration of food making it appear better, and a higher concentration of predators making it appear worse
                Once it is within what appears to be a good area, it will "see" a target that it should move toward to consume, only ceasing its pursuit if the target is first reached by another cell or a predator nears it and makes it attempt to flee """
        direction = math.atan2(
            (target_cell.position[1] - self.position[1]),  # Theta = atan2(y, x)
            (target_cell.position[0] - self.position[0]))  # Broken into multiplle lines for clarity
        return direction

    def check_predators(self):
        """Check whether any predators have entered the cell's immediate vicinity"""
        for other in Predator.CELL_LIST:
            if self.dist(other.position) < self.radius * 5:
                return other

        return -1

    def move(self, angle=0):
        """Moves the cell, takes an angle in radians. """
        speed = 25 / math.log(self.mass) * self.metabolism
        self.position = [self.position[0] + (math.cos(angle) * speed),
                         self.position[1] + (math.sin(angle) * speed)]  # Once direction of movement is decided, moves cell in that direction, with speed dependent on metabolic rate and mass
        self.check_bounds()

    def split(self, angle):
        """Creates a new cell of the same type with a portion of the parent cell's mass"""
        new_position = [(self.position[0] + (math.cos(math.radians(angle)) * (self.radius * 2))),
                        (self.position[1] + (math.sin(math.radians(angle)) * (self.radius * 2)))]
        Consumer(new_position,
                 self.mass / 3)
        self.mass /= 3
        self.check_bounds()


class Predator(Cell):
    """Predator cell subclass:
    Hunts herbivorous cells as well as others of their kind"""

    CELL_LIST = []  # List of cells of this type

    def __init__(self, position, mass):
        # Predators are red and have a split mass of 500

        Predator.CELL_LIST.append(self)
        super().__init__(position, mass, "red", 600)
        self.metabolism = 100 / self.split_mass
        self.target_cell = self
        self.new_target()

    def die(self):
        """Death is simply getting removed from all lists"""
        # 1 in 10 chance to spawn a spore
        Spore(self.position,
              self.mass / 3,
              "Predator")
        Predator.CELL_LIST.remove(self)
        super().die()

    def update(self):
        """Update the position, mass, and actions of the cell"""

        # Cells lose 0.0025% of their mass per tick
        self.mass -= self.mass * 0.003 * self.metabolism

        # Non-plant cells have greater radii per mass
        self.radius = math.sqrt(self.mass / math.pi) * 4

        # If current target is alive, track it, otherwise find new target to track
        if self.target_cell in Consumer.CELL_LIST:
            # Make sure that the target from the previous cycle is still alive, and if not find new target
            self.move(self.target_direction())
        else:
            self.new_target()
            self.move(self.target_direction())

        # consumption
        for other in Consumer.CELL_LIST + Predator.CELL_LIST:
            # loop through the list of other cells to check which can be consumed
            if self.dist(other.position) < (self.radius) and other.radius < self.radius:
                # if this cell is touching the center of another consumable cell, that cell gets eaten
                self.mass += other.mass
                other.die()

        if self.mass < self.split_mass / 6:  # Check if cell should still be alive
            self.die()
        elif self.mass > self.split_mass:  # Check if cell should split
            self.new_target()
            self.split(self.target_direction())

    def new_target(self):
        """Find new cell to chase and attempt to consume"""

        distance_to_target = Cell.FIELD_SIZE * Cell.FIELD_SIZE
        for cell in Consumer.CELL_LIST:  # Search for most desirable target, and save it's index and id
            if cell.mass < self.mass * 2 \
               and self.dist(cell.position) < distance_to_target:
                self.target_cell = cell
                distance_to_target = self.dist(self.target_cell.position)

    def target_direction(self):  # Chooses target based on species of cell
        """Track this cell's quarry"""
        direction = math.atan2(
            (self.target_cell.position[1] - self.position[1]),  # Theta = atan2(y, x)
            (self.target_cell.position[0] - self.position[0]))  # Broken into multiplle lines for clarity
        return direction

    def move(self, angle=0):
        """Moves the cell, takes an angle in radians. """
        speed = 15 / math.log(self.mass) * self.metabolism
        self.position = [self.position[0] + (math.cos(angle) * speed),
                         self.position[1] + (math.sin(angle) * speed)]  # Once direction of movement is decided, moves cell in that direction, with speed dependent on metabolic rate and mass
        self.check_bounds()

    def split(self, angle):
        """Creates a new cell of the same type with a portion of the parent cell's mass"""
        new_position = [(self.position[0] + (math.cos(math.radians(angle)) * (self.radius * 2))),
                        (self.position[1] + (math.sin(math.radians(angle)) * (self.radius * 2)))]
        Predator(new_position,
                 self.mass / 3)
        self.mass /= 3
        self.check_bounds()
