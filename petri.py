import tkinter
import random
from cell import Cell
from cell import Plant
from cell import Consumer
from cell import Spore

# Global constants
FIELD_SIZE = 1200
LIGHT_RADIUS = 200

# Instantiate canvas
CANVAS = tkinter.Tk()
FIELD = tkinter.Canvas(CANVAS, height=FIELD_SIZE, width=FIELD_SIZE)
FIELD.pack()

# Instantiate list of cells
plant_list = []
consumer_list = []
spore_list = []
Cell.FIELD_SIZE = FIELD_SIZE
Plant.CELL_LIST = plant_list
Consumer.CELL_LIST = consumer_list
Consumer.TARGET_LIST = plant_list
Spore.CELL_LIST = spore_list

# Example cases for testing
plant_list.append(Plant(len(plant_list), [200, 200], 80))

plant_list.append(Plant(len(plant_list), [random.randint(0, 1200), random.randint(0, 1200)], 80))
plant_list.append(Plant(len(plant_list), [random.randint(0, 1200), random.randint(0, 1200)], 80))
plant_list.append(Plant(len(plant_list), [random.randint(0, 1200), random.randint(0, 1200)], 80))
plant_list.append(Plant(len(plant_list), [random.randint(0, 1200), random.randint(0, 1200)], 80))

consumer_list.append(Consumer(len(consumer_list), [random.randint(0, 1200), random.randint(0, 1200)], 1000, 250))
consumer_list.append(Consumer(len(consumer_list), [random.randint(0, 1200), random.randint(0, 1200)], 1000, 250))


# Update canvas
def update_field(cell_list):
    """Use previous state of field to generate the next frame"""
    FIELD.delete("all")

    FIELD.create_rectangle(1, 1, FIELD_SIZE, FIELD_SIZE)  # Draw border

    FIELD.create_oval(FIELD_SIZE / 2 - LIGHT_RADIUS, FIELD_SIZE / 2 - LIGHT_RADIUS, FIELD_SIZE / 2 + LIGHT_RADIUS, FIELD_SIZE / 2 + LIGHT_RADIUS, fill="yellow")  # Draw light source

    """ Draw Cells from cell_list:
        Iterate over cells in list, getting location and size from cell.position, which returns a two-element list with the current x and y coordinates,
        then create circle of radius returned by the cell; color according to type
    """
    for entity in cell_list:
        size = entity.radius
        x_pos, y_pos = entity.position

        # Set color of cell based on species
        if entity.attrib["species"] == "plant":
            color = "green"
        elif entity.attrib["species"] == "herbivore":
            color = "blue"
        else:
            color = "red"

        FIELD.create_oval(x_pos - size, y_pos - size, x_pos + size, y_pos + size, fill=color)

    CANVAS.update()


while True:
    update_field(plant_list + consumer_list + spore_list)
    for entity in plant_list:
        entity.update()
        if not entity.living or entity.position[0] > FIELD_SIZE or entity.position[1] > FIELD_SIZE or entity.position[0] < 0 or entity.position[1] < 0:  # If entity is dead or outside of bounds, remove it
            for count in range(entity.index, len(plant_list)):  # If you remove a cell from the middle of the index, you need to tell the cells after the one you removed that their index has decreased by one
                plant_list[count].index -= 1
            plant_list.remove(entity)

    for entity in consumer_list:
        entity.update()
        if not entity.living or entity.position[0] > FIELD_SIZE or entity.position[1] > FIELD_SIZE or entity.position[0] < 0 or entity.position[1] < 0:  # If entity is dead or outside of bounds, remove it
            for count in range(entity.index, len(consumer_list)):  # If you remove a cell from the middle of the index, you need to tell the cells after the one you removed that their index has decreased by one
                consumer_list[count].index -= 1
            consumer_list.remove(entity)

    for entity in spore_list:
        entity.update()
        # spores need no additional code
