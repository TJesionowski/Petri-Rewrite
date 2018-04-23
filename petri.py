import tkinter
import random
from cell import Cell

#Global constants
FIELD_SIZE = 1200
LIGHT_RADIUS = 200

# Instantiate canvas
CANVAS = tkinter.Tk()
FIELD = tkinter.Canvas(CANVAS, height=FIELD_SIZE, width=FIELD_SIZE)
FIELD.pack()

# Instantiate list of cells
entity_list = []

# Example cases for testing
entity_list.append(Cell(len(entity_list), [200, 200], 80))

entity_list.append(Cell(len(entity_list), [random.randint(0, 1200), random.randint(0, 1200)], 80))
entity_list.append(Cell(len(entity_list), [random.randint(0, 1200), random.randint(0, 1200)], 80))
entity_list.append(Cell(len(entity_list), [random.randint(0, 1200), random.randint(0, 1200)], 80))
entity_list.append(Cell(len(entity_list), [random.randint(0, 1200), random.randint(0, 1200)], 80))

entity_list.append(Cell(len(entity_list), [random.randint(0, 1200), random.randint(0, 1200)], 1000, "herbivore", 250))
entity_list.append(Cell(len(entity_list), [random.randint(0, 1200), random.randint(0, 1200)], 1000, "herbivore", 250))



# Update canvas
def updateField(cell_list):
    """Use previous state of field to generate the next frame"""
    FIELD.delete("all")

    FIELD.create_rectangle(1, 1, FIELD_SIZE, FIELD_SIZE) # Draw border

    FIELD.create_oval(FIELD_SIZE/2 - LIGHT_RADIUS, FIELD_SIZE/2 - LIGHT_RADIUS, FIELD_SIZE/2 + LIGHT_RADIUS, FIELD_SIZE/2 + LIGHT_RADIUS, fill="yellow") # Draw light source


    """ Draw Cells from cellList:
            Iterate over cells in list, getting location and size from cell.position, which returns a two-element list with the current x and y coordinates,
    then create circle of radius returned by the cell; color according to type
   """
    for i in cell_list:
        size = i.radius
        x_pos, y_pos = i.position

        # Set color of cell based on species
        if i.attrib["species"] == "plant":
            color = "green"
        elif i.attrib["species"] == "herbivore":
            color = "blue"
        else:
            color = "red"

        FIELD.create_oval(x_pos - size, y_pos - size, x_pos + size, y_pos + size, fill=color)

    CANVAS.update()

while True:
    updateField(entity_list)
    for i in entity_list:
        i.update(entity_list)
        if not i.living:
            for count in range(i.index, len(entity_list)): # if you remove a cell from the middle of the index, you need to tell the cells after the one you removed that their index has dcreased by one
                entity_list[count].index -= 1
            entity_list.remove(i)
