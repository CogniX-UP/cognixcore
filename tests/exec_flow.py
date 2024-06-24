import unittest
import cognixcore as rc

# THIS FAILS, won't be tested any time soon (2024)

class Node1(rc.Node):
    title = 'node 1'
    init_inputs = []
    init_outputs = [rc.PortConfig(type_='exec'), rc.PortConfig(type_='data')]

    def update_event(self, inp=-1):
        self.set_output(1, 'Hello, World!')
        self.exec_output(0)
        print('finished')


class Node2(rc.Node):
    title = 'node 2'
    init_inputs = [rc.PortConfig(type_='exec'), rc.PortConfig(type_='data')]
    init_outputs = []

    def __init__(self, params):
        super().__init__(params)

        self.data = None

    def update_event(self, inp=-1):
        self.data = self.input(1).payload
        print(f'received data on input {inp}: {self.input(inp)}')


class ExecFlowBasic(unittest.TestCase):

    def runTest(self):
        # rc.InfoMsgs.enable(True)
        s = rc.Session()
        s.register_node_types([Node1, Node2])
        f = s.create_flow('main')
        f.set_algorithm_mode('exec')

        n1 = f.create_node(Node1)
        n2 = f.create_node(Node2)
        n3 = f.create_node(Node2)
        n4 = f.create_node(Node2)

        f.connect_ports(n1._outputs[0], n2._inputs[0])
        f.connect_ports(n1._outputs[1], n2._inputs[1])
        f.connect_ports(n1._outputs[0], n3._inputs[0])
        f.connect_ports(n1._outputs[1], n4._inputs[1])

        self.assertEqual(n1._outputs[0].val, None)
        self.assertEqual(n1._outputs[1].val, None)

        n1.update()

        self.assertEqual(n1._outputs[0].val, None)
        self.assertEqual(n1._outputs[1].val, 'Hello, World!')

        self.assertEqual(n2.data, 'Hello, World!')
        self.assertEqual(n3.data, None)
        self.assertEqual(n4.data, None)


if __name__ == '__main__':
    unittest.main()
