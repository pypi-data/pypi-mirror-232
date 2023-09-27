__author__ = "Johannes Köster"
__copyright__ = "Copyright 2022, Johannes Köster, Vanessa Sochat"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import field, fields
from dataclasses import MISSING, dataclass
from typing import Dict, Optional, Type, Union
import copy
from snakemake_interface_common.exceptions import WorkflowError

from snakemake_interface_common.exceptions import InvalidPluginException
from snakemake_interface_common._common import (
    dataclass_field_to_argument_args,
)

# Valid Argument types (to distinguish from empty dataclasses)
ArgTypes = (str, int, float, bool, list)


@dataclass
class SettingsBase:
    """Base class for plugin settings."""

    def get_items_by_category(self, category: str):
        """Yield all items (name, value) of the given group (as defined by the)
        optional category field in the metadata.
        """
        for thefield in fields(self.__class__):
            if thefield.metadata.get("subgroup") == category:
                yield thefield.name, getattr(self, thefield.name)


@dataclass
class TaggedSettings:
    _inner: Dict[str, SettingsBase] = field(default_factory=dict)
    _plugin_name: str

    def register_settings(self, settings: SettingsBase, tag: Optional[str] = None):
        self._inner[tag] = settings

    def get_settings(self, tag: Optional[str] = None) -> SettingsBase:
        try:
            return self._inner[tag]
        except KeyError:
            if tag is not None:
                msg = (
                    f"No settings available for the plugin {self.plugin_name} with "
                    "tag {tag}."
                )
            else:
                msg = (
                    "No untagged settings available for the plugin {self.plugin_name}."
                )
            raise WorkflowError(msg)


class PluginBase(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def cli_prefix(self) -> str:
        ...

    @property
    @abstractmethod
    def settings_cls(self) -> Type[SettingsBase]:
        ...

    @property
    def support_tagged_values(self) -> bool:
        return False

    def has_settings_cls(self):
        """Determine if a plugin defines custom executor settings"""
        return self.settings_cls is not None

    def register_cli_args(self, argparser):
        """Add arguments derived from self.executor_settings to given
        argparser."""

        # Cut out early if we don't have custom parameters to add
        if not self.has_settings_cls():
            return

        # Convenience handle
        params = self.settings_cls

        # Assemble a new dataclass with the same fields, but with prefix
        # fields are stored at dc.__dataclass_fields__
        dc = copy.deepcopy(params)
        for thefield in fields(params):
            if "help" not in thefield.metadata:
                raise InvalidPluginException(
                    "Fields of ExecutorSettings must have a help string."
                )
            if thefield.default is MISSING and thefield.default_factory is MISSING:
                raise InvalidPluginException(
                    "Fields of ExecutorSettings must have a default value."
                )

            # Executor plugin dataclass members get prefixed with their
            # name when passed into snakemake args.
            prefixed_name = self._get_prefixed_name(thefield.name)

            # Since we use the helper function below, we
            # need a new dataclass that has these prefixes
            del dc.__dataclass_fields__[thefield.name]
            thefield.name = prefixed_name
            dc.__dataclass_fields__[thefield.name] = thefield

        settings = argparser.add_argument_group(f"{self.name} executor settings")

        for thefield in fields(dc):
            args, kwargs = dataclass_field_to_argument_args(thefield)

            if thefield.metadata.get("env_var"):
                kwargs["env_var"] = f"SNAKEMAKE_{prefixed_name.upper()}"

            if self.support_tagged_values:
                if thefield.metadata.get("nargs", None) is not None:
                    raise ValueError(
                        f"Plugin {self.name} supports tagged values but specifies args "
                        "with multiple values in its settings class. This is not "
                        "supported and a bug in the plugin. Please file an issue in "
                        "the plugin repository."
                    )
                kwargs["nargs"] = "+"

            settings.add_argument(*args, **kwargs)

    def get_settings(self, args) -> Union[SettingsBase, TaggedSettings]:
        """Return an instance of self.executor_settings with values from args.

        This helper function will select executor plugin namespaces arguments
        for a dataclass. It allows us to pass them from the custom executor ->
        custom argument parser -> back into dataclass -> snakemake.
        """
        if not self.has_settings_cls():
            return SettingsBase()

        # We will parse the args from snakemake back into the dataclass
        dc = self.settings_cls

        def get_name_and_value(field):
            # This is the actual field name without the prefix
            name = field.name.replace(f"{self.name}_", "", 1)
            value = getattr(args, field.name, None)
            return name, value

        kwargs_tagged = defaultdict(dict)
        kwargs_all = dict()
        required_args = set()
        field_names = dict()

        # These fields will have the executor prefix
        for thefield in fields(dc):
            name, value = get_name_and_value(thefield)
            field_names[name] = thefield.name
            if thefield.metadata.get("required"):
                required_args.add(name)

            def extract_values(value, thefield, name, tag=None):
                # This will only add instantiated values, and
                # skip over dataclasses._MISSING_TYPE and similar
                if isinstance(value, ArgTypes):
                    # If a parsing function is defined, we pass the arg value to it
                    # in order to get the correct type back.
                    parse_func = thefield.metadata.get("parse_func")
                    if parse_func is not None:
                        value = parse_func(value)
                    if tag is None:
                        kwargs_all[name] = value
                    else:
                        kwargs_tagged[tag][name] = value

            if self.support_tagged_values:
                for item in value:
                    splitted = item.split(":", 1)
                    if len(splitted) == 2:  # is tagged
                        tag, item = splitted
                    elif len(splitted) == 1:  # not tagged
                        tag = None
                    extract_values(item, thefield, name, tag=tag)
            else:
                extract_values(item, thefield, name)

        for kwargs in kwargs_tagged.values():
            for key, default_value in kwargs_all.items():
                if key not in kwargs:
                    kwargs[key] = default_value

        def check_required(kwargs, tag=None):
            missing = required_args - kwargs.keys()
            if missing:

                cli_args = [self._get_cli_arg(field_names[name]) for name in missing]
                tag_phrase = f" with tag {tag}" if tag is not None else ""
                raise WorkflowError(
                    f"The following required arguments are missing for "
                    f"plugin {self.name}{tag_phrase}: {', '.join(cli_args)}."
                )

        # convert into the dataclass
        if self.support_tagged_values:
            tagged_settings = TaggedSettings()
            for tag, kwargs in kwargs_tagged.items():
                check_required(kwargs, tag=tag)
                tagged_settings.register_settings(dc(**kwargs), tag=tag)
            try:
                check_required(kwargs)
                tagged_settings.register_settings(dc(kwargs_all))
            except WorkflowError:
                # if untagged settings are not complete, do not register them
                pass
            return tagged_settings
        else:
            check_required(kwargs)
            return dc(**kwargs)

    def _get_cli_arg(self, field_name: str) -> str:
        return self._get_prefixed_name(field_name).replace("_", "-")

    def _get_prefixed_name(self, field_name: str) -> str:
        return f"{self.cli_prefix}_{field_name}"
