# SBC Project - Expert System for the Battleship Game  


| "Gheorghe Asachi" Technical University of Iași<br>Faculty of Automatic Control and Computer Engineering<br>Department of Automatic Control and Applied Informatics | **SBC Project** |
|----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------|

**Authors:**  
`Taradaciuc_Nicolae`, `Vicol_Șerban-Ilie`, `Butacu_Ionel-Cătălin`

***

## Development of a Case-Based Expert System for the Battleship Game  

### **Abstract**

This project aimed to develop a case-based expert system
for the Battleship game. The solution our team came up with is a
system that is capable of changing its behavior depending on
the chosen difficulty, as well as on the situation in which the game is found. If
too many rounds pass in which it cannot find a ship on the game board
by using the bomb attack, then it will switch to using line attacks
or the scan attack in the desire to speed up the process of
locating a ship. To make these functionalities possible,
both the rule-based programming language was used to
describe the player's boards and the expert system, the attack types and
the mechanisms by which the two boards are updated, as well as
the Python programming language for creating a graphical interface
that is intuitive for the user.

## **1. Problem Statement. Objectives**

The problem proposed to be solved is the development of a case-based
expert system capable of making decisions regarding a new move with the purpose of
destroying all enemy ships (the human user) and winning the match.

The main purpose of the system is to destroy the opponent's ships by
using a single ability per round. In the case of a successful
hit, the system has the possibility to make a new decision and attack
again, based on its knowledge from the present environment.

The elements of interest are the ships, which can have two states (attacked or
not), the bomb and abilities (scan, etc). Bombs can be placed on a
single portion of the map, once per round.

In the end, the human user will be able to play against the system,
the latter changing its behavior and attack strategies depending on
the number of ships destroyed by the user.

Example hypothesis:

-   It is possible to hit until the moment when the hit is unsuccessful;

-   Both players have the possibility to attack(with a bomb) at least
    once in each round;

-   A single ability(scan) can be used by each
    player, per round;

-   If you have attacked a location, you will not be able to attack it again.

## **2. Description of the Universe of Discourse**

At the beginning of the game, the working environment will contain only "ships" and
"unattacked_position". During the game, the users "player" and
"expert_system" will attack each other using "bomb" or "ability".
A successful attack on a ship will result in changing the position
of a "ship" into "destroyed_ship_position", and a failed attack on an
"unattacked_position" will transform it into an "attacked_position". After
each portion of a "ship" is entirely transformed into
"attacked_ship_position", it will become "destroyed_ship", and
the portions will pass into the state “destroyed_ship_position".

### **a. Concepts**

The concepts used are: free_position, attacked_position, ship,
attacked_ship_position, destroyed_ship, bomb, ability, player,
expert_system

### **b. Properties**

Board T1 position (row, column) is free.

Board T1 position (row, column) is attacked.

Board T1 position (row, column) is occupied by ship N2 and is
attacked.

Board T1 position (row, column) is occupied by ship N3 and is
destroyed.

The system decides.

The system waits.

### **c. Relationships**

Board T1 ship N2 is located on positions ( x1, y1), (x2, y1), (x3, y1).

Board T1 position (row, column) is attacked with B.

### **d. Actions**

The action of attacking position (x, y) from Board T1 with B. This is
applicable only if the position has not been attacked previously.

The action of scanning position (x, y) from Board T2 with S. This is
applicable at any time, but the ability cannot be reused for 5
rounds.

## **3. Considered Scenarios**

Instance 1: Destroying a position on the game board

The expert system receives the command to attack a position on the game board
with a bomb-type attack.

Instance 2 : Destroying a line on the game board

The expert system receives the command to attack a position on the game board
with a line-type attack.

## **4. Solving Strategies**

For instance 1: Destroying a position on the game board

To solve this scenario, the expert system needs to take into
consideration two aspects:

-   Whether the position is already destroyed

-   Whether the position is occupied by a ship portion or not

Depending on the type of position, the expert system will consider it an attacked
free position or a position with an attacked ship portion.

For instance 2: Destroying a line on the game board

To solve this scenario, the expert system will use
the position that it receives in order to realize which line on the
game board must be destroyed. It will plan a series of bomb-type
attacks on all positions on that line, after which it will enter
the scenario above.

## **5. Definition of the Fact Base**

### a\. Fact Patterns

(Board \<Board_ID\> position \<row\> \<column\> is \<state\>)

(Board \<Board_ID\> position \<row\> \<column\> is occupied by ship
\<Ship_ID\> and is \<ship_position_state\>)

(Ship \<Ship_ID\> from position \<row\> \<column\> is attacked with
\<attack_type\>)

(System attacks position \<row\> \<column\> from board \<Board_ID\> with
\<attack_type\>)

(Player attacks position \<row\> \<column\> from board \<Board_ID\> with
\<attack_type\>)

(Horizontal ship \<Ship_ID\> row \<Row_ID\> on columns \<\<\<
column_indices\>\>\>)

(Vertical ship \<Ship_ID\> column \<Column_ID\> on rows \<\<\<
row_indices\>\>\>)

(Ship \<Ship_ID\> in board \<Board_ID\>)

(difficulty \<Difficulty_Level\>)

(update_map \<State\>)

(calculate_boundary \< row \> \<column\>)

(boundary \<top_left_corner_row\> \<top_left_corner_column\>
\<bottom_right_corner_row\> \<bottom_right_corner_column\>)

### b\. Description Through Unstructured Facts

The unstructured facts from instance 1:

-   Case for attacking a free position

> (Board T1 position 6 7 is free)
>
> (System attacks position 6 7 from board T1 with B)

-   Case for attacking a ship portion

> (Board T1 position 6 7 is occupied by ship N1 and is unattacked)
>
> (System attacks position 6 7 from board T1 with B)

## **6. Definition of the Rule Base**

In the situation in which attacking with B (bomb) a position from
the opponent's Board is chosen, and the position has not been attacked previously, then
this action is achievable. The solving of this situation is
materialized in the following rule named Actualizare_Teren_atacat_B:

If the system or the player attacks the position given by ?rand and ?coloana
from board ?Teren and the position is free, then it becomes
attacked.

In the situation in which the Actualizare_Teren_atacata_B rule led to the attacking
of a ship, we will provide a rule to update its state. The solving of
this situation is materialized in the following rule named
Actualizare_Nava_atacata_B:

If the system or the player attacks the position given by ?rand and ?coloana
from board ?Teren, the position is occupied by ship ?nava and is
unattacked, then the state of the ship becomes attacked.

In the situation in which attacking a line from the opponent's
Board is chosen, each position on that line will be attacked with a bomb,
provided that the position has not been attacked previously. The solving of
this situation is materialized in the following rules named
Atac_linie_jucator and Atac_linie_sistem:

If the system or the player attacks the line given by ?rand from board
?Teren, the free unattacked/free positions will become attacked.

In the situation in which scanning a portion from the opponent's
Board is chosen, each position in that portion will be scanned in order to
detect the presence of at least one ship without providing its exact position.
The solving of this situation is materialized in the following
rules named Atac_scanare_jucator and Atac_scanare_sistem:

If the system or the player selects a position for scanning,
the portion to be scanned will be a 3x3 matrix with the center in the
selected position (?rand, ?coloana) from board ?Teren, then the
message “There is a ship in the scanned area" will be sent.

## **7. Conflict Resolution**

### **7.1 Conflict Cases**

Conflict 1:

A conflict that was identified within the application is the closing,
opening, writing and reading from the file in an incorrect order,
which led to different errors such as "writing information to an
already closed file" and "reading from a file that has not yet been
opened".

Conflict 2:

Another identified conflict was the activation of the rule
Actualizare_Teren_atacat_B during the running of the Atac_linie_sistem
/ Atac_linie_jucator rules, which led to different errors such as updating
a position before the line attack was completed.

### **7.2 Conflict Resolution Strategies**

Conflict 1 resolution:

The strategy used to solve this conflict was the use of
priorities, giving the rules the following priorities:
Rule_Opening_File_Read (100), Rule_Reading_Map (99),
Rule_Closing_File_Read (98), Rule_Opening_File_Write (97),
Rule_Writing_In_Map (96), Update_Map_Command (96) and
Rule_Closing_File_Write (95).

Conflict 2 resolution:

The strategy used to solve this conflict was the use of
priorities, increasing the priority of the line attack to be greater
than the position update rule: Actualizare_Teren_atacat_B (1),
Atac_linie_sistem (10), Atac_linie_jucator (10).

## **8. Operating (Logical) Scheme. Decision Tree**

![A diagram of a company Description automatically
generated](.doc/image1.jpeg)

## **9. Using Clips in Another Application**

Language used: Python

Libraries used: clipspy \[2\], NumPy \[3\], PyQt5 \[4\]

Functions used:

-   clipspy \[2\] : clear, load, reset, eval, run, facts, activations

-   NumPy \[3\] : zeros, random

-   PyQt5 \[4\] : connect, emit, blockSignals, move, show, exec, exit,
    parentWidget, addWidget, addLayout, setCursor, moveCursor,
    updateGeometry setObjectName, setStyleSheet, setProperty,
    setAlignment, setCheckable, setEnabled, setText, setFont,
    setCentralWidget, setWindowTitle, setFixedSize, setReadOnly,
    currentDateTime

GUI interface description:

Before starting the game, we are greeted by a simple interface where
we must enter our name and select the difficulty level.
Choosing the difficulty level influences the aggressiveness of the
system's attacks, thus creating a personalized gameplay experience.

![A screenshot of a computer Description automatically
generated](.doc/image2.png)

The interface will present a battle territory divided into two
distinct boards, one for the player's ships (left) and the other for
the system's ships (right). In the first stage of the game, both the system
and the player will randomly place their ships in their own boards.
The ships that the player will place are located below their board.

![A screenshot of a computer game Description automatically
generated](.doc/image3.png)

As the game progresses, the player will be able to launch a series of
attacks against the enemy, attacks such as bombs, scanning, line attack,
these being visible below the enemy's board. During the
game, in both boards, each state (“Free/unattacked position",
“Attacked position", “Attacked ship", “Ship found but unattacked", "Scanned
and free ship") will be represented through a series of symbols
such as:

-   Blue square= Free/unattacked position

-   Light blue square with the gray "X" symbol = Attacked position ( without ship )

-   Light blue square with the red "X" symbol = Attacked ship

-   Blue square with the gray "?" symbol = Scanned and free position

-   Blue square with the yellow "?"symbol = Scanned ship, but unattacked

## **Conclusions**

Positive elements:

-   the interface, which is simple and intuitive, allowing players to
    start the game quickly, without going through other complicated steps

-   Personalization of the gameplay style by selecting the
    difficulty level.

-   The interactive feedback that is located at the top of the interface and
    gives us data about what actions take place during the game.

Negative elements:

-   The difficulty level could be extended by affecting the gameplay
    style in other ways as well and not only the system's attacks.

-   At the moment of scanning, the player knows the exact position of the ships on the
    map, not only a detail such as their existence or absence.

Possibilities for improvement:

-   Solving an error encountered in the integration of clips \[5\] with
    the Python interface.

-   Improving the system's search and attack algorithm
    (Currently, incomplete).

-   Adding an explanatory guide with a short description of each
    difficulty level and the differences between them.

-   Visual improvements to make the interface more attractive and
    engaging.

-   Modifying the scan attack to provide details such as
    the existence or absence of ships in that area, not the exact states
    of all scanned positions.

-   Adding a bomb as an object to be placed on the map, in order to create a
    more detailed gameplay experience.

## **Bibliography**

\[1\] Panescu D., Pascal C., Rule-Based Programming, Laboratory Guide, Conspress Publishing House, Bucharest, 2013, ISBN 978-973-100-258-3.\
\[2\] Documentation, clipspy library, <https://clipspy.readthedocs.io>\
\[3\] Documentation, NumPy library, <https://numpy.org/>\
\[4\] Documentation, PyQt5 library, <https://www.riverbankcomputing.com/static/Docs/PyQt5/>\
\[5\] Clips Manual, CLIPS Reference Manual Volume I Basic Programming Guide, Version 6.30 March 17th 2015

