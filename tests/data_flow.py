import json
import unittest
import cognixcore as rc


class NodeBase(rc.Node):
    pass


class Node1(NodeBase):
    title = 'node 1'
    init_inputs = []
    init_outputs = [rc.PortConfig(type_='data'), rc.PortConfig(type_='data')]

    def update_event(self, inp=-1):
        self.set_output(0, 'Hello, World!')
        self.set_output(1, 42)
        print('finished')


class Node2(NodeBase):
    title = 'node 2'
    init_inputs = [rc.PortConfig(default='default value')]
    init_outputs = []

    def update_event(self, inp=-1):
        print(f'received data on input {inp}: {self.input(inp)}')


class DataFlowBasic(unittest.TestCase):

    def runTest(self):
        s = rc.Session()
        s.register_node_types([Node1, Node2])

        f = s.create_flow('main')

        n1 = f.create_node(Node1)
        n2 = f.create_node(Node2)
        n3 = f.create_node(Node2)
        n4 = f.create_node(Node2)

        n2.update()

        f.connect_ports(n1._outputs[0], n2._inputs[0])
        f.connect_ports(n1._outputs[1], n3._inputs[0])
        f.connect_ports(n1._outputs[1], n4._inputs[0])

        # test data model

        self.assertEqual(n1._outputs[0].val, None)
        self.assertEqual(n1._outputs[1].val, None)

        n1.update()

        self.assertEqual(n1._outputs[0].val, 'Hello, World!')
        self.assertEqual(n1._outputs[1].val, 42)
        self.assertEqual(n3.input(0), n4.input(0))

        # test save and load

        project = s.serialize()
        print(json.dumps(project, indent=4))
        del s

        s2 = rc.Session()
        s2.register_node_types([Node1, Node2])
        s2.load(project)
        f2 = s2.flows['main']

        n1_2, n2_2, n3_2, n4_2 = f2.nodes

        n1_2.update()
        
        assert n2_2.input(0) == 'Hello, World!'
        assert n3_2.input(0) == 42
        assert n4_2.input(0) == 42



if __name__ == '__main__':
    unittest.main()
