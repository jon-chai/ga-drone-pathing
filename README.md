# drone-pathing-ga

Drone Pathing GA is a Python & Processing module that creates a simulation of drones that learn how to steer using genetic algorithms.

## Installation

Download Processing [here](https://processing.org/download/).

After downloading, [enable Python mode](https://py.processing.org/tutorials/gettingstarted/).

Next, click File -> Open and navigate to Drone_GA -> Drone_GA.pyde that you've downloaded from github.

The simulation should now be runnable: simply click the play button on the top left corner.

## Usage

The simulation automatically begins in training mode.

### Hotkeys

`[mouse click] -> toggle debug mode`

`[mouse drag] -> draw obstacle at target location` WARNING: May cause massive lag and sporadic behavior.

`s -> save the best drone from all generations that have been trained in the current simulation to the file results.txt`

`t -> switch from training mode to individual testing mode, or from individual testing mode to group testing mode.` Note that the first drone that is tested will always be the manually created "human drone". Subsequent drones will be in reverse order, the newer (later generations) drones first.

`g -> generate a new test world`

`q -> quit the simulation`

### Modifiability
Most of the modifiable parameters exist within the `setup` function. Play around with them and see what you can do! For any clarification, feel free to send us a message and we will be happy to assist.

## License
[MIT](https://choosealicense.com/licenses/mit/)
