
<p align="center">
  <img src="./docs/img/logo.png" alt="drawing" width="70%"/>
</p>

A Python library for offline and streaming graph-based processing and evaluation, designed for modern flow-based/node-based scenarios. It is the driving force behind the CogniX project, but was designed with extensibility and modularity in mind. This library started as a fork of [ryvencore](https://github.com/leon-thomm/ryvencore), with additional functionality. Due to requirements that introduced breaking changes and deviation from the original source, the [fork](https://github.com/HeftyCoder/ryvencore/tree/cognix) was moved to a stand-alone repository.

### Installation

PyPi installation is in the works.

Install from sources - preferably after creating and activating a [python virtual environment](https://docs.python.org/3/library/venv.html): 
```
git clone https://github.com/leon-thomm/ryvencore
cd cognixcore
pip install .
```

### Usage

The API should be quite stable. However, if at some point the current design is deemed outdated or hinders any kind of major workflow, breaking changes will be introduced. For a guide on how to get started and what you can actually do, visit the [docs].

### Features

The main features include

- **load & save** from and into JSON
- **no immediate association** with any GUI library 
- **configurable nodes** through [Traits](https://docs.enthought.com/traits/) and automatic UI generation with [TraitsUI](https://docs.enthought.com/traitsui/) (both can be overriden or extended) 
- **flexible port connection type-checking** with Python's type hinting using [beartype](https://github.com/beartype/beartype)
- **fast BFS graph evaluation** with out of the box support for data streaming scenarios (i.e. Audio Processing, Brain Computer Interfaces, ...)
- **per flow variables system** that includes Python's primitive types but can be extended 
- **built-in logging** where each Node and Flow have their own loggers based on Python's [logging module](https://docs.python.org/3/library/logging.html)
- **actions system for nodes** for defining custom context-menus
- **RESTful API** with [FastAPI](https://fastapi.tiangolo.com) to enable third-party application interoperability

### A most simple example

**loading a project**

```python
import cognixcore as cc
import json
import sys

if __name__ == '__main__':
    # project file path
    fpath = sys.args[1]

    # read project file
    with open(fpath, 'r') as f:
        project: dict = json.loads(f.read())

    # run ryvencore
    session = cc.Session()
    session.load(project)

    # access the first flow
    f = session.flows[0]
    
    # and the last node that was created
    my_node = f.nodes[-1]

    # and execute it
    my_node.update()
```

### Licensing

cognixcore is licensed under the [LGPL License](https://github.com/CogniX-Up/cognixcore/blob/main/LICENSE).
