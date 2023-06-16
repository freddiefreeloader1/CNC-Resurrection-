# CNC-Resurrection
ME462 Term Project 

Main goals:
- Create a generic controller for the out of order CNC machines
- Come up with a ROS2 based universal remote handwheel/controller, mainly for the CNC's, but it should be applicable for other uses as well

Stepper Pairs:
-Pins BH and Pins DF

CNC Milling Machine Specs:
-Pitch of the lead screws : 1mm
-UGS Parameters:
--Step size of axes : 800pulse/mm
--Max Travel Rate : 150
Do not increase feed rate more than 100mm/min. It staggers motors because motors cannot catch that pulse speed.
