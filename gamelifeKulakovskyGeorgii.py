import os
import time
from threading import Thread
from pynput import keyboard

base = []
height = int(input("высота? = "))
width = int(input("ширина? = "))
cell = "0"
void = "_"
cursor = "X"
updatetime = 0.3
border_size = 3

movedir = 0
sel=False
exit=False
cursorpos=[3,3]

kill=False

for i in range(height):
    base.append([])
    for v in range(width):
        base[i].append(void)
print("\nWASD - двигать курсор; F - поставить клетку сверху (если сверху нет места то снизу). \nНаступите/зайдите на живую клетку курсором чтобы её раздавить/удалить. Нажмите X чтобы завершить редактирование. Раскладка клавиатуры английская\n")
print("Я не понял что и куда добавлять ! поэтому тут его нет\n")
input("Нажмите любую клавишу чтобы продолжить ")
def keyb():
    global kill
    global movedir
    global sel
    global exit
    def on_press(key):
        global movedir
        global kill
        global sel
        global exit
        try:
            if key.char == "w":
                movedir = 1
            elif key.char == "a":
                movedir = 2
            elif key.char == "s":
                movedir = 3
            elif key.char == "d":
                movedir = 4
            elif key.char == "f":
                sel=True
            elif key.char == "x":
                exit = True
                if kill == True:
                    return False
        except Exception as e : print (f"\t\t\t\t\tПроизошла ошибка: {e}")
        
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
thrkeyb=Thread(target=keyb)
thrkeyb.start()

def monitor_start():
    os.system("cls")
    for i in base:
        for v in i:
            print(v,end="")
        print("")
cursorLastPlc=[]
while True:
    monitor_start()
    if movedir==1:
        movedir =0
        if cursorpos[0]>0:
            cursorpos[0]-=1
    elif movedir==2:
        movedir =0
        if cursorpos[1]>0:
            cursorpos[1]-=1
    elif movedir==3:
        movedir =0
        if cursorpos[0]<height-1:
            cursorpos[0]+=1
    elif movedir==4:
        movedir =0
        if cursorpos[1]<width-1:
            cursorpos[1]+=1
    if exit == True:
        exit =False
        kill = True
        base[cursorpos[0]][cursorpos[1]] = void
        break
    if sel == True:
        sel = False
        if cursorpos[0]>0:
            base[cursorpos[0]-1][cursorpos[1]] = cell
        else:
            base[cursorpos[0]+1][cursorpos[1]] = cell
        monitor_start()
    if len(cursorLastPlc)>0:
        base[cursorLastPlc[0][0]][cursorLastPlc[0][1]] = void
        cursorLastPlc.pop(0)
    cursorLastPlc.append([cursorpos[0],cursorpos[1]])
    base[cursorpos[0]][cursorpos[1]] = cursor
    time.sleep(0.1)

def count_neighbors(grid, row, col):
    count = 0

    
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            
            new_row = row + i
            new_col = col + j
            

            if new_col < 0:
                new_col = width-1
            if new_col > width-1:
                new_col = 0
            if new_row > height-1:
                new_row = 0
            if new_row < 0:
                new_row = height-1
            if grid[new_row][new_col] == cell:
                count += 1
    return count

# def expand_if_needed(grid):
#     height = len(grid)
#     width = len(grid[0])
    
#     need_top = any(grid[i][j] == cell for i in range(border_size) for j in range(width))
#     need_bottom = any(grid[i][j] == cell for i in range(height - border_size, height) for j in range(width))
#     need_left = any(grid[i][j] == cell for i in range(height) for j in range(border_size))
#     need_right = any(grid[i][j] == cell for i in range(height) for j in range(width - border_size, width))
    
#     if need_top:
#         for _ in range(5):
#             grid.insert(0, [void] * width)
    
#     if need_bottom:
#         for _ in range(5):
#             grid.append([void] * width)
    
#     height = len(grid)
#     width = len(grid[0])
    
#     if need_left:
#         for i in range(height):
#             for _ in range(5):
#                 grid[i].insert(0, void)
    
#     if need_right:
#         for i in range(height):
#             for _ in range(5):
#                 grid[i].append(void)
    
#     return grid

def next_generation(grid):

    new_grid = []
    
    for i in range(height):
        new_row = []
        for j in range(width):
            neighbors = count_neighbors(grid, i, j)
            current_cell = grid[i][j]
            
            if current_cell == cell:
                if neighbors == 2 or neighbors == 3:
                    new_row.append(cell)
                else:
                    new_row.append(void)
            else:
                if neighbors == 3:
                    new_row.append(cell)
                else:
                    new_row.append(void)
        
        new_grid.append(new_row)
    
    return new_grid

generation = 0

while True:
    os.system("cls")

    #base = expand_if_needed(base)

    height = len(base)
    width = len(base[0])
    alive_cells = sum(row.count(cell) for row in base)
    display_rows = base
    
    for row in display_rows:
        print("".join(row))

    base = next_generation(base)
    generation += 1
    print("=" * width)
    print(f"Поколение: {generation} | Живых клеток: {alive_cells}")
    print("Нажмите x чтобы завершить...")
    if exit == True:
        break
    time.sleep(updatetime)

