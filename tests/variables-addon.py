import json
import unittest
import cognixcore as rc

from cognixcore.addons.variables._core import VarsAddon, Variable


class NodeBase(rc.Node):

    def __init__(self, params):
        super().__init__(params)

        self.Vars = self.session.addon(VarsAddon)

    def create_var1(self):
        if not self.Vars.var_exists(self.flow, 'var1'):
            self.Vars.create_var(self.flow, 'var1', 'Hello, World!')


class Node1(NodeBase):
    title = 'node 1'
    init_inputs = []
    init_outputs = [
        rc.PortConfig(),
        rc.PortConfig()
    ]

    def __init__(self, params):
        super().__init__(params)

        self.var_val = None

    def subscribe_to_var1(self):
        self.Vars.subscribe(self, 'var1', self.on_var1_changed)
        self.var_val = self.Vars.var(self.flow, 'var1').value

    def update_event(self, inp=-1):
        self.set_output(0, 'Hello, World!')
        self.set_output(1, 42)

    def on_var1_changed(self, var: Variable):
        self.var_val = var.value
        print('var1 changed in slot:', self.var_val)
        self.update()


class Node2(NodeBase):
    title = 'node 2'
    init_inputs = [rc.PortConfig()]
    init_outputs = []

    def update_event(self, inp=-1):
        pass

    def update_var1(self, val):
        self.Vars.var(self.flow, 'var1').value = val
        print('var1 successfully updated:', val)


class VariablesBasic(unittest.TestCase):

    def runTest(self):
        s = rc.Session(load_addons=True)
        s.register_node_types([Node1, Node2])

        f = s.create_flow('main')

        n1 = f.create_node(Node1)
        n2 = f.create_node(Node2)
        n3 = f.create_node(Node2)
        n4 = f.create_node(Node2)

        f.connect_ports(n1._outputs[0], n2._inputs[0])
        f.connect_ports(n1._outputs[1], n3._inputs[0])
        f.connect_ports(n1._outputs[1], n4._inputs[0])

        n1.create_var1()

        n1.update()

        self.assertEqual(n1._outputs[0].val, 'Hello, World!')
        self.assertEqual(n1._outputs[1].val, 42)
        self.assertEqual(n3.input(0), n4.input(0))

        # test variables addon

        n1.subscribe_to_var1()
        n2.update_var1("Jesus")
        assert n1.var_val == "Jesus"
        
        print('----------------------------------------------------------')

        # test save and load

        var = n1.Vars.var(f, 'var1')
        project = s.serialize()
        del s

        s2 = rc.Session(load_addons=True)
        s2.register_node_types([Node1, Node2])
        s2.load(project)

        vars = s2.addon(VarsAddon)

        f2 = s2.flows['main']
        self.assertEqual(vars.var(f2, 'var1').value, "Jesus")

        n1_2, n2_2, n3_2, n4_2 = f2.nodes
        n1_2.update()
        n2_2.update_var1('test')
        
        self.assertEqual(n1_2.var_val, 'test')

        n1_2.update()
        n2_2.update_var1('bro')

        self.assertEqual(n1_2.var_val, 'bro')


if __name__ == '__main__':
    unittest.main()
