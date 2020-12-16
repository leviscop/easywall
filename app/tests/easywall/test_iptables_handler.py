"""TODO: Doku."""
from tests import unittest
from tests.utils import prepare_configuration, restore_configuration

from easywall.__main__ import CONFIG_PATH
from easywall.config import Config
from easywall.iptables_handler import Chain, Iptables, PolicyTarget


class TestIPTablesHandler(unittest.TestCase):
    """TODO: Doku."""

    def setUp(self) -> None:
        """TODO: Doku."""
        prepare_configuration()
        self.config = Config(CONFIG_PATH)
        self.iptables = Iptables(self.config)

    def tearDown(self) -> None:
        """TODO: Doku."""
        self.iptables.reset()
        restore_configuration()

    def test_policy(self) -> None:
        """TODO: Doku."""
        self.iptables.add_policy(Chain.FORWARD, PolicyTarget.ACCEPT)

    def test_chain(self) -> None:
        """TODO: Doku."""
        self.iptables.add_chain(Chain.PORTSCAN.value)
        self.iptables.delete_chain(Chain.PORTSCAN.value)

    def test_append(self) -> None:
        """TODO: Doku."""
        self.iptables.add_chain(Chain.PORTSCAN)
        self.iptables.add_append(Chain.PORTSCAN, "-i lo -j ACCEPT")
        self.iptables.flush_chain(Chain.PORTSCAN)

    def test_status(self) -> None:
        """TODO: Doku."""
        self.iptables.status()

    def test_save(self) -> None:
        """TODO: Doku."""
        self.iptables.save()

    def test_restore(self) -> None:
        """TODO: Doku."""
        self.iptables.restore()
