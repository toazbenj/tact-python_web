# -*- coding: utf-8 -*-
"""
Tandem Control Game

    Try
        Make graphics window
        Register and tare sensors
        Register haptic files
        Make ball graphic
        Set conditions
        
        Main loop
            Spawn target
            
            Movement loop
                Get position data
                Select haptics direction
                Play haptics, return recorded values
                Convert sensor angle movement to ball movement
                Speed limit
                Respawn ball if out of bounds
                Checks for hit target
                
        Close window
        Close sensors
        Display Score
        
    Except KeyboadInterrupt
        Try
            Close window
            Close sensors
            Display Score
            
        Except NameError
            Close window
            Close dongle
            Display Score
    
Reference: http://anh.cs.luc.edu/handsonPythonTutorial/graphics.html

Created on Thu Dec 23 08:19:17 2021
@author: Ben Toaz
"""

import graphics
import utilitiesMethods as utilities
from math import pi
from time import perf_counter
from random import randint
import csv

angle_dict = {'a': pi, 'wd': pi/4, 'd': 2*pi, 'wa': 3*pi/4, 'w': pi/2,
              'sa': 5*pi/4, 's': 3*pi/2, 'sd': 7*pi/4}

try:
    # Make Window
    x_bounds = 750
    y_bounds = 500
    window = graphics.GraphWin(width = x_bounds, height = y_bounds)
    
    # Register and Tare Sensors
    teacher, student, dongle = utilities.getDevices()
    
    # Register haptic files
    iteration = 4
    utilities.register(iteration)
    
    # Make Ball
    point = graphics.Point(x_bounds/2, y_bounds/2)
    
    ball = graphics.Circle(point, 25)
    ball.setOutline('blue')
    ball.setFill('blue')
    ball.draw(window)
    
    # Sentinels/Conditions
    time = 0
    start = perf_counter()
    commandTime = 0
    tolerance = pi/96
    miss_margin = 10
    speed_limit = 15
    score = 0
    index = ''
    file ='gameDemo.csv'
    
    header = ['Time','Teacher-x','Teacher-y','Teacher-z','Student-x',
              'Student-y','Student-z','Difference-x','Difference-y',
              'Difference-z','Intensity','Angle','Score']
    
    # Open data file, write header
    with open(file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header)
        
    # Main Loop, 1 minute run time
    while time < 60:
        # Remake Target
        x_coord = x_bounds * randint(2, 9)/10
        y_coord = y_bounds * randint(2, 9)/10
        
        point = graphics.Point(x_coord,y_coord)
        target = graphics.Circle(point,30)
        target.setOutline('red')
        target.draw(window)        
        
        # Movement Loop
        while True:    
            
            # Get position data
            teacher_tup = teacher.getStreamingBatch()
            student_tup = student.getStreamingBatch()
            difference_tup = difference_tup = (student_tup[0]-teacher_tup[0], 
                                   student_tup[1]-teacher_tup[1],
                                   student_tup[2]-teacher_tup[2])
            
            # Select haptics direction
            index = utilities.getIndex(difference_tup, tolerance)
            
            # Play haptics, return values for recording
            angle, intensity, commandTime = utilities.advancedPlay(
                index, difference_tup, start, commandTime, iteration)
            
            # Convert sensor angle movement to ball movement
            if utilities.checkTolerance(teacher_tup, tolerance) and\
                utilities.checkTolerance(student_tup, tolerance):
                    
                x_move = (teacher_tup[1]+student_tup[1]) / (2*pi/4) * 10
                y_move = (teacher_tup[2]+student_tup[2]) / (2*pi/4) * 10                
            else:
                x_move = 0 
                y_move = 0
                        
            # If speed limit exceeded, sets speed to limit in same direction
            if abs(x_move) > speed_limit:
                x_move = speed_limit * (x_move/x_move)
            if abs(y_move) > speed_limit:
                y_move = speed_limit * (y_move/y_move)
            
            ball.move(-x_move,-y_move)
            
            # Respawns ball in center of window if out of bounds
            if ball.getCenter().x > x_bounds or ball.getCenter().y > y_bounds\
                or ball.getCenter().x < 0 or ball.getCenter().y < 0:
                
                point.undraw()
                ball.undraw()
                
                pt = graphics.Point(x_bounds/2, y_bounds/2)
                ball = graphics.Circle(pt, 25)
                ball.setOutline('blue')
                ball.setFill('blue')
                ball.draw(window)
            
            # Checks if target is hit
            x_diff = abs( ball.getCenter().x-target.getCenter().x)
            y_diff = abs( ball.getCenter().y-target.getCenter().y)
            
            if x_diff < miss_margin and y_diff < miss_margin:
                target.undraw()
                score += 1
                break
            
            time = perf_counter()-start
            utilities.writeData(file, time, teacher_tup, student_tup, difference_tup,
                         intensity, angle, score, 2)
            
    window.close()
    utilities.close([teacher, student, dongle])
    print('\nYour score is {}.'.format(score))
    
except KeyboardInterrupt:
    
    # For manual shutdown
    try:
        win.close()
        utilities.close([teacher, student, dong])
        print('\nYour score is {}.'.format(score))
        
    except NameError:
        # Will execute if setup not completed
        utilities.close([dongle])
        print('\nYour score is {}.'.format(score))