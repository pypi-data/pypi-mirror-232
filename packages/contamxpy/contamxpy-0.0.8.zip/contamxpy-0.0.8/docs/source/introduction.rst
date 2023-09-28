Introduction
============

This is the documentation for the :py:mod:`contamxpy` module which provides Python bindings to the *ContamX* API ``contamx-lib``.  

The :py:mod:`contamxpy` module consists mainly of the :py:class:`contamxpy.cxLib` class that provides the wrapper to ``contamx-lib``. This documentation provides the details of the Python API which can be used to run CONTAM simulations on existing CONTAM projects, i.e., *.prj* files. ``contamx-lib`` provides a thread-safe API to the CONTAM simulation engine, ContamX. A simulation *state* is associated with each instance of :py:class:`contamxpy.cxLib` upon instantiation for a particular PRJ file.

To utilize :py:mod:`contamxpy` :  
--------------------------------

Install :py:mod:`contamxpy` from PyPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    pip install contamxpy

Import `cxLib` wrapper class into user-defined driver module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from contamxpy import cxLib

.. note:: 

    ``contamx-lib`` will allow for co-simulation to be performed according to the following:

    * steady airflow with no contaminants
    * steady airflow with steady or transient contaminants
    * transient airflow with transient contaminants
    * Only the Default Solver (Implicit Euler) is allowed for contaminant calculations

    Co-simulation is not allowed for the following:

    * Airflow simulations: Duct Balance, Building Airflow Test, or Building Pressurization Test
    * Contaminant simulations: Cyclic, Short Time Step, or CVODE
    * CFD analysis

.. seealso:: 

    :doc:`/example-driver`
