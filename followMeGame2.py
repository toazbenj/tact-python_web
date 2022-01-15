# -*- coding: utf-8 -*-
"""
Tandem Follow Me Game

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
            Close sensors
            Display Score
    
Reference: http://anh.cs.luc.edu/handsonPythonTutorial/graphics.html

Created on Thu Dec 23 08:19:17 2021
@author: Ben Toaz
"""

import graphics as g
import sensorVestMethods as sv
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
    win = g.GraphWin(width = x_bounds, height = y_bounds)
    
    # Register and Tare Sensors
    teacher, student, dong = sv.getDevices()
    
    # Register haptic files
    sv.register(3)
    
    # Make Ball
    pt = g.Point(x_bounds/2, y_bounds/2)
    
    ball = g.Circle(pt, 25)
    ball.setOutline('blue')
    ball.setFill('blue')
    ball.draw(win)
    
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
        
        pt = g.Point(x_coord,y_coord)
        target = g.Circle(pt,30)
        target.setOutline('red')
        target.draw(win)        
        
        # Movement Loop
        while True:    
            
            # Get position data
            tec_tup = teacher.getStreamingBatch()
            stu_tup = student.getStreamingBatch()
            diff_tup = diff_tup = (stu_tup[0]-tec_tup[0], 
                                   stu_tup[1]-tec_tup[1],
                                   stu_tup[2]-tec_tup[2])
            
            # Select haptics direction
            index = sv.getIndex(diff_tup,tolerance)
            
            # Play haptics, return values for recording
            angle, intensity, commandTime = sv.advancedPlay(index, diff_tup,
                                                            start, commandTime)
            
            # Convert sensor angle movement to ball movement
            if sv.checkTolerance(tec_tup,tolerance) and\
                sv.checkTolerance(stu_tup,tolerance):
                    
                x = (tec_tup[1]+stu_tup[1]) / (2*pi/4) * 10
                y = (tec_tup[2]+stu_tup[2]) / (2*pi/4) * 10                
            else:
                x = 0 
                y = 0
            
            # print('{}, {}'.format(round(pt.x,3),round(pt.y,3)))
            
            # If speed limit exceeded, sets speed to limit in same direction
            if abs(x) > speed_limit:
                x = speed_limit * x/x
            if abs(y) > speed_limit:
                y = speed_limit * y/y
            
            ball.move(-x,-y)
            
            # Respawns ball in center of window if out of bounds
            if ball.getCenter().x > x_bounds or ball.getCenter().y > y_bounds\
                or ball.getCenter().x < 0 or ball.getCenter().y < 0:
                
                pt.undraw()
                ball.undraw()
                
                pt = g.Point(x_bounds/2, y_bounds/2)
                ball = g.Circle(pt, 25)
                ball.setOutline('blue')
                ball.setFill('blue')
                ball.draw(win)
            
            # Checks if target is hit
            x_diff = abs( ball.getCenter().x-target.getCenter().x)
            y_diff = abs( ball.getCenter().y-target.getCenter().y)
            
            if x_diff < miss_margin and y_diff < miss_margin:
                target.undraw()
                score += 1
                break
            
            time = perf_counter()-start
            sv.writeData(file, time, tec_tup, stu_tup, diff_tup, intensity, 
                         angle, score,2)
            
    win.close()
    sv.close([teacher, student, dong])
    print('\nYour score is {}.'.format(score))
    
except KeyboardInterrupt:
    
    # For manual shutdown
    try:
        win.close()
        sv.close([teacher, student, dong])
        print('\nYour score is {}.'.format(score))
        
    except NameError:
        # Will execute if setup not completed
        sv.close([dong])
        print('\nYour score is {}.'.format(score))
