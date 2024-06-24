import json
import unittest
import cognixcore as rc
from collections.abc import Sequence

class NodeBase(rc.Node):
    pass


class Node1(NodeBase):
    title = 'node 1'
    init_inputs = []
    init_outputs = [
        rc.PortConfig(allowed_data=list), 
        rc.PortConfig(allowed_data=int), 
        rc.PortConfig()
    ]

class Node2(NodeBase):
    title = 'node 2'
    init_inputs = [
        rc.PortConfig(default='default value'), 
        rc.PortConfig(allowed_data=Sequence | int)
    ]
    init_outputs = []


class DataFlowBasic(unittest.TestCase):

    def runTest(self):
        s = rc.Session()
        s.register_node_types([Node1, Node2])

        f = s.create_flow('main')

        n1 = f.create_node(Node1)
        n2 = f.create_node(Node2)

        assert f.connect_ports(n1._outputs[0], n2._inputs[1]) != None
        f.disconnect_ports(n1._outputs[0], n2._inputs[1])
        assert f.connect_ports(n1._outputs[1], n2._inputs[1]) != None
        f.disconnect_ports(n1._outputs[1], n2._inputs[1])
        assert f.connect_ports(n1._outputs[2], n2._inputs[1]) == None

if __name__ == '__main__':
    unittest.main()