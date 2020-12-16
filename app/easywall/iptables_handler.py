"""TODO: Doku."""
from enum import Enum
from logging import debug, info, error

from easywall.config import Config
from easywall.utility import (create_file_if_not_exists,
                              create_folder_if_not_exists,
                              delete_file_if_exists, execute_os_command,
                              file_get_contents)


class PolicyTarget(Enum):
    """iptables's available targets for policies."""
    ACCEPT = "ACCEPT"
    DROP = "DROP"


class Target(Enum):
    """iptables's default targets."""
    ACCEPT = "ACCEPT"
    DROP = "DROP"
    QUEUE = "QUEUE"
    RETURN = "RETURN"
    LOG = "LOG"
    REJECT = "REJECT"
    MASQUERADE = "MASQUERADE"
    MARK = "MARK"


class Chain(Enum):
    """iptables's default and custom chains provided by easywall"""
    INPUT = "INPUT"
    FORWARD = "FORWARD"
    OUTPUT = "OUTPUT"
    PREROUTING = "PREROUTING"
    POSTROUTING = "PREROUTING"
    SSHBRUTE = "SSHBRUTE"
    INVALIDDROP = "INVALIDDROP"
    PORTSCAN = "PORTSCAN"
    ICMPFLOOD = "ICMPFLOOD"


class Table(Enum):
    """iptables's tables."""
    FILTER = "filter"
    NAT = "nat"
    MANGLE = "mangle"
    RAW = "raw"
    SECURITY = "security"


class Iptables:
    """TODO: Doku."""

    def __init__(self, cfg: Config) -> None:
        """TODO: Doku."""
        self.cfg = cfg

        self.iptables_bin = self.cfg.get_value("EXEC", "iptables")
        self.iptables_bin_save = self.cfg.get_value("EXEC", "iptables-save")
        self.iptables_bin_restore = self.cfg.get_value("EXEC", "iptables-restore")

        self.ip6tables_bin = self.cfg.get_value("EXEC", "ip6tables")
        self.ip6tables_bin_save = self.cfg.get_value("EXEC", "ip6tables-save")
        self.ip6tables_bin_restore = self.cfg.get_value("EXEC", "ip6tables-restore")

        self.ipv6 = self.cfg.get_value("IPV6", "enabled")
        if self.ipv6 is True:
            debug("IPV6 is enabled")

        self.backup_path = "backup"
        self.backup_file_ipv4 = "iptables_v4_backup"
        self.backup_file_ipv6 = "iptables_v6_backup"

    def add_policy(self, chain: Chain, target: PolicyTarget) -> None:
        """Create a new policy in iptables firewall by using the os command."""
        option = "-P"
        execute_os_command("{} {} {} {}".format(
            self.iptables_bin, option, chain.value, target.value))
        if self.ipv6 is True:
            execute_os_command("{} {} {} {}".format(
                self.ip6tables_bin, option, chain.value, target.value))

        info("iptables policy added for chain {} and target {}".format(chain.value, target.value))

    def add_chain(self, chain: Chain) -> None:
        """Create a new custom chain in iptables."""
        option = "-N"

        execute_os_command("{} {} {}".format(self.iptables_bin, option, chain.value))
        if self.ipv6 is True:
            execute_os_command("{} {} {}".format(self.ip6tables_bin, option, chain.value))

        info("iptables chain {} added".format(chain.value))

    def add_append(self, chain: Chain, rule: str,
                   onlyv6: bool = False, onlyv4: bool = False, table: Table = Table.FILTER) -> None:
        """Create a new append in iptables."""
        table_value = table.value
        option = "-A"

        if table_value != "":
            if not table_value.startswith("-t"):
                table_value = "-t " + table_value

        if onlyv4 is True or (onlyv6 is False and onlyv4 is False):
            execute_os_command("{} {} {} {} {}".format(
                self.iptables_bin, table_value, option, chain.value, rule))
            info("append for ipv4: table: {}, chain: {}, rule: {} added".format(
                table_value, chain.value, rule))

        if self.ipv6 is True and (onlyv6 is True or (onlyv6 is False and onlyv4 is False)):
            execute_os_command("{} {} {} {} {}".format(
                self.ip6tables_bin, table_value, option, chain.value, rule))
            info("append for ipv6: table: {}, chain: {}, rule: {} added".format(
                table_value, chain.value, rule))

    def insert(self, chain: Chain, rule: str,
               onlyv6: bool = False, onlyv4: bool = False, table: Table = Table.FILTER) -> None:
        """TODO: Doku."""
        table_value = table.value
        option = "-I"

        if table_value != "":
            if not table_value.startswith("-t"):
                table_value = "-t " + table_value

        if onlyv4 is True or (onlyv6 is False and onlyv4 is False):
            execute_os_command("{} {} {} {} {}".format(
                self.iptables_bin, table_value, option, chain.value, rule))
            info("insert for ipv4, table: {}, chain: {}, rule: {} added".format(
                table_value, chain.value, rule))

        if self.ipv6 is True and (onlyv6 is True or (onlyv6 is False and onlyv4 is False)):
            execute_os_command("{} {} {} {} {}".format(
                self.ip6tables_bin, table_value, option, chain.value, rule))
            info("insert for ipv6, table: {}, chain: {}, rule: {} added".format(
                table_value, chain.value, rule))

    def add_custom(self, rule: str) -> None:
        """TODO: Doku."""
        execute_os_command("{} {}".format(self.iptables_bin, rule))
        if self.ipv6 is True:
            execute_os_command("{} {}".format(self.ip6tables_bin, rule))

        info("iptables custom rule added: {}".format(rule))

    def flush_all_chains(self) -> None:
        # Flush all chains but keep Docker chains and rules
        for table in Table:
            for chain in Chain:
                self.flush_chain(table.name, chain.name)

    def flush_chain(self, table: Table, chain: Chain) -> None:
        table_str = table.value
        chain_str = chain.value
        # Flush but keep Docker rules
        cmd = execute_os_command(f"{self.iptables_bin} -t {table_str} -L {chain_str} | tail -n+3")
        if not cmd.successful:
            return
        # All iptables rules end with \n, so we split. Last element would be '', so we also remove it.
        rules = cmd.output.split("\n", )[:-1]
        deleted_rules = 0
        rule_number = 0
        for rule in rules:
            if "DOCKER" not in rule:
                rule_id = rule_number - deleted_rules
                cmd = execute_os_command(f"{self.iptables_bin} -t {table_str} -D {chain_str} {rule_id}")
                if cmd.successful:
                    deleted_rules += 1
            rule_number += 1

    def delete_all_chains(self) -> None:
        # Delete all user chains but keep Docker's ones
        for chain in Chain:
            self.delete_chain(chain.name)

    def delete_chain(self, chain: Chain = Chain.INPUT) -> None:
        """Delete a chain or all chains in iptables firewall."""
        info("removing iptables rules...")
        self.delete_chain(chain.value, self.iptables_bin)
        if self.ipv6 is True:
            info("removing ip6tables rules...")
            self.__delete_chain(chain.value, self.ip6tables_bin)

    def __delete_chain(self, chain: str, iptables_bin: str) -> None:
        cmd = execute_os_command(f"{iptables_bin} -X {chain}")
        if cmd.successful:
            if chain != "":
                info(f"iptables chain {chain} deleted")
            else:
                info("all iptables chains deleted")
        else:
            if chain != "":
                details = f"code: {cmd.code} | Err: {cmd.err}"
                error(f"iptables chain {chain} could not be deleted.", details)
            else:
                details = f"code: {cmd.code} | Err: {cmd.err}"
                info("iptables chains could not be deleted.", details)

    def reset(self) -> None:
        """Reset iptables and allows all connections to the system and from the system."""
        self.add_policy(Chain.INPUT, PolicyTarget.ACCEPT)
        self.add_policy(Chain.OUTPUT, PolicyTarget.ACCEPT)
        self.add_policy(Chain.FORWARD, PolicyTarget.ACCEPT)
        self.flush_all_chains()
        self.delete_all_chains()

        info("incoming and outgoing connections have been opened and chains have been deleted")

    def status(self) -> str:
        """List the iptables configuration as string.

        [WARNING] this is not machine readable!
        """
        tmpfile = ".iptables_list"
        execute_os_command("{} -L > {}".format(self.iptables_bin, tmpfile))
        content = file_get_contents(tmpfile)
        delete_file_if_exists(tmpfile)
        return content

    def save(self) -> None:
        """Save the current iptables state into a file."""
        create_folder_if_not_exists(self.backup_path)

        create_file_if_not_exists("{}/{}".format(self.backup_path, self.backup_file_ipv4))
        execute_os_command("{} >> {}/{}".format(self.iptables_bin_save,
                                                self.backup_path, self.backup_file_ipv4))
        debug("backup for ipv4 rules created")

        if self.ipv6 is True:
            create_file_if_not_exists("{}/{}".format(self.backup_path, self.backup_file_ipv6))
            execute_os_command("{} >> {}/{}".format(self.ip6tables_bin_save,
                                                    self.backup_path, self.backup_file_ipv6))
            debug("backup of ipv6 rules created")

        info("backup of iptables configuration created")

    def restore(self) -> None:
        """Restore a backup of a previously saved backup."""
        create_folder_if_not_exists(self.backup_path)

        execute_os_command("{} < {}/{}".format(self.iptables_bin_restore,
                                               self.backup_path, self.backup_file_ipv4))
        debug("ipv4 rules restored")

        if self.ipv6 is True:
            execute_os_command("{} < {}/{}".format(self.ip6tables_bin_restore,
                                                   self.backup_path, self.backup_file_ipv6))
            debug("ipv6 rules restored")

        info("restores iptables state from previous created backup")
