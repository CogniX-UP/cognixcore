from __future__ import annotations
from typing import Self

from cognixcore import (
    Node,
    PortConfig,
    ProgressState,
)
from cognixcore.config.traits import *

from numbers import Number
from random import random
from cognixcore.config import NodeConfig

class NumberNode(Node):
    """This node outputs any kind of number"""
    
    title='Number'
    version='0.1'
    
    class Config(NodeTraitsConfig):
        mode: str = Enum('random', 'int', 'float', desc="mode for number generation")
        int_num = CX_Int(0, visible_when='mode=="int"', desc="int number")
        float_num = CX_Int(0.0, visible_when='mode=="float"', desc="float number")
        
        def number(self) -> Number:
            if self.mode == 'random':
                return random()
            elif self.mode == 'int':
                return self.int_num
            else:
                return self.float_num
    
    init_outputs = [
        PortConfig('num', allowed_data=Number)
    ]
    
    @property
    def config(self) -> Config:
        return self._config
        
    def update_event(self, inp=-1):
        self.progress = ProgressState(1, -1, "Outputing number")
        self.set_output(0, self.config.number())
        self.progress = None
        
class AddNode(Node):
    """
    This is a node that adds two numbers. The numbers can 
    be any type of number
    """
    
    title = 'Add'
    version = '0.1'
    
    class Config(NodeTraitsConfig):
        ports: PortList = Instance(
            PortList,
            lambda: PortList(
                    list_type = PortList.ListType.INPUTS,
                    inp_params = PortList.Params(
                        allowed_data=Number    
                    ),
                )
        )
        
        def set_ports(self, ports: list[str]):
            self.port.ports = ports
        
    init_outputs=[
        PortConfig(label='out', allowed_data=Number)
    ]
    
    def __init__(self, flow, config = None):
        super().__init__(flow, config)
        self.result = 0
    
    def init(self):
        self.first_res = True
    
    # it's better to redefine the config for intellisense purposes
    @property
    def config(self) -> Config:
        return self._config
    
    def update_event(self, inp=-1):
        
        prev_result = self.result
        
        self.result = 0
        for i in range(self.num_inputs):
            val = self.input(i)
            if not val:
                val = 0
            self.result += val
        if self.result != prev_result or self.first_res:
            self.first_res = False
            self.set_output(0, self.result)
            self.logger.info(f"Addition result: {self.result}")
        
from cognixcore import (
    Flow,
    Session
)

session = Session()
# Register the nodes
session.register_node_types([NumberNode, AddNode])

flow = session.create_flow(title='Example')

# First number node
num_one = flow.create_node(NumberNode)
num_one.config.mode = 'random'

# second number node
num_two = flow.create_node(NumberNode)
num_two.config.mode = 'int'
num_two.config.int_num = 25

# add node
add_node: AddNode = flow.create_node(AddNode)
# dynamically change the ports through the port list
add_node.config.set_ports(['port_one', 'port_two'])

flow.connect_nodes(num_one, 0, add_node, 1, silent=False)
flow.connect_nodes(num_two, 0, add_node, 1, silent=False)

print(add_node.result)

session.play_flow('Example')