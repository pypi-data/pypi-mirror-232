from abc import ABC, abstractmethod
from pathlib import Path as FilePath
from typing import List   # for getPathFlow() -> List[float]

import _contamxpy

_lib = _contamxpy.lib
_ffi = _contamxpy.ffi

MAX_LEN_VER_STR = 64
NAMEFIELDLEN = 48     # replaces NAMELEN and NMLN2


# =========================================================== class Zone  =====


class Zone:
    """Instances of :py:class:`Zone` are created via the
    :py:func:`prjDataReadyFcnP` callback function. If the callback function
    is called as indicated via the :py:class:`cxLib` constructor,
    then `Zones` will will be accessible via the :py:attr:`cxLib.zones` list.

    Attributes
    ----------
    nr : `int`
        Zone number, typically assigned by *ContamW*.
    name : `str`
        Zone name, typically assigned by *ContamW*.

        Implicit supply and return zones of simple air-handling systems (SAHS)
        will have either "(Sup)" or "(Ret)" appended to the name of the SAHS
        with which they are associated.

    flags : `int`

        + 0x01 variable Pressure node
        + 0x02 variable Mass fraction node
        + 0x04 variable Temperature node
        + 0x08 implicit Simple AHS node, i.e., supply or return
        + 0x10 unconditioned node
        + 0x20 node volume > 0, i.e., not massless

    volume : `real`
        Zone volume [m\ :sup:`3`]
    level_nr : `int`
        Level number on which this Zone is located.
    level_name : `str`
        Name of level on which this Zone is located.
    """

    def __init__(self, nr, name, flags, volume, level_nr, level_name) -> None:
        self.nr = nr
        self.name = name
        self.flags = flags
        self.volume = volume
        self.level_nr = level_nr
        self.level_name = level_name

    def __repr__(self):
        ret_str = (
            f"{self.__class__.__name__}({self.nr},{self.name},"
            f"{self.flags!r},{self.volume},{self.level_nr},{self.level_name})"
        )
        return ret_str

    def __str__(self):
        return (
            f"{self.__class__.__name__}(\n\tnr={self.nr}\n\t"
            f"name={self.name}\n\tflags={self.flags}\n\t"
            f"volume={self.volume}\n\tlevel_nr={self.level_nr}\n\t"
            f"level_name={self.level_name}\n\t"
        )

# =========================================================== class Path  =====


class Path:
    """Instances of Path are created via the
    :py:func:`contamxpy.prjDataReadyFcnP` callback function.  
    If the callback function is called as indicated via the :py:class:`cxLib`
    constructor, then `Paths` will will be accessible via the
    :py:attr:`cxLib.paths` list.

    Attributes
    ----------
    nr : `int`
        Path number, typically assigned by *ContamW*.
    flags : `int`
        Flags used to indicate airflow path properties. Not all of these flags
        are relevant to co-simulation, e.g., the WPC-related flags can be
        ignored.

        Airflow path flag values:

        + 0x0001 possible wind pressure
        + 0x0002 path uses WPC file pressure
        + 0x0004 path uses WPC file contaminants
        + 0x0008 Simple air-handling system (SAHS) supply or return path
        + 0x0010 SAHS recirculation flow path
        + 0x0020 SAHS outside air flow path
        + 0x0040 SAHS exhaust flow path
        + 0x0080 path has associate pressure limits
        + 0x0100 path has associate flow limits
        + 0x0200 path has associated constant airflow element
        + 0x0400 junction leak path

    from_zone : `int`
        Number of *From* zone used to indicate positive flow direction:
        *from_zone* -> to_zone. Zone `0` indicates *Ambient*.
    to_zone : `int`
        Number of *To* zone used to indicate positive flow direction:
        from_zone -> *to_zone*. Zone `0` indicates *Ambient*.
    ahs_nr : `int`
        Number of the Simple AHS associated with this Path if represents
        either a ventilation system *supply* or *return*.
    X : `real`
        X-coordinate
    Y : `real`
        Y-coordinate
    Z : `real`
        Z-coordinate
    envIndex : `int`
        Index identifies order of specifying values in WPC file and used to
        reference specific airflow paths located in ambient when using the
        ``contamx-lib`` API. Zero for airflow paths not located in ambient.
    """

    def __init__(self, nr, flags, from_zone, to_zone, ahs_nr,
                 X, Y, Z, envIndex) -> None:
        self.nr = nr
        self.flags = flags
        self.from_zone = from_zone
        self.to_zone = to_zone
        self.ahs_nr = ahs_nr
        self.X = X
        self.Y = Y
        self.Z = Z
        self.envIndex = envIndex

    def __repr__(self):
        return ("{}({!r},{!r},{!r},{!r},{!r},{:.2f},{:.2f},{:.2f},{!r})".
                format(self.__class__.__name__, self.nr, self.flags,
                       self.from_zone, self.to_zone, self.ahs_nr, self.X,
                       self.Y, self.Z, self.envIndex))

    def __str__(self):
        return (f"{self.__class__.__name__}(\n\tnr={self.nr}\n\t"
                f"flags={self.flags}\n\tfrom_zone={self.from_zone}\n\t"
                f"to_zone={self.to_zone}\n\tahs_nr={self.ahs_nr}\n\t"
                f"coords({self.X:.2f},{self.Y:.2f},{self.Z:.2f})\n\t"
                f"envIndex={self.envIndex}\n)")

# =================================================== class DuctTerminal  =====


class DuctTerminal:
    """Instances of DuctTerminal are created via the
    :py:func:`contamxpy.prjDataReadyFcnP` callback function.

    If the callback function is called as indicated via the :py:class:`cxLib`
    constructor, then `DuctTerminals` will will be accessible via the
    :py:attr:`cxLib.ductTerminals` list.

    Attributes
    ----------
    nr : `int`
        Duct Terminal number, typically assigned by *ContamW*.
    flags : `int`
        Airflow path flag values:  

        + 0x0001 terminal has wind pressure associated with it
        + 0x0002 terminal uses WPC file pressure
        + 0x0400 duct leak

    X : `real`
        X-coordinate [m]
    Y : `real`
        Y-coordinate [m]
    Z : `real`
        Z-coordinate [m]
    relHt : `real`
        Height relative to level on which the terminal is located [m]
    to_zone : `int`
        Zone number in which the terminal is located.
        Positive flow: terminal -> *to_zone*. Zone `0` indicates *Ambient*.
    envIndex : `int`
        Index identifies order of specifying values in WPC file and used to
        reference specific terminals located in ambient when using the
        ``contamx-lib`` API. Zero for terminals not located in ambient.
    """

    def __init__(self, nr, flags, X, Y, Z, relHt, to_zone, envIndex) -> None:
        self.nr = nr
        self.flags = flags
        self.X = X
        self.Y = Y
        self.Z = Z
        self.relHt = relHt
        self.to_zone = to_zone
        self.envIndex = envIndex

    def __repr__(self):
        return ("{}({!r},{!r},{:.2f},{:.2f},{:.2f},{!r},{!r},{!r})".format(
            self.__class__.__name__, self.nr, self.flags,
            self.X, self.Y, self.Z, self.relHt, self.to_zone, self.envIndex)
        )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(\n\tnr={self.nr}\n\t"
            f"flags={self.flags}\n\t"
            f"coords({self.X:.2f},{self.Y:.2f},{self.Z:.2f})\n\t"
            f"relHt={self.relHt}\n\tto_zone={self.to_zone}\n\t"
            f"envIndex={self.envIndex}\n)"
        )


class DuctLeak(DuctTerminal):
    """Instances of DuctLeak are created via the
    :py:func:`contamxpy.prjDataReadyFcnP` callback function.

    If the callback function is called as indicated via the :py:class:`cxLib`
    constructor, then `DuctLeaks` will be accessible via the
    :py:attr:`cxLib.ductLeaks` list.

    :py:class:`contamxpy.DuctLeak` inherits :py:class:`contamxpy.DuctTerminal`.
    """

# =================================================== class DuctJunction  =====


class DuctJunction:
    """Instances of `DuctJunction` are created via the
    :py:func:`contamxpy.prjDataReadyFcnP` callback function.

    If the callback function is called as indicated via the
    :py:class:`cxLib` constructor, then `DuctJunctions` will be accessible
    via the :py:attr:`cxLib.ductJunctions` list.

    Attributes
    ----------
    nr : `int`
        Duct Junction number, typically assigned by *ContamW*.
    flags : `int`

    containing_zone : `int`
        Zone number in which the junction is located. Zone `0`
        indicates *Ambient*.
    envIndex : `int`
        Index identifies order of specifying values in WPC file and used to
        reference specific duct junctions located in ambient when using the
        ``contamx-lib`` API. Zero for duct junctions not located in ambient.

    """

    def __init__(self, nr, flags, containing_zone, envIndex) -> None:
        self.nr = nr
        self.flags = flags
        self.containing_zone = containing_zone
        self.envIndex = envIndex

    def __repr__(self):
        return ("{}({!r},{!r},{!r},{!r})".format(
            self.__class__.__name__, self.nr, self.flags,
            self.containing_zone, self.envIndex))

    def __str__(self):
        return (
            f"{self.__class__.__name__}(\n\tnr={self.nr}\n\t"
            f"flags={self.flags}\n\tcontaining_zone={self.containing_zone}\n\t"
            f"envIndex={self.envIndex}\n)")


# ============================================================= class AHS =====
class AHS:
    """Instances of AHS are created via the
    :py:func:`contamxpy.prjDataReadyFcnP` callback function.

    If the callback function is called as indicated via the :py:class:`cxLib`
    constructor, then `AHS`\s will will be accessible via the
    :py:attr:`cxLib.AHSs` list.

    Attributes
    ----------
    nr : `int`
        Simple AHS number, typically assigned by *ContamW*.
    name : `str`
        Simple AHS name, typically assigned by *ContamW*.
    zone_ret : `int`
        Number of the implicit Return zone associated with this AHS.
    zone_sup : `int`
        Number of the implicit Supply zone associated with this AHS.
    path_rec : `int`
        Number of the implicit Recirculation flow path associated
        with this AHS.
    path_oa : `int`
        Number of the implicit Outdoor air intake flow path associated
        with this AHS.
    path_exh : `int`
        Number of the implicit Exhaust flow path associated with this AHS.
    """

    def __init__(self, nr, name, zone_ret, zone_sup, path_rec,
                 path_oa, path_exh) -> None:
        self.nr = nr
        self.name = name
        self.zone_ret = zone_ret
        self.zone_sup = zone_sup
        self.path_rec = path_rec
        self.path_oa = path_oa
        self.path_exh = path_exh
        self.supply_points = []
        self.return_points = []

    def __repr__(self):
        return ("{}({!r},{!r},{!r},{!r},{!r},{!r},{!r})".format(
            self.__class__.__name__, self.nr, self.name,
            self.zone_ret, self.zone_sup, self.path_rec,
            self.path_oa, self.path_exh)
        )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(\n\tNr={self.nr}\n\t"
            f"name={self.name}\n\tzone_ret={self.zone_ret}\n\t"
            f"zone_sup={self.zone_sup}\n\tpath_rec={self.path_rec}\n\t"
            f"path_oa={self.path_oa}\n\tpath_exh={self.path_exh}\n)"
        )

    def diagram(self):
        print(f"\n========== AHS {self.nr}: {self.name}\n")
        print("->-(oa)-+----->[sup]-->[Zone Supplies]")
        print("        | ")
        print("      (rec)")
        print("        | ")
        print("<-(exh)-+---<--[ret]<--[Zone Returns]\n")
        print(
            f"Implicit Flow Paths: rec={self.path_rec} oa={self.path_oa} "
            f"exh={self.path_exh} ")
        print(f"Implicit Zones: ret={self.zone_ret} sup={self.zone_sup}")
        print("Zone Supplies:", end=" ")
        for path in self.supply_points:
            print(f"(p{path.nr} z{path.to_zone})", end=" ")
        print("\nZone Returns: ", end=" ")
        for path in self.return_points:
            print(f"(p{path.nr} z{path.from_zone})", end=" ")
        print("\n==========")

# ======================================================== class Control  =====


class Control(ABC):
    """Abstract Base Class of :py:class:`contamxpy.InputControl` and
    :py:class:`contamxpy.OutputControl`.

    Attributes
    ----------
    nr
        Control node number, typically assigned by *ContamW*.
    name
        Name of control node, typically user-defined via *ContamW*.
    """

    def __init__(self, nr, name) -> None:
        self.nr: int = nr
        self.name: str = name

    @abstractmethod
    def dummy(self):
        pass

# =================================================== class InputControl  =====


class InputControl(Control):
    """This class extends base class :py:class:`contamxpy.Control`.

    Attributes
    ----------
    typeStr = CT_SET

    """

    def __init__(self, nr, name, type_str="CT_SET") -> None:
        super().__init__(nr, name)
        self.type_str: str = type_str

    def __repr__(self):
        return ("{}({!r},{!r},{!r})".format(
            self.__class__.__name__, self.nr, self.name, self.type_str))

    def dummy(self):
        return super().dummy()

# ================================================== class OutputControl  =====


class OutputControl(Control):
    """This class extends base class :py:class:`contamxpy.Control`.

    Attributes
    ----------
    typeStr = CT_PASS

    """

    def __init__(self, nr, name, type_str="CT_PASS") -> None:
        super().__init__(nr, name)
        self.type_str: str = type_str

    def __repr__(self):
        return ("{}({!r},{!r},{!r})".format(
            self.__class__.__name__, self.nr, self.name, self.type_str))

    def dummy(self):
        return super().dummy()

# ========================================================== class cxLib  =====


class cxLib:
    """
    :py:class:`contamxpy.cxLib` provides a wrapper around ``contamx-lib`` that
    provides a thread-safe API to the CONTAM simulation engine, ContamX.
    A simulation *state* is associated with each instance of
    :py:class:`contamxpy.cxLib` upon instantiation for a particular
    CONTAM PRJ file.

    Attributes
    ----------
    prj_file_path : `string`
        Provide path to associated PRJ file. It will be converted to a `prjlib`
        path to set the :py:attr:`contamxpy.cxLib.prjPath` instance attribute.

    wp_mode : `int` {0, 1}, optional
        Set wind pressure calculation method :py:attr:`cxLib.wp_mode`

        + 0 = CONTAM computes wind pressures using WTH-like messages and
            ambient Mass Fractions using CTM-like messages, i.e.,
            setAmbtXXX() messages.
        + 1 = Use envelope-related functions of the contam-x-cosim API to set
            wind pressure of individual envelope flow paths (default), i.e.,
            setEnvelopeXXX().

    cb_option : `bool`, optional
        Set callback option :py:attr:`cxLib.cb_option` for
        :py:func:`contamxpy.prjDataReadyFcnP`

        + `False` = ``contamx-lib`` will not execute callback function.
        + `True`  = ``contamx-lib`` will execute callback function.

    wth_init_function : (function name), optional
        Set user-defined function :py:func:`cxLib.wth_init_function` via this
        parameter. It will be called by :py:func:`contamxpy.prjDataReadyFcnP`,
        for example, to set initial ambient conditions prior to running
        steady-state initialization calculations.
    """

    def __init__(self, prj_file_path: str, wp_mode: int = 0,
                 cb_option: bool = False, wth_init_function=None):

        # ----- Instance Attributes -----#

        self._self_handle = _ffi.new_handle(self)
        """`void *` - FFI-generated handle."""

        self._state = _lib.cxiGetContamState()
        """`void *` - ContamXState obtained from ``contamx-lib`` via
        instantiation of :py:class:`cxLib`."""

        self.prj_file_path = FilePath(prj_file_path)
        """`pathlib` form of CONTAM PRJ file with which this instance of
        :py:class:`contamxpy.cxLib` is associated.

        This attribute is set via the `prj_file_path` parameter of
        the constructor.
        """

        self.wp_mode: int = wp_mode

        if wp_mode < 0 or wp_mode > 1:
            wp_mode = 0
        _lib.cxiSetWindPressureMode(self._state, wp_mode)

        self.cb_option: bool = cb_option

        # DEBUG
        # print(f"cxLib __init__() =>\n\t_state=[{self._state}]\n\t")
        # print(f"self_handle=[{self._self_handle}]\n\tself=[{self}]\n")
        # print(f"\tnContaminants={self.nContaminants}\n\tn")
        # print(f"Zones={self.nZones}\n\tnPaths={self.nPaths}\n")

        if (cb_option is True):
            # {self._self_handle} is passed through to provide the callback
            #   with access to the instance of the {cxLib} object.
            _lib.cxiRegisterCallback_PrjDataReady(
                self._state, self._self_handle, _lib.prjDataReadyFcnP)

        self.wth_init_function = wth_init_function

        self.verbose: int = 0
        """Logging level {0 = none (default), 1 = medium, 2 = high}.

        Set via the :py:func:`cxLib.setVerbosity`.
        """

        # ----- PRJ-related Instance Attributes -----#

        self.nContaminants: int = -1
        """(Read-only) Number of `Contaminants` in the PRJ. Defaults to `-1`.
        See :py:attr:`cxLib.contaminants`.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.contaminants: list = []
        """(Read-only) List of contaminant names (`list` of `str`).

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.nZones: int = -1
        """(Read-only) Number of `Zones` in the PRJ. Defaults to `-1`.
        See :py:attr:`cxLib.zones`.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.zones: list = []
        """(Read-only) List of :py:class:`contamxpy.Zone` objects.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.nPaths: int = -1
        """(Read-only) Number of `Paths` in the PRJ. Defaults to `-1`.
        See :py:attr:`cxLib.paths`.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.paths: list = []
        """(Read-only) List of :py:class:`contamxpy.Path` objects.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.nEnvPaths: int = -1
        """(Read-only) Number of `Paths` in the PRJ connected to ambient.
        Defaults to `-1`.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.envPaths: list = []
        """(Read-only) List of :py:class:`contamxpy.Path` objects with
        connections to Ambient.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.nAhs: int = -1
        """(Read-only) Number of `Simple AHSs` in the PRJ. Defaults to `-1`.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.AHSs: list = []
        """(Read-only) List of :py:class:`contamxpy.AHS` objects.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.nInputControls: int = -1
        """(Read-only) Number of `Input Controls`, i.e., *Constant* type
        controls in the PRJ. Defaults to `-1`.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.nOutputControls: int = -1
        """(Read-only) Number of `Output Controls`, i.e., *Signal split* type
        controls in the PRJ. Defaults to `-1`.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.inputControls: list = []
        """(Read-only) List of :py:class:`contamxpy.InputControl` objects.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.outputControls: list = []
        """(Read-only) List of :py:class:`contamxpy.OutputControl` objects.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.nDuctJunctions: int = -1
        """(Read-only) Number of `Duct Junctions` in the PRJ. Defaults to `-1`.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.ductJunctions: list = []
        """(Read-only) List of :py:class:`contamxpy.DuctJunction` objects.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.nDuctTerminals: int = -1
        """(Read-only) Number of `Duct Terminals` in the PRJ. Defaults to `-1`.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.ductTerminals: list = []
        """(Read-only) List of :py:class:`contamxpy.DuctTerminal` objects.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.nEnvTerminals: int = -1
        """(Read-only) Number of `Duct Terminals` in the PRJ connected to
        ambient. Defaults to `-1`.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.envTerminals: list = []
        """(Read-only) List of :py:class:`contamxpy.DuctTerminal` objects with
        connections to Ambient.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.nDuctLeaks: int = -1
        """(Read-only) Number of `Duct Leaks` in the PRJ. Defaults to `-1`.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

        self.ductLeaks: list = []
        """(Read-only) List of :py:class:`contamxpy.DuctLeak` objects.

        Set via the :py:func:`contamxpy.prjDataReadyFcnP` callback function if
        :py:attr:`cxLib.cb_option` is `True`.
        """

    @staticmethod
    def __convertString(cdataStr):
        """
        Private helper function used to decode C-strings to Python strings.

        :param cdataStr: C-string obtained via `contamx-lib` function calls,
        e.g., *cxiGetVersion(state, buffer)*

        :rtype: str
        """
        return _ffi.string(cdataStr).decode('utf-8')

    def setVerbosity(self, level=0):
        """Set logging level for instance of :py:class:`cxLib`.
        See :py:attr:`cxLib.verbose`.

        Args:
            level : `int`
                Logging level:

                + 0 No logging
                + 1 Minimal logging
                + 2 Maximum logging
        """
        self.verbose = max(level, 0)

    # ---------- contamx-lib: simulation initialization

    def setupSimulation(self, use_cosim=1) -> int:
        """
        Setup the simulation including the option to run ContamX in the
        co-simulation mode. Calling cxiSetupSimulation() with `use_cosim`
        set to `1` will initiate the simulation by reading the PRJ file,
        allocating simulation data, calling of the user-defined callback
        function if set to do so via cxiRegisterCallback_PrjDataReady(), and
        running the steady state initialization.

        Args:
            use_cosim: `int`
                Select ContamX run mode:

                * 0 = run a CONTAM-only simulation,
                * 1 = run ContamX in co-simulation mode.

        :returns: 0 indicating success, 1 indicating invalid settings for co-simulation.
        :rtype: int
        """
        strPath = str(self.prj_file_path)
        return _lib.cxiSetupSimulation(self._state, strPath.encode('ascii'), use_cosim)

    def getVersion(self):
        """
        :returns: The version of ``contamx-lib``, i.e., the *ContamX* version,
            e.g., `3.4.1.4-64bit`.
        :rtype: str
        """
        buffer_str = _ffi.new("char[]", MAX_LEN_VER_STR)
        _lib.cxiGetVersion(self._state, buffer_str)
        return cxLib.__convertString(buffer_str)

    # ---------- contamx-lib: Simulation properties ----------
    def getSimTimeStep(self):
        """
        :returns: Calculation time step in seconds (1 - 60)
        :rtype: int
        """
        time_step = _lib.cxiGetSimulationTimeStep(self._state)
        return time_step

    def getSimStartDate(self):
        """
        :returns: Start day of year of the simulation [1 - 365]
        :rtype: int
        """
        day_of_year = _lib.cxiGetSimulationStartDate(self._state)
        return day_of_year

    def getSimEndDate(self):
        """
        :returns: End day of year of the simulation [1 - 365]
        :rtype: int
        """
        day_of_year = _lib.cxiGetSimulationEndDate(self._state)
        return day_of_year

    def getSimStartTime(self):
        """
        :returns: Start time of day the simulation in seconds [0 - 86400)
        :rtype: int
        """
        time_of_day_seconds = _lib.cxiGetSimulationStartTime(self._state)
        return time_of_day_seconds

    def getSimEndTime(self):
        """
        :returns: End time of day of the simulation in seconds [0 - 86400)
        :rtype: int
        """
        time_of_day_seconds = _lib.cxiGetSimulationEndTime(self._state)
        return time_of_day_seconds

    # ---------- contamx-lib: Simulation time ----------
    def getCurrentDayOfYear(self):
        """
        :returns: Current day of year of the simulation [1 - 365]
        :rtype: int
        """
        return _lib.cxiGetCurrentDate(self._state)

    def getCurrentTimeInSec(self):
        """
        :returns: Current time of day of the simulation in seconds [0 - 86400)
        :rtype: int
        """
        return _lib.cxiGetCurrentTime(self._state)

    # ----------- contamx-lib: Simulation control ----------
    def doSimStep(self, step_forward=1):
        """Run next simulation time step.

        Args:
            stepForward : `int`
                Currently only a value of  `1` is allowed which will
                run the next time step.
        """
        step_forward = 1
        _lib.cxiDoCoSimStep(self._state, step_forward)

    def endSimulation(self):
        """This function must be called at the end of a co-simulation. 
        This should only be called after all time steps of the co-simulation
        have been completed, i.e., after :py:func:`cxLib.doSimStep` has been
        called for the values obtained for the ending date and time of
        the simulation."""
        _lib.cxiEndSimulation(self._state)

    # ----------- contamx-lib: Set ambient conditions ----------
    def setAmbtTemperature(self, temperature):
        """Set outdoor temperature [K] (temperature >= 0)."""
        _lib.cxiSetAmbtTemperature(self._state, temperature)

    def setAmbtPressure(self, pressure):
        """Set outdoor pressure [Pa] (pressure >= 0)."""
        _lib.cxiSetAmbtPressure(self._state, pressure)

    def setAmbtWindSpeed(self, wind_speed):
        """Set wind speed [m/s] (WS >= 0)."""
        _lib.cxiSetAmbtWndSpd(self._state, wind_speed)

    def setAmbtWindDirection(self, wind_direction):
        """Set wind direction [deg] (0 <= wind_direction <= 360)."""
        wind_direction = wind_direction % 360
        _lib.cxiSetAmbtWndDir(self._state, wind_direction)

    def setAmbtMassFraction(self, contaminant_nr, mass_fraction):
        """Set outdoor mass fraction [kg_cont/kg_air]
        (0.0 <= mass_fraction <= 1.0)."""
        mass_fraction = max(0.0, min(mass_fraction, 1.0))
        _lib.cxiSetAmbtMassFraction(self._state, contaminant_nr, mass_fraction)

    def setEnvelopeWP(self, env_index, wind_pressure):
        """
        Set the wind pressure of an envelope flow path. This is akin to
        using a WPC file.

        Args:
            env_index : `int`
                Index set by ContamX. See :py:attr:`contamxpy.Path.envIndex`.
            wind_pressure: `float`
                Wind pressure value [Pa].
        """
        _lib.cxiSetEnvelopeWP(self._state, env_index, wind_pressure)

    def setEnvelopeMF(self, env_index, contaminant_num, mass_fraction):
        """
        Set the mass fraction at an envelope flow path. This is akin to
        using a WPC file.

        Args:
            env_index : `int`
                Index set by ContamX. See :py:attr:`contamxpy.Path.envIndex`.
            contaminant_num : `int`
               Contaminant number, e.g., assigned by ContamW
            mass_fraction: `float`
                Mass fraction [kg_cont/kg_air].
        """
        _lib.cxiSetEnvelopeMF(self._state, env_index, 
                              contaminant_num, mass_fraction)

    # ----------- contamx-lib: Other Set methods ----------
    def setZoneAddMass(self, zone_num, contaminant_num, mass) -> int:
        """
        Add mass of contaminant to zone.

        Args:
            zone_num : `int`
                Zone number to which mass should be added. Zone
                numbers range from `1` to :py:attr:`contamxpy.cxLib.nZones`and
                are assigned by *ContamW*.
            contaminant_num : `int`
                Number of contaminant for which mass is to be added to zone.
                Contaminant numbers range from `0` to
                :py:attr:`contamxpy.cxLib.nContaminants` `-1` and
                are assigned by *ContamW*.
            mass : `float`
                Amount of mass [kg] to add to the zone (>= 0.0).

        :returns: 0 indicating success, > 0 indicating error occurred.
        :rtype: int

        """
        if (zone_num > self.nZones):
            return 1
        elif (mass < 0.0):
            return 2
        elif (contaminant_num > self.nContaminants):
            return 3
        _lib.cxiSetZoneAddMass(self._state, zone_num, contaminant_num, mass)
        return 0

    def setZoneTemperature(self, zone_num, temperature) -> int:
        """Set zone temperature.

        Args:
            zone_num : `int`
                Zone number for which temperature should be set. Zone
                numbers range from `1` to :py:attr:`contamxpy.cxLib.nZones`
                and are assigned by *ContamW*.
            temperature : `float`
                Temperature [K] to set (>= 0.0).
        """
        t_set = max(0.0, temperature)
        _lib.cxiSetZoneTemperature(self._state, zone_num, t_set)

    def setJunctionTemperature(self, junction_num, temperature) -> int:
        """Set Duct Junction temperature.

        Args:
            junction_num : `int`
                Junction number for which temperature should be set. Zone
                numbers range from `1` to 
                :py:attr:`contamxpy.cxLib.nDuctJunctions` and are assigned
                by *ContamW*.
            temperature : `float`
                Temperature [K] to set (>= 0.0).
        """
        t_set = max(0.0, temperature)
        _lib.cxiSetJunctionTemperature(self._state, junction_num, t_set)

    def setAhsSupplyReturnFlow(self, path_num, flow):
        """Set airflow rate of Simple AHS Supply or Return flow path.

        Args:
            path_num : `int`
                Airflow path number for which flow should be set. Path 
                numbers range from `1` to :py:attr:`contamxpy.cxLib.nPaths`
                and are assigned by *ContamW*.
            flow : `float`
                Mass flow rate [kg/s] to set (>= 0.0).
        """
        flow_set = max(0.0, flow)
        _lib.cxiSetSupplyReturnPathFlow(self._state, path_num, flow_set)

    def setAhsPercentOa(self, ahs_num, oa_fraction):
        """Set Outdoor Air fraction for Simple AHS.

        Args:
            ahs_num: `int`
                Air-handling System number for which OA fraction is to be set.
                AHS numbers range from `1` to :py:attr:`contamxpy.cxLib.nAhs`
                and are typically assigned by *ContamW*.
            oa_fraction: `float`
                Fraction of outdoor air (0 <= oa_fraction <= 1.0)

        """
        frac_set = max(0.0, min(oa_fraction, 1.0))
        # print(f"setAhsPctOa({ahsNr} {f})")
        _lib.cxiSetAHSPercentOA(self._state, ahs_num, frac_set)

    # ----------- contamx-lib: Get results methods ----------

    def getZoneMassFraction(self, zone_num, contaminant_num) -> float:
        """Get the mass fraction of a zone for selected contaminant.

        Args:
            zone_num : `int`
                Zone number for which mass fraction should be obtained. Zone
                numbers range from `1` to :py:attr:`contamxpy.cxLib.nZones`
                and are assigned by *ContamW*.
            contaminant_num : `int`
                Contaminant number for which mass fraction should be obtained.
                Contaminant numbers range from `0` to
                :py:attr:`contamxpy.cxLib.nContaminants` -1 and
                are assigned by *ContamW*.

        :returns: Mass fraction [kg_cont/kg_air].
        :rtype: float
        """
        ptr_mass_fraction = _ffi.new("double *")
        _lib.cxiGetZoneMF(self._state, zone_num,
                          contaminant_num, ptr_mass_fraction)
        mass_fraction = ptr_mass_fraction[0]
        return mass_fraction

    def getEnvelopeExfil(self, envIndex, contaminant_num) -> float:
        """Get the mass of contaminant exfiltrating from
        an envelope airflow path.

        Args:
            envIndex : `int`
                Envelope index of airflow path for which to
                obtain exfiltration.
            contaminant_num : `int`
                Contaminant number for which exfiltrating mass should
                be obtained. Contaminant numbers range from
                `0` to :py:attr:`contamxpy.cxLib.nContaminants` -1 and
                are assigned by *ContamW*.

        :returns: Mass of contaminant [kg_cont].
        :rtype: float

        .. seealso::
            :py:attr:`contamxpy.cxLib.paths`
            :py:attr:`contamxpy.Path.envIndex`
        """
        ptr_mass = _ffi.new("double *")
        _lib.cxiGetEnvelopeExfil(self._state, envIndex,
                                 contaminant_num, ptr_mass)
        mass = ptr_mass[0]
        return mass

    def getPathFlow(self, path_num) -> List[float]:
        """Get airflow rate through path.

        Args:
            path_num : `int`
                Number of flow path for which to obtain airflow rate.

        :returns: Array of two-way flows through the path: Flow0 and Flow1 [kg/s]
        :rtype: float[]
        """
        ptr_flow_0 = _ffi.new("double *")
        ptr_flow_1 = _ffi.new("double *")
        retVal = _lib.cxiGetPathFlows(self._state, path_num,
                                      ptr_flow_0, ptr_flow_1)
        flows = [ptr_flow_0[0], ptr_flow_1[0]]
        return flows

    def getDuctTerminalFlow(self, terminal_num) -> float:
        """Get airflow rate through duct terminal.

        Args:
            terminal_num : `int`
                Number of duct terminal (1 - :py:attr:`cxLib.ductTerminals`)
                in the :py:attr:`contamxpy.cxLib.ductTerminals` list for
                which to obtain the airflow rate.

        :returns: Positive airflow out of the terminal into the zone or
            Negative airflow into the terminal from the zone [kg/s]

        :rtype: float
        """
        ptr_flow = _ffi.new("double *")
        retVal = _lib.cxiGetTermFlow(self._state, terminal_num, ptr_flow)
        flow = ptr_flow[0]
        return flow

    def getDuctLeakFlow(self, leak_num) -> float:
        """Get airflow rate through duct leak.

        Args:
            leak_num : `int`
                Number of duct leak (1 -> :py:attr:`cxLib.nDuctLeaks`) in the
                :py:attr:`cxLib.ductLeaks` list for which to obtain the
                airflow rate.

        :returns: Positive airflow out of the junction into the zone or
            Negative airflow into the junction from the zone [kg/s]
        :rtype: float
        """
        ptr_flow = _ffi.new("double *")
        retVal = _lib.cxiGetLeakFlow(self._state, leak_num, ptr_flow)
        flow = ptr_flow[0]
        return flow

    # ----------- contamx-lib: Controls methods ----------
    def setInputControlValue(self, i, val):
        """Set value of Input control type (CT_SET).

        Args:
            i : `int`
                Index of Input control (1 - :py:attr:`cxLib.nInputControls`)
                in the :py:attr:`cxLib.inputControls` list for which to set
                the value.
            val : `float`
                Value to set.
        """
        retVal = _lib.cxiSetInputControlValue(self._state, i, val)

    def getOutputControlValue(self, i) -> float:
        """Get Output control value (CT_PASS).

        Args:
            i : `int`
                Index of Output control (1 - :py:attr:`cxLib.nOutputControls`)
                in the :py:attr:`contamxpy.cxLib.outputControls` list for
                which to get the value.

        :returns: Value of control output signal.
        :rtype: float

        .. todo::
            Initial values all seem to be 0.0 even though LOG file results
            appear to reflect steady-state simulation results.
        """
        ptr_ctrl_value = _ffi.new("float *")
        retVal = _lib.cxiGetOutputControlValue(self._state, i, ptr_ctrl_value)
        ctrl_value = ptr_ctrl_value[0]
        return ctrl_value

    # ----------- Called by prjDataReadyFcnP() ----------
    # These "private" functions are used to populate the list of
    #   items which are members of cxLib instances.
    #
    def _getCtmName(self, i):
        """
        Args:
            i : `int`
                Contaminant number, e.g., assigned by ContamW

        :returns: Contaminant name.
        :rtype: str
        """
        name_str = _ffi.new("char[]", NAMEFIELDLEN)
        if 0 <= i < self.nContaminants:
            _lib.cxiGetCtmName(self._state, i, name_str)
        return cxLib.__convertString(name_str)

    def _getZoneInfo(self, zone_num):
        """
        Args:
            zone_num : `int`
                Zone number, e.g., assigned by ContamW

        :returns: :py:class:`contamxpy.Zone` instance for requested Zone number
        :rtype: :py:class:`contamxpy.Zone`
        """
        ptr_zone = _ffi.new("ZONE_COSIM_DSC *")
        zone_name_str = _ffi.new("char[]", NAMEFIELDLEN)
        level_name_str = _ffi.new("char[]", NAMEFIELDLEN)

        if 0 < zone_num <= self.nZones:
            _lib.cxiGetZoneInfo(self._state, zone_num, ptr_zone)
            zone_name_str = cxLib.__convertString(ptr_zone.name)
            level_name_str = cxLib.__convertString(ptr_zone.level_name)
            zone = Zone(ptr_zone.nr, zone_name_str, ptr_zone.flags,
                        ptr_zone.Vol, ptr_zone.level_nr, level_name_str)
        return zone

    def _getPathInfo(self, path_num):
        """
        Args:
            path_num : `int`
                Path number, e.g., assigned by ContamW

        :returns: :py:class:`contamxpy.Path` instance for requested Path number
        :rtype: :py:class:`contamxpy.Path`
        """
        ptr_path = _ffi.new("PATH_COSIM_DSC *")

        if 0 < path_num <= self.nPaths:
            _lib.cxiGetPathInfo(self._state, path_num, ptr_path)
            path = Path(ptr_path.nr, ptr_path.flags,
                        ptr_path.from_zone, ptr_path.to_zone, ptr_path.ahs_nr,
                        ptr_path.X, ptr_path.Y, ptr_path.Z, ptr_path.envIndex)
        return path

    def _getAhsInfo(self, ahs_num):
        """
        Args:
            ahs_num : `int`
                AHS number, e.g., assigned by ContamW

        :returns: :py:class:`contamxpy.AHS` instance for requested AHS number
        :rtype: :py:class:`contamxpy.AHS`
        """
        ptr_ahs = _ffi.new("AHS_COSIM_DSC *")
        ahs_name_str = _ffi.new("char[]", NAMEFIELDLEN)

        if 0 < ahs_num <= self.nAhs:
            _lib.cxiGetAhsInfo(self._state, ahs_num, ptr_ahs)
            ahs_name_str = cxLib.__convertString(ptr_ahs.name)
            ahs = AHS(ptr_ahs.nr, ahs_name_str,
                      ptr_ahs.zone_ret, ptr_ahs.zone_sup,
                      ptr_ahs.path_rec, ptr_ahs.path_oa, ptr_ahs.path_exh)
        return ahs

    def _getJunctionInfo(self, junction_num):
        """
        Args:
            junction_num : `int`
                Junction number, e.g., assigned by ContamW. NOTE: Terminals
                are also Junctions.

        :returns: :py:class:`contamxpy.DuctJunction` instance for requested
            Junction number
        :rtype: :py:class:`contamxpy.DuctJunction`
        """
        ptr_junction = _ffi.new("JCT_COSIM_DSC *")

        if 0 < junction_num <= self.nDuctJunctions:
            _lib.cxiGetJunctionInfo(self._state, junction_num, ptr_junction)
            junction = DuctJunction(
                ptr_junction.nr, ptr_junction.flags,
                ptr_junction.containing_zone, ptr_junction.envIndex)
        return junction

    def _getTerminalInfo(self, terminal_num):
        """
        Args:
            terminal_num : `int`
                Terminal number, e.g., assigned by ContamW. NOTE:
                All Terminals are also Junctions.

        :returns: :py:class:`contamxpy.DuctTerminal` instance for the
            requested Terminal number
        :rtype: :py:class:`contamxpy.DuctTerminal`
        """
        ptr_terminal = _ffi.new("TERM_COSIM_DSC *")

        if 0 < terminal_num <= self.nDuctTerminals:
            _lib.cxiGetTermInfo(self._state, terminal_num, ptr_terminal)
            terminal = DuctTerminal(
                ptr_terminal.nr, ptr_terminal.flags, ptr_terminal.X,
                ptr_terminal.Y, ptr_terminal.Z, ptr_terminal.relHt,
                ptr_terminal.to_zone, ptr_terminal.envIndex)
        return terminal

    def _getLeakInfo(self, leak_num):
        """
        Args:
            leak_num : `int`
                Leak number, e.g., assigned by ContamX, i.e.,
                Duct leakage is not stored in the PRJ.
                Leakage is determined by ContamX prior to simulation.
                NOTE: Leaks utilize the TERM_COSIM_DSC data structure.

        :returns: :py:class:`contamxpy.DuctTerminal` instance for requested
            Leak number
        :rtype: :py:class:`contamxpy.DuctTerminal`
        """
        ptr_terminal = _ffi.new("TERM_COSIM_DSC *")

        if 0 < leak_num <= self.nDuctLeaks:
            _lib.cxiGetLeakInfo(self._state, leak_num, ptr_terminal)
            leak = DuctLeak(ptr_terminal.nr, ptr_terminal.flags,
                            ptr_terminal.X, ptr_terminal.Y, ptr_terminal.Z,
                            ptr_terminal.relHt, ptr_terminal.to_zone,
                            ptr_terminal.envIndex)
        return leak

    def _getInputControlInfo(self, ctrl_index):
        """
        Args:
            ctrl_index : `int`
                Input control index assigned by ``contamx-lib`` upon
                initialization of co-simulation lists.

        :returns: :py:class:`contamxpy.InputControl` instance for the
            requested index
        :rtype: :py:class:`contamxpy.InputControl`
        """
        ptr_control = _ffi.new("CONTROL_COSIM_DSC *")

        if 0 < ctrl_index <= self.nInputControls:
            _lib.cxiGetInputControlInfo(self._state, ctrl_index, ptr_control)
            ctrl_name_str = cxLib.__convertString(ptr_control.name)
            ctrl = InputControl(ptr_control.nr, ctrl_name_str)
        return ctrl

    def _getOutputControlInfo(self, ctrl_index):
        """
        Args:
            ctrl_index : `int`
                Output control index assigned by ``contamx-lib`` upon
                initialization of co-simulation lists. 

        :returns: :py:class:`contamxpy.OutputControl` instance for the
            requested index
        :rtype: :py:class:`contamxpy.OutputControl`

        """
        ptr_control = _ffi.new("CONTROL_COSIM_DSC *")

        if (ctrl_index > 0 and ctrl_index <= self.nOutputControls):
            _lib.cxiGetOutputControlInfo(self._state, ctrl_index, ptr_control)
            ctrl_name_str = cxLib.__convertString(ptr_control.name)
            ctrl = OutputControl(ptr_control.nr, ctrl_name_str)
        return ctrl


# ===================================================== Callback function =====
#
@_ffi.def_extern()
def prjDataReadyFcnP(state, handle):
    """
    This function populates the list attributes associated with
    :py:class:`cxLib`, e.g., :py:attr:`contamxpy.cxLib.contaminants`,
    :py:attr:`contamxpy.cxLib.zones`, and :py:attr:`contamxpy.cxLib.paths`.

    NOTE: The function name must match that in the associated
    `contamx-build.py` module that defines the CFFI interface of
    :py:mod:`contamxpy`.

    Parameters
    ----------
    state
        The *ContamXState* obtained from ``contamx-lib`` upon instantiation of
        a :py:class:`cxLib` object.
    handle
        The CFFI handle to the current :py:class:`cxLib` instance.

    """

    # ----- Get instance of cxLib class from pass-through data handle
    #      created in cxLib.__init__() via FFI function, new_handle().
    cxlib = _ffi.from_handle(handle)
    if cxlib.verbose > 0:
        print(
            f"===== Begin prjDataReadFcnP(\n\t"
            f"state=[{state}]\n\tpData=[{handle}]\n\tuser_data=[{cxlib}]\n)\n"
        )

    # ===== Get data from the state =====#
    # ----- Number of Items in PRJ.
    cxlib.nContaminants = _lib.cxiGetNumCtms(state)
    cxlib.nZones = _lib.cxiGetNumZones(state)
    cxlib.nPaths = _lib.cxiGetNumPaths(state)
    cxlib.nAhs = _lib.cxiGetNumAHS(state)
    cxlib.nDuctJunctions = _lib.cxiGetNumJunctions(state)
    cxlib.nDuctTerminals = _lib.cxiGetNumTerminals(state)
    cxlib.nDuctLeaks = _lib.cxiGetNumLeaks(state)
    cxlib.nInputControls = _lib.cxiGetNumInputCtrlNodes(state)
    cxlib.nOutputControls = _lib.cxiGetNumOutputCtrlNodes(state)

    if cxlib.verbose > 0:
        print(
            f"nContaminants={cxlib.nContaminants}\n"
            f"nZones={cxlib.nZones}\nnPaths={cxlib.nPaths}"
        )
        print(f"nAhs={cxlib.nAhs}")
        print(
            f"nJunctions={cxlib.nDuctJunctions}\n"
            f"nTerminals={cxlib.nDuctTerminals}\nnLeaks={cxlib.nDuctLeaks}"
        )
        print(
            f"nInputControls={cxlib.nInputControls}\n"
            f"nOutputControls={cxlib.nOutputControls}"
        )

    # ===== Populate lists of building components from contamx-lib =====#
    # ----- Contaminants (0 -> nContaminants-1).
    for i in range(cxlib.nContaminants):
        name = cxlib._getCtmName(i)
        if (len(name) <= 0):
            print(f"ERROR: cxiGetCtmName({i})\n")
        else:
            cxlib.contaminants.append(name)
    if (cxlib.verbose == 1):
        print(f"\ncontaminants = {cxlib.contaminants}")

    # ----- Zones (1->nZones).
    for i in range(cxlib.nZones):
        zone = cxlib._getZoneInfo(i + 1)
        cxlib.zones.append(zone)
    if cxlib.verbose == 1:
        print(f"\nzones = {cxlib.zones}")
    elif cxlib.verbose == 2:
        print("\nzones")
        for zone in cxlib.zones:
            print(f"{zone}")

    # ----- Paths (1->nPaths).
    for i in range(cxlib.nPaths):
        path = cxlib._getPathInfo(i + 1)
        cxlib.paths.append(path)

        # Envelope Paths
        if path.envIndex > 0:
            cxlib.envPaths.append(path)
    cxlib.nEnvPaths = len(cxlib.envPaths)

    if cxlib.verbose == 1:
        print(f"\npaths = {cxlib.paths}")
        print(f"\n{cxlib.nEnvPaths} envPaths = {cxlib.envPaths}")
    elif cxlib.verbose == 2:
        print("\npaths")
        for path in cxlib.paths:
            print(f"{path}")
        print(f"{cxlib.nEnvPaths} envPaths (pathNr, envIndex)")
        for path in cxlib.envPaths:
            print(f"({path.nr}, {path.envIndex})", end=" ")
        print("\n")

    # ----- AHS (1->nAhs).
    for i in range(cxlib.nAhs):
        ahs = cxlib._getAhsInfo(i + 1)
        cxlib.AHSs.append(ahs)

    # Set lists of AHS supplies and returns.
    AHS_S = int("0x0008", 16)   # system supply or return path

    if (len(cxlib.paths) > 0):
        for path in cxlib.paths:
            if ((path.ahs_nr > 0) and (path.flags & AHS_S)):
                ahs = cxlib.AHSs[path.ahs_nr - 1]
                if (path.from_zone == ahs.zone_sup):
                    ahs.supply_points.append(path)
                elif (path.to_zone == ahs.zone_ret):
                    ahs.return_points.append(path)

    if (cxlib.verbose == 1):
        print(f"\nAHSs = {cxlib.AHSs}")
    elif (cxlib.verbose == 2):
        for ahs in cxlib.AHSs:
            ahs.diagram()

    # ----- Junctions (1->nDuctJunctions).
    for i in range(cxlib.nDuctJunctions):
        junction = cxlib._getJunctionInfo(i + 1)
        cxlib.ductJunctions.append(junction)

    if (cxlib.verbose == 1):
        print(f"\nductJunctions = {cxlib.ductJunctions}")
    if (cxlib.verbose == 2):
        print("\nductJunctions")
        for junction in cxlib.ductJunctions:
            print(f"{junction}")

    # ----- Terminals (1->nDuctTerminals).
    for i in range(cxlib.nDuctTerminals):
        terminal = cxlib._getTerminalInfo(i + 1)
        cxlib.ductTerminals.append(terminal)

        # Envelope Terminals
        if (terminal.envIndex > 0):
            cxlib.envTerminals.append(terminal)
    cxlib.nEnvTerminals = len(cxlib.envTerminals)

    if (cxlib.verbose == 1):
        print(f"\nductTerminals = {cxlib.ductTerminals}")
    elif (cxlib.verbose == 2):
        print("\nductTerminals")
        for terminal in cxlib.ductTerminals:
            print(f"{terminal}")
    if (cxlib.verbose > 0):
        print(f"{cxlib.nEnvTerminals} envTerminals (termNr, envIndex)")
        for term in cxlib.envTerminals:
            print(f"({term.nr}, {term.envIndex})", end=" ")
        print("\n")

    # ----- Duct Leaks (1->nDuctLeaks).
    for i in range(cxlib.nDuctLeaks):
        terminal = cxlib._getLeakInfo(i + 1)
        cxlib.ductLeaks.append(terminal)

        # NOTE: Envelope Duct Leakages are currently not implemented

    if (cxlib.verbose == 1):
        print(f"\nductLeaks = {cxlib.ductLeaks}")
    elif (cxlib.verbose == 2):
        print("\nductLeaks")
        for terminal in cxlib.ductLeaks:
            print(f"{terminal}")

    # ----- Input controls.
    for i in range(cxlib.nInputControls):
        ctrl = cxlib._getInputControlInfo(i + 1)
        cxlib.inputControls.append(ctrl)
    if (cxlib.verbose == 1):
        print(f"\ninputControls = {cxlib.inputControls}")
    elif (cxlib.verbose == 2):
        print("\ninputControls")
        for ctrl in cxlib.inputControls:
            print(f"{ctrl}")

    # ----- Output controls.
    for i in range(cxlib.nOutputControls):
        ctrl = cxlib._getOutputControlInfo(i + 1)
        cxlib.outputControls.append(ctrl)
    if (cxlib.verbose == 1):
        print(f"\noutputControls = {cxlib.outputControls}")
    elif (cxlib.verbose == 2):
        print("\noutputControls")
        for ctrl in cxlib.outputControls:
            print(f"{ctrl}")

    # ----- Set Weather Initialization Function.
    if (cxlib.wth_init_function is not None):
        cxlib.wth_init_function(cxlib)

    if (cxlib.verbose > 0):
        print("\n===== End prjDataReadyFcnP() =====\n")
