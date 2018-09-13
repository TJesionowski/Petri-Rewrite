import tkinter
import random
from cell import Cell
from cell import Plant
from cell import Spore
from cell import Consumer
from cell import Predator

# Global constants
FIELD_SIZE = 1000
LIGHT_RADIUS = 200
Cell.FIELD_SIZE = FIELD_SIZE


# Instantiate canvas
CANVAS = tkinter.Tk()
FIELD = tkinter.Canvas(CANVAS, height=FIELD_SIZE, width=FIELD_SIZE)
FIELD.config(background="white")
FIELD.pack()

# Instantiate list of cells
plant_list = []
spore_list = []
consumer_list = []
predator_list = []
Plant.CELL_LIST = plant_list
Spore.CELL_LIST = spore_list
Consumer.CELL_LIST = consumer_list
Predator.CELL_LIST = predator_list

# Example cases for testing
Plant([FIELD_SIZE / 2, FIELD_SIZE / 2], 80)

Plant([random.randint(0, FIELD_SIZE), random.randint(0, FIELD_SIZE)], 80)
Plant([random.randint(0, FIELD_SIZE), random.randint(0, FIELD_SIZE)], 80)
Plant([random.randint(0, FIELD_SIZE), random.randint(0, FIELD_SIZE)], 80)
Plant([random.randint(0, FIELD_SIZE), random.randint(0, FIELD_SIZE)], 80)

Consumer([random.randint(0, FIELD_SIZE), random.randint(0, FIELD_SIZE)], 200)
Consumer([random.randint(0, FIELD_SIZE), random.randint(0, FIELD_SIZE)], 200)

Predator([1000, 1000], 400)


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
        color = entity.color

        FIELD.create_oval(x_pos - size, y_pos - size, x_pos + size, y_pos + size, fill=color)

    CANVAS.update()


def update_list(entity_list):
    """Update every entity in a list"""
    for entity in entity_list:
        entity.update()


def global_update():
    update_field(plant_list + consumer_list + spore_list + predator_list)

    update_list(plant_list)
    update_list(consumer_list)
    update_list(spore_list)
    update_list(predator_list)


# Update until simulation is killed
while True:
    global_update()
