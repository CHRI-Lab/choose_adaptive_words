choose_adaptive_words
===========================

This package contains a set of nodes that are used to get user handwriting input and adapt the next word to the skills of the user

Tested with ROS Indigo on Ubuntu 16.04 (LTS)

Install & Compile:
---------------
```
$ cd ~/catkin_ws/src/
$ git clone  https://github.com/chili-epfl/choose_adaptive_words.git
$ cd ../
$ catkin_make
```


Requierments:
---------------
See CoWriter project requirements

Provided functionalities:
---------------
In `./nodes` run `python activity.py`to launch the writing app. 
The main node that opens two windows, one for writing the other one to manage the parameters

![](/home/wafa/catkin_ws/src/choose_adaptive_words/p1.png)


- Change the Simple Learning Pace (0,100)
- TODO : use PCA
- TODO : use CNN
- TODO: use adapt thibolt

Letters dataset configuration
-----------------------------

The launch argument `choose_adaptive_words`

For instance, for a specific experiment, this way:

```
$ roslaunch choose_adaptive_words [...other options]

```


TODO
-----
- Remove Federer Button (be able to change to adaptive mode or regular mode with a threshold we could set
- Clean screen just after the we send a new word
- Make a "real" eraser, select the zones to clean
- makenao look at tablet 
- check arms
- make the path of the robot editable by the kid

