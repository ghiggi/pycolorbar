# -----------------------------------------------------------------------------.
# MIT License

# Copyright (c) 2024 pycolorbar developers
#
# This file is part of pycolorbar.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# -----------------------------------------------------------------------------.
"""Define the register of univiariate colorbars."""

import os

from pycolorbar.settings.colorbar_io import read_cbar_dicts, write_cbar_dicts
from pycolorbar.settings.colorbar_validator import validate_cbar_dict
from pycolorbar.settings.utils import get_auxiliary_categories
from pycolorbar.utils.yaml import list_yaml_files


class ColorbarRegistry:
    """
    A singleton class to manage colorbar registrations.

    This class provides methods to register colorbars settings, add new one on-the-fly,
    and to remove them.

    Attributes
    ----------
    _instance : ColorbarRegistry
        The singleton instance of the ColorbarRegistry.
    registry : dict
        The dictionary holding the registered colorbar settings.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            #  cls._instance = super(ColorbarRegistry, cls).__new__(cls)
            cls._instance.registry = {}
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls()  # this will call __new__
        return cls._instance

    def reset(self):
        """Clears the entire Colorbar registry."""
        self.registry.clear()

    @property
    def names(self):
        """List the names of all registered colorbars settings."""
        return sorted(list(self.registry))

    def available(self, category=None, exclude_referenced=False):
        """List the name of available colorbars for a specific category."""
        if exclude_referenced:
            names = self.get_standalone_settings()
        else:
            names = self.names

        if category is None:
            return names

        # Subset names by category
        cat_names = []
        for name in names:
            cbar_dict = self.get_cbar_dict(name, resolve_reference=True)
            categories = get_auxiliary_categories(cbar_dict)
            categories = [cat.upper() for cat in categories]
            if category.upper() in categories:
                cat_names.append(name)
        return cat_names

    def register(self, filepath: str, verbose: bool = True, force: bool = True):
        """
        Register colorbar(s) configuration(s) defined in a YAML file.

        Parameters
        ----------
        filepath : str
            The YAML file path where the colorbar(s) settings are specified.
            A single YAML file can contain the configuration of multiple colorbars !
            The name of the YAML files it's not used !
        force : bool, optional
            If True, it allow to overwrites existing colorbar settings. The default is True.
            If False, it raise an error if attempting to overwrite an existing colorbar.
        verbose : bool, optional
            If True, the method will print a warning when overwriting existing colorbars. The default is True.

        Notes
        -----
        If a a colorbar configuration with the same name already exists, it will be overwritten.
        The validity of the colorbar(s) configuration(s) is not validated at registration !
        Use `pycolorbar.colorbars.validate()` to validate the registered colorbars.
        """
        # Check file exists
        if not os.path.isfile(filepath):
            raise ValueError(f"The colorbars configuration YAML file {filepath} does not exist.")
        # Read colorbars settings
        cbar_dicts = read_cbar_dicts(filepath=filepath)
        # Register colorbars settings
        for name, cbar_dict in cbar_dicts.items():
            if name in self.registry:
                if force and verbose:
                    print(f"Warning: Overwriting existing colorbar '{name}'")
                if not force:
                    raise ValueError(
                        f"A colorbar setting named '{name}' already exists. To allow overwriting, set 'force=True'."
                    )
            self.registry[name] = cbar_dict

    def unregister(self, name: str):
        """
        Remove a specific colorbar configuration from the registry.

        Parameters
        ----------
        name : str
            The name of the colorbar's configuration to remove.

        Raises
        ------
        ValueError
            If the colorbar with the specified name is not registered.
        """
        if name in self.registry:
            _ = self.registry.pop(name)
        else:
            raise ValueError(f"The colorbar configuration for {name} is not registered in pycolorbar.")

    def get_standalone_settings(self):
        """Return the colorbar settings names which are not a reference to another colorbar."""
        names = []
        for name in self.names:
            cbar_dict = self.get_cbar_dict(name, resolve_reference=False)
            if "reference" not in cbar_dict:
                names.append(name)
        return names

    def get_referenced_settings(self):
        """Return the colorbar settings names which a reference to another colorbar."""
        names = []
        for name in self.names:
            cbar_dict = self.get_cbar_dict(name, resolve_reference=False)
            if "reference" in cbar_dict:
                names.append(name)
        return names

    def add_cbar_dict(self, cbar_dict: dict, name: str, verbose: bool = True):
        """
        Add a colorbar configuration to the registry by providing a colorbar dictionary.

        Parameters
        ----------
        cbar_dict : dict
            The colorbar dictionary containing the colorbar's configuration.
        name : str
            The name of the colorbar.
        verbose : bool, optional
            If True, the method will print a warning when overwriting an existing colorbar. The default is True.
        Notes
        -----
        If a colorbar with the same name already exists, it will be overwritten.
        The configuration is validated when adding a colorbar configuration with this method !
        """
        # Check if the name is already used
        if verbose and name in self.registry:
            print(f"Warning: Overwriting existing colorbar '{name}'")
        # Validate cmap_dict
        cbar_dict = validate_cbar_dict(cbar_dict)
        # Update registry
        self.registry[name] = cbar_dict

    def get_cbar_dict(self, name: str, resolve_reference=True):
        """
        Retrieve the colorbar dictionary of a registered colorbar.

        Parameters
        ----------
        name : str
            The name of the colorbar.
        resolve_reference: bool
            Determines the behavior when the colorbar dictionary contains the 'reference' keyword.
            If True, the function resolves the reference by returning the actual colorbar dictionary
            that the reference points to.
            If False, the function returns the original colorbar dictionary, including the 'reference' keyword.
            The default is True.

        Returns
        -------
        dict
            The validated colorbar dictionary.

        Raises
        ------
        ValueError
            If the colorbar configuration is not registered.
        """
        if name not in self.registry:
            raise ValueError(f"The colorbar configuration for {name} is not registered in pycolorbar.")
        cbar_dict = self.registry[name]
        if resolve_reference and "reference" in cbar_dict:
            cbar_dict = self.registry[cbar_dict["reference"]]
            validate_cbar_dict(cbar_dict)
        return cbar_dict

    def get_cmap(self, name):
        """
        Retrieve the colormap of a registered colorbar.

        Parameters
        ----------
        name : str
            The name of the colorbar.

        Returns
        -------
        matplotlib.colors.Colormap
            The matplotlib Colormap.

        Notes
        -----
        This function also sets the over/under and bad colors specified in the colorbar configuration.

        """
        from pycolorbar.settings.colorbar_utility import get_cmap

        cbar_dict = self.get_cbar_dict(name=name, resolve_reference=True)
        return get_cmap(cbar_dict)

    def to_yaml(self, filepath, names=None, force=False, sort_keys=False):
        write_cbar_dicts(
            cbar_dicts=self.registry,
            filepath=filepath,
            names=names,
            force=force,
            sort_keys=sort_keys,
        )

    def validate(self, name: str = None):
        """
        Validate the registered colorbars. If a specific name is provided, only that colorbar is validated.

        Parameters
        ----------
        name : str, optional
            The name of a specific colorbar to validate. If None, all registered colorbars are validated.

        Raises
        ------
        ValueError
            If any of the validated colorbars have invalid configurations.

        Notes
        -----
        Invalid colorbar configurations are reported.
        """
        if isinstance(name, str):
            names = [name]
        else:
            names = self.names

        # Validate colorbars
        wrong_names = []
        for name in names:
            try:
                _ = validate_cbar_dict(self.get_cbar_dict(name, resolve_reference=False))
            except Exception as e:
                wrong_names.append(name)
                print(f"{name} has an invalid configuration: {e}")
                print("")
        if wrong_names:
            raise ValueError(f"The {wrong_names} colorbars have invalid configurations.")
        return

    def get_plot_kwargs(self, name=None, user_plot_kwargs={}, user_cbar_kwargs={}):
        """Get pycolorbar plot kwargs (updated with optional user arguments)."""
        from pycolorbar.settings.colorbar_utility import (
            get_plot_cbar_kwargs,
            update_plot_cbar_kwargs,
        )

        if not isinstance(name, (str, type(None))):
            raise TypeError("Expecting the colorbar setting name.")

        try:
            cbar_dict = self.get_cbar_dict(name)
        except Exception:
            cbar_dict = {}

        # Retrieve defaults pycolorbar kwargs
        plot_kwargs, cbar_kwargs = get_plot_cbar_kwargs(cbar_dict)
        plot_kwargs, cbar_kwargs = update_plot_cbar_kwargs(
            default_plot_kwargs=plot_kwargs,
            default_cbar_kwargs=cbar_kwargs,
            user_plot_kwargs=user_plot_kwargs,
            user_cbar_kwargs=user_cbar_kwargs,
        )
        return plot_kwargs, cbar_kwargs

    def show_colorbar(self, name, user_plot_kwargs={}, user_cbar_kwargs={}, fig_size=(6, 1)):
        from pycolorbar.settings.colorbar_visualization import plot_colorbar

        plot_kwargs, cbar_kwargs = self.get_plot_kwargs(
            name=name, user_plot_kwargs=user_plot_kwargs, user_cbar_kwargs=user_cbar_kwargs
        )

        plot_colorbar(plot_kwargs=plot_kwargs, cbar_kwargs=cbar_kwargs, ax=None, subplot_size=fig_size)

    def show_colorbars(self, category=None, exclude_referenced=True, subplot_size=None):
        """Display available colorbars (optionally of a specific category)"""
        from pycolorbar.settings.colorbar_visualization import plot_colorbars

        # Retrieve available (of a given category) colorbars settings
        names = self.available(category=category, exclude_referenced=exclude_referenced)
        # Display colorbars
        if len(names) > 0:
            list_args = [[name] + list(self.get_plot_kwargs(name=name)) for name in names]
            plot_colorbars(list_args, subplot_size=subplot_size)
        else:
            print(f"No colorbar settings are available within the category '{category}'.")


def register_colorbars(directory: str, verbose: bool = True, force: bool = True):
    """
    Register all colorbar YAML files present in the specified directory (if name=None).

    This function assumes that all YAML files present in the directory are
    valid pycolorbar colorbars configuration files.

    Parameters
    ----------
    directory : str
        The directory where colorbar YAML files are located.
    force : bool, optional
        If True, it allow to overwrites existing colorbar settings. The default is True.
        If False, it raise an error if attempting to overwrite an existing colorbar.
    verbose : bool, optional
        If True, the method will print a warning when overwriting existing colorbars. The default is True.

    Notes
    -----
    If a a colorbar configuration with the same name already exists and `force=True`, it will be overwritten.
    The validity of the colorbar(s) configuration(s) is not validated at registration !
    Use `pycolorbar.colorbars.validate()` to validate the registered colorbars.
    """
    # List the colorbar YAML files to register
    filepaths = list_yaml_files(directory)

    # Add colorbars to the ColorbarRegistry
    colorbars = ColorbarRegistry.get_instance()
    for filepath in filepaths:
        colorbars.register(filepath, force=force, verbose=verbose)


def register_colorbar(filepath: str, verbose: bool = True, force: bool = True):
    """
    Register a single colorbar YAML file.

    Parameters
    ----------
    filepath : str
        The file path where the colorbar's YAML file is located.
    force : bool, optional
        If True, it allow to overwrites existing colorbar settings. The default is True.
        If False, it raise an error if attempting to overwrite an existing colorbar.
    verbose : bool, optional
        If True, the method will print a warning when overwriting existing colorbars. The default is True.

    Raises
    ------
    ValueError
        If the specified colorbar YAML file is not available in the directory.

    Notes
    -----
    If a a colorbar configuration with the same name already exists and `force=True`, it will be overwritten.
    The validity of the colorbar(s) configuration(s) is not validated at registration !
    Use `pycolorbar.colorbars.validate()` to validate the registered colorbars.
    """
    colorbars = ColorbarRegistry.get_instance()
    colorbars.register(filepath, verbose=verbose, force=force)


def get_cbar_dict(name, resolve_reference=True):
    """
    Retrieve the validated colorbar dictionary of a registered colorbar.

    Parameters
    ----------
    name : str
        The name of the colorbar.
    resolve_reference: bool
        Determines the behavior when the colorbar dictionary contains the 'reference' keyword.
        If True, the function resolves the reference by returning the
        actual colorbar dictionary that the reference points to.
        If False, the function returns the original colorbar dictionary, including the 'reference' keyword.
        The default is True.

    Returns
    -------
    dict
        The validated colorbar dictionary.

    """
    colorbars = ColorbarRegistry.get_instance()
    return colorbars.get_cbar_dict(name, resolve_reference=resolve_reference)


def get_plot_kwargs(name=None, user_plot_kwargs={}, user_cbar_kwargs={}):
    colorbars = ColorbarRegistry.get_instance()
    return colorbars.get_plot_kwargs(name=name, user_plot_kwargs=user_plot_kwargs, user_cbar_kwargs=user_cbar_kwargs)


def available_colorbars(category=None, exclude_referenced=False):
    colorbars = ColorbarRegistry.get_instance()
    names = colorbars.available(category=category, exclude_referenced=exclude_referenced)
    return names
