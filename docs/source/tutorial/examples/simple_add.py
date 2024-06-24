from cognixcore import (
    Node,
    PortConfig,
)

from numbers import Number

from cognixcore.config import NodeConfig

class NumberNode(Node):
    """This node outputs any kind of number"""
    
    title='Number'
    version='0.1'
    
    init_outputs = [
        PortConfig(label='num', allowed_data=Number)
    ]
    
    def __init__(self, flow, config = None):
        super().__init__(flow, config)
        self.number = 0
    
    def update_event(self, inp=-1):
        self.set_output(0, self.number)
        
class AddNode(Node):
    """
    This is a node that adds two numbers. The numbers can 
    be any type of number
    """
    
    title = 'Add'
    version = '0.1'
    
    init_inputs=[
        PortConfig(label='num1', allowed_data=Number),
        PortConfig(label='num2', allowed_data=Number)
    ]
    init_outputs=[
        PortConfig(label='out', allowed_data=Number)
    ]
    
    def __init__(self, flow, config = None):
        super().__init__(flow, config)
        self.result = 0
        
    def update_event(self, inp=-1):
        
        # Get the number of the current input
        num: Number = self.input(inp)
        if not num:
            num = 0
        
        # get the number on the other port
        other_port = 0 if inp==1 else 1
        other_num: Number = self.input(other_port)
        if not other_num:
            other_num = 0
        
        # add them and output
        self.result = num + other_num
        self.set_output(0, self.result)

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
num_one.number = 25

# second number node
num_two = flow.create_node(NumberNode)
num_two.number = 324.25

# add node
add_node = flow.create_node(AddNode)

flow.connect_nodes(num_one, 0, add_node, 1, silent=False)
flow.connect_nodes(num_two, 0, add_node, 1, silent=False)

print(add_node.result)