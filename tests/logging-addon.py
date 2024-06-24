import unittest
import cognixcore as rc
from utils import check_addon_available

check_addon_available('Logging', __file__)

from cognixcore.addons.logging import LoggingAddon


class NodeBase(rc.Node):

    def __init__(self, params):
        super().__init__(params)

        self.Logging: LoggingAddon = self.get_addon(LoggingAddon.addon_name())


class Node1(NodeBase):
    title = 'node 1'
    init_inputs = []
    init_outputs = [rc.PortConfig(type_='data'), rc.PortConfig(type_='data')]

    def __init__(self, params):
        super().__init__(params)

        self.log1 = self.Logging.new_logger(self, 'log1')
        self.log2 = self.Logging.new_logger(self, 'log2')

    def update_event(self, inp=-1):
        self.set_output(0, 'Hello, World!')
        self.set_output(1, 42)
        print('finished')


class Node2(NodeBase):
    title = 'node 2'
    init_inputs = [rc.PortConfig()]
    init_outputs = []

    def update_event(self, inp=-1):
        print(f'received data on input {inp}: {self.input(inp)}')


class DataFlowBasic(unittest.TestCase):

    def runTest(self):
        s = rc.Session(load_addons=True)
        s.register_node_types([Node1, Node2])

        f = s.create_flow('main')

        # TODO: logging tests


if __name__ == '__main__':
    unittest.main()
