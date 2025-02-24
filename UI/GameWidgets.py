# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 16:15:36 2024

@authors: Catalin.BUTACU, Serban.VICOL, Nicu.TARADACIUC
"""

import sys
import random
import numpy as np

from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QPushButton, QGridLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QIcon, QCursor
from PyQt5.QtGui import QPainter, QBrush, QColor, QFont

from UI.DataCollector import *
from UI.UI_Elements import ShipPlacementButton, AbilityPlacementButtons
from UI.ModuleWidgets import InfoWidget



### TERRAIN CLASSES
"""
    TerrainWidget - BASIC MAP
    > init ground with bunch of buttons and connect each button with place_item
    > keep in focus one ship to be placed and check for condition if it can be placed
    > will use 'isShipPlaced' property to know if a button/cell on the map is already assigned

"""
class TerrainWidget(QWidget):
    signal_decrese_count = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_ship:Ship = None
        self.selected_ability:Ability = None
        self.ships = []
        self.grid_size = 40
        self.squares = 10
        self.id_count = 0
        self.init_ui()
        self.data = self.init_data(10,10)

    def init_ui(self):
        layout = QGridLayout(self)
        layout.setObjectName("layoutGridTerrain")
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(0)
        self.setFixedSize(self.squares * self.grid_size, self.squares * self.grid_size)
        self.buttons = []
        for i in range(self.squares):
            row = []
            for j in range(self.squares):
                button = QPushButton(self)
                button.setObjectName("seaPosition")
                button.setFixedSize(self.grid_size, self.grid_size)
                button.setEnabled(True)
                button.setProperty("isShipPlaced","no")
                row.append(button)
                layout.addWidget(button, i, j)
                button.clicked.connect(lambda state, row = i, col = j: self.place_item(row, col))
            self.buttons.append(row)

    def init_data(self, W, H):
        matrix_state = np.zeros((W,H),dtype=int)
        for w in range(W):
            for h in range(H):
                matrix_state[w][h] = MapState.SPACE_FREE.value

        matrix_ids = np.zeros((W,H),dtype=int)
        matrix = {
            "state": matrix_state,
            "ids": matrix_ids
            }
        return matrix


    def place_item(self, row, col):
        # check for enemy terrain
        if self.parentWidget().objectName() == "EnemyTerrainWidget":
            if self.selected_ability:
                self.selected_ability.setRefPos(row, col)
                self.place_ability()

        # check for user terrain
        if self.parentWidget().objectName() == "UserTerrainWidget":
            parent = self.parentWidget()
            if parent.all_ships_placed == False:
                parent.check_ships_left()

            if parent.all_ships_placed:
                print("All ships have been placed.")
                return False

            if self.selected_ship is None:
                print("No ship selected.")
                return

            self.selected_ship.setRefPos(row, col)
            self.place_ship()


    def place_ship(self):
        if self.can_place_ship(self.selected_ship) == False:
            self.parentWidget().setCursor(Qt.ArrowCursor)
            self.selected_ship = None
            return

        x, y = self.selected_ship.refX, self.selected_ship.refY
        size = self.selected_ship.size
        self.update_matrix(x, y, size, self.selected_ship.orientation)

        self.deactivate_ship_cells()
        ship_image = QPixmap(self.selected_ship.image_path)

        scaleX, scaleY = self.selected_ship.get_size_px()
        ship_image = ship_image.scaled(scaleX, scaleY)

        if self.selected_ship.orientation == Ship.HORIZONTAL:
            for i in range(size):
                self.buttons[x][y + i].setIcon(QIcon(ship_image.copy(i * 40, 0, 40, 40)))
                self.buttons[x][y + i].setIconSize(QSize(40,40))
        else:
            for i in range(size):
                self.buttons[x + i][y].setIcon(QIcon(ship_image.copy(0, i * 40, 40, 40)))
                self.buttons[x + i][y].setIconSize(QSize(40,40))

        self.signal_decrese_count.emit(size)
        self.parentWidget().addMessageToConsole.emit(f"O nava de tip {self.selected_ship.name} de nivel {self.selected_ship.size} a fost plasată la poziția {x},{y}")
        self.parentWidget().check_ships_left()

        if self.parentWidget().all_ships_placed:
            self.parentWidget().emit_ships_placed()
            self.parentWidget().addMessageToConsole.emit("Toate navele au fost plasate în teren! ^-^")


    def place_ability(self):
        x, y = self.selected_ability.refX, self.selected_ability.refY
        print(f"O abilitate a fost plasată la poziția {x},{y}")

        if self.selected_ability.id == 1:
            self.place_bomb(x, y)
        elif self.selected_ability.id == 2:
            self.place_scan(x, y)
        elif self.selected_ability.id == 3:
            self.place_line_assault(x, y)

        self.parentWidget().setCursor(Qt.ArrowCursor)
        self.signal_decrese_count.emit(self.selected_ability.id)
        self.selected_ability = None

    def place_bomb(self, x, y):
        button = self.buttons[x][y]
        button.setEnabled(False)
        new_style = "color: red; font-size: 30px; font-weight: bold;" if self.data["ids"][x][y] != 0 else "color: #5D3FD3;"
        button.setStyleSheet(new_style)
        button.setText("X")
        self.data["state"][x][y] = MapState.SPACE_ATTACKED.value if self.data["ids"][x][y]==0 else MapState.SHIP_ATTACKED.value
        self.parentWidget().can_act = True if self.data["state"][x][y] == MapState.SHIP_ATTACKED.value else False

    def place_scan(self, x, y):
        info = InfoWidget.get_instance()
        difficulty = info.current_level
        area = 4 - difficulty
        for i in range(max(x-area,0), min(x+area+1,10)):
            for j in range(max(y-area,0), min(y+area+1,10)):
                new_style = "color: yellow; font-size: 30px; font-weight: bold;" if self.data["ids"][i][j] != 0 else "color: gray;"
                self.buttons[i][j].setStyleSheet(new_style)
                self.buttons[i][j].setText("?")

    def place_line_assault(self, x, y):
        for i in range(self.squares):
            self.place_bomb(x,i)

    def update_matrix(self,x,y,size,orientation):
        self.id_count += 1
        if orientation == self.selected_ship.VERTICAL:
            for i in range(size):
                self.data["state"][x+i][y] = MapState.SHIP_PLACED.value
                self.data["ids"][x+i][y] = self.id_count
        else:
            for i in range(size):
                self.data["state"][x][y+i] = MapState.SHIP_PLACED.value
                self.data["ids"][x][y+i] = self.id_count

        #print(self.data["state"])
        #print(self.data["ids"])


    def deactivate_ship_cells(self):
        x, y = self.selected_ship.refX, self.selected_ship.refY

        if self.selected_ship.orientation == Ship.HORIZONTAL:
            for i in range(self.selected_ship.size):
                self.buttons[x][y + i].blockSignals(True)
                self.buttons[x][y + i].setProperty("isShipPlaced","yes")
        else:
            for i in range(self.selected_ship.size):
                self.buttons[x + i][y].blockSignals(True)
                self.buttons[x + i][y].setProperty("isShipPlaced","yes")

    def deactivate_all_buttons(self):
        for i in range(self.squares):
            for j in range(self.squares):
                self.buttons[i][j].setCheckable(False)


    def can_place_ship(self, ship):
        # check for available deploiments
        count = 0
        if ship.size == 1:
            count = self.parentWidget().buttonT1.getCount()
        elif ship.size == 2:
            count = self.parentWidget().buttonT2.getCount()
        elif ship.size == 3:
            count = self.parentWidget().buttonT3.getCount()
        elif ship.size == 4:
            count = self.parentWidget().buttonT4.getCount()

        if count == 1:
            self.parentWidget().setCursor(Qt.ArrowCursor)

        if count == 0:
            self.parentWidget().addMessageToConsole.emit(f"Toate navele de nivel {ship.size} au fost plasate în teren.")
            return False

        # check for not covering other ships already placed
        size = ship.size
        row, col = ship.refX, ship.refY
        orientation = ship.orientation
        # print(f"size={size}, row={row}, col={col}, orientation={orientation}")

        if orientation == Ship.HORIZONTAL:
            if col + size - 1 >= self.squares:
                return False
            for i in range(size):
                if self.buttons[row][col + i].property("isShipPlaced") == "yes" :
                    self.parentWidget().addMessageToConsole.emit(f"A apărut o coliziune cu altă navă la poziția {row},{col+i}")
                    return False
        else:
            if row + size - 1 >= self.squares:
                return False
            for i in range(size - 1):
                if self.buttons[row + i][col].property("isShipPlaced") == "yes":
                    self.parentWidget().self.addMessageToConsole.emit(f"A apărut o coliziune cu altă navă la poziția {row+i},{col}")
                    return False

        return True


"""
    UserTerrainWidget - BASIC Widget
    > init UI subcomponents and ensure communication between widgets
    > let user place ships on the own map

"""
class UserTerrainWidget(QWidget):
    signal_all_ships_placed = pyqtSignal()  # will be used later to start the game
    addMessageToConsole = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("UserTerrainWidget")
        self.init_ui()
        self.all_ships_placed = False

    def init_ui(self):
        layout = QVBoxLayout(self)

        user_label = QLabel("Terenul tău ", self)
        user_label.setObjectName("userLabel")
        user_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(user_label)

        self.terrain_widget = TerrainWidget(self)
        layout.addWidget(self.terrain_widget)
        self.terrain_widget.signal_decrese_count.connect(self.decrease_count)

        navy_label = QLabel("Selectează nava pe care dorești să o poziționezi.", self)
        navy_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(navy_label)

        button_layout = QHBoxLayout()

        self.buttonT1 = ShipPlacementButton(tier=1, count=4, parent=self)
        self.buttonT2 = ShipPlacementButton(tier=2, count=3, parent=self)
        self.buttonT3 = ShipPlacementButton(tier=3, count=2, parent=self)
        self.buttonT4 = ShipPlacementButton(tier=4, count=1, parent=self)

        self.buttonT1.setObjectName("placeNavyTier1")
        self.buttonT2.setObjectName("placeNavyTier2")
        self.buttonT3.setObjectName("placeNavyTier3")
        self.buttonT4.setObjectName("placeNavyTier4")

        button_layout.addWidget(self.buttonT1)
        button_layout.addWidget(self.buttonT2)
        button_layout.addWidget(self.buttonT3)
        button_layout.addWidget(self.buttonT4)

        self.buttonT1.signal_ship_selected.connect(self.setSelectionShip)
        self.buttonT2.signal_ship_selected.connect(self.setSelectionShip)
        self.buttonT3.signal_ship_selected.connect(self.setSelectionShip)
        self.buttonT4.signal_ship_selected.connect(self.setSelectionShip)

        layout.addLayout(button_layout)

    def setSelectionShip(self, size:int, orientation:bool):
        self.terrain_widget.selected_ship = Ship(size, orientation)

    def check_ships_left(self):
        QTimer(self).start(1000)
        sum_control = self.buttonT1.getCount()
        sum_control += self.buttonT2.getCount()
        sum_control += self.buttonT3.getCount()
        sum_control += self.buttonT4.getCount()

        if sum_control == 0:
            self.all_ships_placed = True
            self.setCursor(Qt.ArrowCursor)

    def decrease_count(self, size:int):
        if size == 1:
            self.buttonT1.decrease_count()
        elif size == 2:
            self.buttonT2.decrease_count()
        elif size == 3:
            self.buttonT3.decrease_count()
        elif size == 4:
            self.buttonT4.decrease_count()

    def emit_ships_placed(self):
        self.signal_all_ships_placed.emit()

    def mouseReleaseEvent(self, event):
        if self.all_ships_placed == False:
            self.check_ships_left()


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_R and self.terrain_widget.selected_ship:
            self.terrain_widget.selected_ship.rotate()
            width, height = self.terrain_widget.selected_ship.get_size_px()
            self.setCursor(QCursor(QPixmap(self.terrain_widget.selected_ship.image_path).scaled(width, height), -1, -1))

    def get_changed_indices(old_matrix, new_matrix):
        changes = []
        old_state = old_matrix["state"]
        new_state = new_matrix["state"]
        
        for i in range(len(old_state)):
            for j in range(len(old_state[i])):
                if old_state[i][j] != new_state[i][j]:
                    changes.append((i, j))
        
        return changes

    def update_map_from_file(self, matrix:dict):
        changes = self.get_changed_indices(self.terrain_widget.data, matrix)
        for i, j in changes:
            self.update_ui_at_index(i, j, matrix["state"][i][j])

        self.terrain_widget.data = matrix

    def update_ui_at_index(self, i, j, new_state):
        if new_state == MapState.SHIP_ATTACKED:
            self.terrain_widget.buttons[i][j].setStyleSheet("color: red; font-size: 30px; font-weight: bold;")
            self.terrain_widget.buttons[i][j].setText("X")
            self.terrain_widget.buttons[i][j].setDisabled(True)
        elif new_state == MapState.SPACE_ATTACKED:
            self.terrain_widget.buttons[i][j].setStyleSheet("color: gray;")
            self.terrain_widget.buttons[i][j].setText("X")
            self.terrain_widget.buttons[i][j].setDisabled(True)


"""
    EnemyTerrainWidget - BASIC Widget
    > init UI subcomponents and ensure communication between widgets
    > let user use abilities on the enemy map

"""
class EnemyTerrainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EnemyTerrainWidget")
        self.can_act = True
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        enemy_label = QLabel("Terenul inamic", self)
        enemy_label.setObjectName("enemyLabel")
        enemy_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(enemy_label)

        self.terrain_widget = TerrainWidget(self)
        layout.addWidget(self.terrain_widget)
        self.terrain_widget.signal_decrese_count.connect(self.decrease_count)

        action_label = QLabel("Selectează o acțiune", self)
        action_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(action_label)

        self.button_layout = QHBoxLayout()

        self.bomb_button = AbilityPlacementButtons(1, 200, self)
        self.bomb_button.setObjectName("bombButton")
        self.bomb_button.signal_ability_selected.connect(self.drop_ability)
        self.button_layout.addWidget(self.bomb_button)

        self.scan_button = AbilityPlacementButtons(2, 1, self)
        self.scan_button.setObjectName("scanButton")
        self.scan_button.signal_ability_selected.connect(self.drop_ability)
        self.button_layout.addWidget(self.scan_button)

        self.line_assault_button = AbilityPlacementButtons(3, 2,  self)
        self.line_assault_button.setObjectName("lineAssaultButton")
        self.line_assault_button.signal_ability_selected.connect(self.drop_ability)
        self.button_layout.addWidget(self.line_assault_button)

        layout.addLayout(self.button_layout)

        self.init_ships()

    # algo place ships
    def init_ships(self):
        sizes = [4,3,3,2,2,2,1,1,1]
        id_ship_to_place = 0
        for s in sizes:
            x, y, o = self.select_random_ref_position(s)
            if (x, y, o) != (None, None, None):
                id_ship_to_place += 1
                self.place_ship_on_matrix(x, y, s, o, id_ship_to_place)
                # print(self.terrain_widget.data["ids"])
            else:
                print("Cannot place ship of size", s)

    def select_random_ref_position(self, size):
        orientation = random.choice([Ship.HORIZONTAL, Ship.VERTICAL])
        for _ in range(1000):  # Attempt a maximum of 1000 times to find a valid position
            x = random.randint(0, 9)
            y = random.randint(0, 9)
            if self.is_valid_position(x, y, size, orientation):
                return x, y, orientation
        return None, None, None

    def is_valid_position(self, x, y, sizes, orientation):
        # print(x,y,sizes)
        if orientation == Ship.HORIZONTAL:
            for i in range(sizes):
                if x + i >= self.terrain_widget.squares:
                    return False
                if self.terrain_widget.data["ids"][x + i][y]:
                    return False
        else:
            for i in range(sizes):
                if y + i >= self.terrain_widget.squares:
                    return False
                if self.terrain_widget.data["ids"][x][y + i]:
                    return False
        return True

    def place_ship_on_matrix(self, x, y, sizes, orientation, ship_id):
        if orientation == 'horizontal':
            for i in range(sizes):
                self.terrain_widget.data["state"][min(x + i,9)][y] = MapState.SHIP_PLACED.value
                self.terrain_widget.data["ids"][min(x + i,9)][y] = ship_id
        else:
            for i in range(sizes):
                self.terrain_widget.data["state"][x][min(y + i,9)] = MapState.SHIP_PLACED.value
                self.terrain_widget.data["ids"][x][min(y + i,9)] = ship_id

    def drop_ability(self, id_ability:int):
        self.terrain_widget.selected_ability = Ability(id_ability)

    def decrease_count(self, id_ability:int):
        if id_ability == 1:
            self.bomb_button.decrease_count()
        elif id_ability == 2:
            self.scan_button.decrease_count()
        elif id_ability == 3:
            self.line_assault_button.decrease_count()

        if self.can_act == False:
           self.bomb_button.setEnabled(False)
           self.scan_button.setEnabled(False)
           self.line_assault_button.setEnabled(False)



def load_styles_from_file(root, file_path):
    try:
        with open(file_path, "r") as file:
            style_sheet = file.read()
            root.setStyleSheet(style_sheet)
    except FileNotFoundError:
        print(f"Stylesheet file not found: {file_path}")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = QWidget()
    layout = QVBoxLayout(window)

    user_terrain = UserTerrainWidget() # UserTerrainWidget() # EnemyTerrainWidget(window)
    layout.addWidget(user_terrain)
    load_styles_from_file(window, "UI/styles.qss")

    window.show()
    sys.exit(app.exec_())
