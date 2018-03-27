choose_adaptive_words
===========================

This package contains a set of nodes that are used to get user handwriting input and adapt the next word to the skills of the user

Tested with ROS Indigo.

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


Provided nodes:
---------------
- `????.py`: the main node ????

- `some_other_node??.py`: provides services etc.


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

