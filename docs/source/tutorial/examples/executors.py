from cognixcore import (
    Session,
    FlowAlg,
)

session = Session()
flow = session.create_flow("Example Flow")
flow.algorithm_mode = FlowAlg.DATA_OPT

# This will manually set it to a ManualFlow executor
session.play_flow("Example Flow")
from simple_add import AddNode

from cognixcore import (
    Session,
    Node,
    FrameNode,
    PortConfig
)
from random import random
from numbers import Number

class NumberGeneratorNode(FrameNode):
    """Generates a number"""
    
    title='Number Generator'
    version='v0.1'
    
    init_outputs = [
        PortConfig(label='num', allowed_data=Number)
    ]
    
    def __init__(self, flow):
        super().__init__(flow)
        self.scale = 2
    
    def frame_update(self):
        num = self.scale * random()
        self.set_output(0, num)
    
session = Session()
session.register_node_types([NumberGeneratorNode, AddNode])

flow = session.create_flow('Random Number Generation')
rnd_node = flow.create_node(NumberGeneratorNode)
add_node = flow.create_node(AddNode)

flow.connect_nodes(rnd_node, 0, add_node, 0)

session.play_flow(
    'Random Number Generation',
    on_other_thread=True,
)
