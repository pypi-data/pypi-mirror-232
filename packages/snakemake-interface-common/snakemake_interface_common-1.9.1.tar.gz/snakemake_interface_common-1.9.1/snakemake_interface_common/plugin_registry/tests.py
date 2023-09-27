from abc import ABC, abstractmethod
import argparse

from snakemake_interface_common.plugin_registry.plugin import PluginBase, SettingsBase
from snakemake_interface_common.plugin_registry import PluginRegistryBase


class TestRegistryBase(ABC):
    __test__ = False

    @abstractmethod
    def get_registry(self) -> PluginRegistryBase:
        ...

    @abstractmethod
    def get_test_plugin_name(self) -> str:
        ...

    @abstractmethod
    def validate_plugin(self, plugin: PluginBase):
        ...

    @abstractmethod
    def validate_settings(self, settings: SettingsBase, plugin: PluginBase):
        ...

    def test_registry_collect_plugins(self):
        registry = self.get_registry()
        assert (
            len(registry.plugins) == 1
        ), "we assume that only one plugin is installed in test environment"
        plugin = registry.get_plugin(self.get_test_plugin_name())
        self.validate_plugin(plugin)

    def test_registry_register_cli_args(self):
        registry = self.get_registry()
        parser = argparse.ArgumentParser()
        registry.register_cli_args(parser)
        prefix = registry.get_plugin(self.get_test_plugin_name()).cli_prefix
        for action in parser._actions:
            if not action.dest == "help":
                assert action.dest.startswith(prefix)

    def test_registry_cli_args_to_settings(self):
        registry = self.get_registry()

        parser = argparse.ArgumentParser()
        registry.register_cli_args(parser)
        args = parser.parse_args([])

        plugin = registry.get_plugin(self.get_test_plugin_name())
        settings = plugin.get_settings(args)

        self.validate_settings(settings, plugin)
