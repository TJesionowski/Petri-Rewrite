import tkinter
import random
from cell import Cell

#Global constants
FIELD_SIZE = 1200
LIGHT_RADIUS = 200

# Instantiate canvas
canvas = tkinter.Tk()
field = tkinter.Canvas(canvas, height=FIELD_SIZE, width=FIELD_SIZE)
field.pack()

# Instantiate list of cells
entities = []

# Example cases for testing
entities.append(Cell(len(entities), [200, 200], 80))

entities.append(Cell(len(entities), [random.randint(0, 1200), random.randint(0, 1200)], 80))
entities.append(Cell(len(entities), [random.randint(0, 1200), random.randint(0, 1200)], 80))
entities.append(Cell(len(entities), [random.randint(0, 1200), random.randint(0, 1200)], 80))
entities.append(Cell(len(entities), [random.randint(0, 1200), random.randint(0, 1200)], 80))

entities.append(Cell(len(entities), [random.randint(0, 1200), random.randint(0, 1200)], 1000, "herbivore", 250))
entities.append(Cell(len(entities), [random.randint(0, 1200), random.randint(0, 1200)], 1000, "herbivore", 250))



# Update canvas
def updateField(cell_list):
    field.delete("all")

    field.create_rectangle(1, 1, FIELD_SIZE, FIELD_SIZE) # Draw border

    field.create_oval(FIELD_SIZE/2 - LIGHT_RADIUS, FIELD_SIZE/2 - LIGHT_RADIUS, FIELD_SIZE/2 + LIGHT_RADIUS, FIELD_SIZE/2 + LIGHT_RADIUS, fill="yellow") # Draw light source


    """ Draw Cells from cellList:
            Iterate over cells in list, getting location and size from cell.position, which returns a two-element list with the current x and y coordinates, and [Search domain actenortheast.org] actenortheast.org
More results
            In the future
    """
    for cell in cell_list:
        size = cell.radius
        x, y = cell.position

        # Set color of cell based on species
        if cell.attrib["species"] == "plant":
            color = "green"
        elif cell.attrib["species"] == "herbivore":
            color = "blue"
        else:
            color = "red"

        circle = field.create_oval(x - size, y - size, x + size, y + size, fill=color)

    canvas.update()

while True:
    updateField(entities)
    for cell in entities:
        cell.update(entities)
        if not cell.living:
            for count in range(cell.index, len(entities)): # if you remove a cell from the middle of the index, you need to tell the cells after the one you removed that their index has dcreased by one
                entities[count].index -= 1
            entities.remove(cell)
