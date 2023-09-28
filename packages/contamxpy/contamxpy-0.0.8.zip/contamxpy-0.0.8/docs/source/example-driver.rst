Example Driver Programs
=======================

Several driver programs provide examples of the main functionality of the `contamxpy.py` module. Some are tailored to specific PRJ files in order to apply boundary conditions associated with those PRJs. The cases are described below, and the code is provided in the `DriverPrograms`_ section below. These drivers also import the `cxRunSim.py`_ and `cxResults.py`_ modules to obtain and output results to text files.

WTH and CTM-like API Cases
--------------------------

These cases can be run via the `test_OneZoneWthCtm.py` driver module and will apply corresponding boundary conditions based on the PRJ file name provided on the command line. Each of these "-UseApi" PRJs have a corresponding non-API version to which they can be compared below.

Note: The `--verbose=2` command line option will provide detailed information related to the contents of the PRJ file as obtained via :py:class:`contamxpy.cxLib`, and `> out.txt` redirects the output to a text file that can be viewed via a text editor.

* test_OneZoneWthCtm-UseApi.prj
* test_OneZoneWthCtmStack-UseApi.prj
* valThreeZonesWthCtm-UseApi.prj
* testGetPrjInfo.prj 
  
  This is a generic test case to demonstrate all API functions that are available for obtaining information about the contents of the PRJ that are relevant to utilizing the API via driver modules. Run this case with `--verbose=2` to show all possible PRJ info available via  :py:class:`contamxpy.cxLib`. Further, this case also includes Simple AHSs and Controls for which the `test_OneZoneWthCtm.py` module includes inputs to demonstrate setting AHS flows and outdoor air fraction and setting Input Control values.


Command line:

    ``test_OneZoneWthCtm.py <PRJ File Name> --verbose=2 > out.txt``

WTH and CTM-like non-API Cases
------------------------------

These cases are fully contained PRJ files that include references to WTH and CTM files within them. They can be run via *ContamW*, *ContamX*, or the generic driver program `test_cxcffi.py`_. The driver program will simply run the PRJ through all of its time steps and output zone mass fractions to a text file along with other CONTAM-generated results files.

Command line:

    ``test_cxcffi.py <PRJ File Path>``

* test_OneZoneWthCtm.prj

  - test_OneZoneWthCtm.wth
  - test_OneZoneWthCtm.ctm

* test_OneZoneWthCtmStack.prj

  - test_OneZoneWthCtmStack.wth
  - test_OneZoneWthCtm.ctm

* valThreeZonesWthCtm.prj

  - valThreeZonesWthCtm.wth
  - valThreeZonesWthCtm.ctm

WPC-like API Cases
------------------

This case can be run via the `test_OneFloorWpcAddMf.py`_ driver module and will apply boundary conditions similar to those provided via a WPC file. The corresponding non-API version should provide the same results as the API version.

Command line:

    ``test_OneFloorWpcAddMf.py test_OneFloorWpcAddMf-UseApi.prj``

Thread-safe Driver
------------------

`contamxpy` is thread safe, and the `test_Multirun.py`_ driver demonstrates this capability by running multiple PRJ files provided in a list file using the Python `threading` module. **NOTE**: At the time of this release, `contamxpy` cannot be used with Python's multiprocessing capabilities due to pickling limitations of CFFI-based modules.
 
Command line:

    ``test_MultiRun.py prjFile.lst -m1``

Steady-State Case
-----------------

While ``contamx-lib`` was originally developed to perform co-simulation for transient simulations, it can also be used to run PRJ files configured for steady-state airflow and/or contaminant analysis. This case can be run with the `test_OneZoneSS.py`_ example driver program.
 
Command line:

    ``test_OneZoneSS.py test_OneZoneSS-UseApi.prj``

**NOTE:** *test_OneZoneSS-UseApi-BAD.prj* is provided to demonstrate a PRJ that has incorrect simulation parameters that ``contamx-lib`` should prevent from being executed. It is defined to perform a cyclic simulation.

There are several non-API versions with which this test can be compared. These are listed below with associated WTH and CTM files.

* test_OneZoneSS.prj - Steady-state airflow and contaminant transport simulation.
* test_OneZoneSS-Transient.prj - Equivalent transient simulation using WTH and CTM files.

    + test_OneZoneSS-Transient.wth
    + test_OneZoneSS-Transient.ctm

.. _DriverPrograms:

Driver Programs
---------------

.. _test_OneZoneWthCtm:

test_OneZoneWthCtm.py
~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../demo_files/test_OneZoneWthCtm.py

.. _test_cxcffi.py:

test_cxcffi.py
~~~~~~~~~~~~~~

.. literalinclude:: ../../demo_files/test_cxcffi.py

.. _test_OneFloorWpcAddMf.py:

test_OneFloorWpcAddMf.py
~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../demo_files/test_OneFloorWpcAddMf.py

.. _test_MultiRun.py:

test_MultiRun.py
~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../demo_files/test_MultiRun.py

.. _test_OneZoneSS.py:

test_OneZoneSS.py
~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../demo_files/test_OneZoneSS.py

.. _cxRunSim.py:

cxRunSim.py
~~~~~~~~~~~~

.. literalinclude:: ../../demo_files/cxRunSim.py

.. _cxResults.py:

cxResults.py
~~~~~~~~~~~~

.. literalinclude:: ../../demo_files/cxResults.py

