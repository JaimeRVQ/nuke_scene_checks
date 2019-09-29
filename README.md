# Nuke scene checks (node system)

Node-based editor that lets the user run different checks through the scene, configure multiple outputs for it on the fly and render them. Due to the way the these nodes are configured, this editor lets the user render one Nuke node to multiple locations, also with different frameranges and extensions.

### Types of nodes available

#### Writing nodes
At least one of each necessary to build the output for the scene.

| Node | Information held |
| ------ | :------: |
| Origin | Node to be rendered |
| Filepath | Target directory |
| Comment | User comment for the rendered files |
| Frame start | Frame to start the rendering at |
| Frame end | Frame to end the rendering at |
| Extension | Extension for the output files |

#### Additional information nodes
These nodes are not necessary for writing, but can be used to add extra information to the output.

| Node | Information held |
| ------ | :------: |
| Version | Version number of the output to be rendered |
| Padding | Padding of frames in the output |


#### Check nodes
Perform checks on the scene before rendering the output.

| Node | Checks run |
| ------ | :------: |
| Errors | Looks for standard errors inside all nodes |
| Regex naming | Makes sure that no node name matches the given RegEx |
| Disconnected Reads | Lists all Read nodes with no connected output |
| Class filter | Makes sure that there are no nodes of the specified class |

#### Manipulation nodes
Perform basic manipulations to the output of the scene before rendering it.
They are applied separately for each stream.

| Node | Modifications performed |
| ------ | :------: |
| Desaturation | Desaturates the image |
| Flip | Flips the image horizontally |


### Recommended way to launch
Install the module to your desired location and run:
```
from nuke_scene_checks import scene_checks_widget
sc = scene_checks_widget.SceneChecks()
```

### Look of the widget
![network](https://user-images.githubusercontent.com/43014805/65394206-0c6a5a80-dd8b-11e9-878b-f3130d401133.jpg)

This module has been tested successfully in **Nuke 11.1v1**
***

For more info: www.jaimervq.com