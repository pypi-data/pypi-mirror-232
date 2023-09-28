NIST Developer Notes
====================

Calling hierarchy within :py:func:`contamxpy.cxLib.setupSimulation()`:

.. code:: c

    struct ContamXState * cxs  

    SetupSimulation(cxs, projectPath)
    {
        contamx(cxs) {
            prj_read(cxs, prjPath)
            sim_data(cxs) {
                cxs->nafnd = afnd_set(cxs)
                cxs->nafpt = afpt_set(cxs)
            }
            setup_cosim_lists(cxs)
        }
    }

Number of items in the `state`/PRJ
----------------------------------

+ `nzone` => Includes "standard" zones and Implicit Simple AHS (SAHS) Supply and Return zones. These items are referenced by `cxs->ZoneList[]`.
+ `npath` => Includes "standard" paths, SAHS Inlets and Outlets, and Implicit SAHS paths (OA -> Supply, Return -> Supply, Return -> Exhaust). These items are referenced by `cxs->PatList[]`
+ `nduct` => Includes all duct segments in the PRJ. These items are referenced in `cxs->DcList[]`.
+ `njct` => Includes "standard" junctions and terminals referenced by `cxs->JctList[]`

Lists created by ContamX for simulation:  
----------------------------------------

The following lists are created by calls from `sim_data()`:  

+ **afnd0** => List of `AF_NODE`\ s created by ContamX in `afnd_set()`.  
  
    Includes `cxs->nafnd` items set upon return from `afnd_set()`:

    - `nzone` items from `cxs->ZoneList[]`
    - `njct` items from `cxs->JctList[]`
    - `cxs->pambt` is the last node in the list which is also referenced by `cxs->ambt.pafn`.

+ **afpt0** => List of `AF_PATH`\ s created by ContamX in `afpt_set()`.

    Includes `cxs->nafpt` items set upon return from `afpt_set()`:

    - `npath` items from `cxs->PathList[]`.
    - `nduct` items from `cxs->DcList[]`.
    - Each Terminal junction (`AF_NODE`\ s: junction -> to_zone).
    - Each duct Leak (`AF_NODE`\ s: junction -> containing_zone). `AF_PATH`\ s for Leaks are created in `afpt_set()` based on junction leakage area data field, `JCT_DSC->CA`.

Co-simulation lists created by ``contamx-lib``:  
-----------------------------------------------

**setup_cosim_lists**\ (ContamXState* cxs)

.. code:: c
    
    struct ContamXState {
        ...
        struct cosimState cosim
        {
            AF_NODE** cosim_zone_list;  // list of pointers to zones [1:cxs->nzone]
            AF_NODE** cosim_jct_list;   // list of pointers to junction nodes [1:cxs->njct]
            AF_PATH** cosim_path_list;  // list of pointers to path links [1:cxs->npath]
            AHS_DSC** cosim_ahs_list;   // list of pointers to Simple AHSs [1:cxs->nahs]
            AF_PATH** cosim_oap_list;   // list of pointers to AHS outdoor air path [1:cxs->nahs]
            AF_PATH** cosim_term_list;  // list of pointers to terminal links [1:cxs->cosim.num_cosim_terms]
            AF_PATH** cosim_leak_list;  // list of pointers to terminal links [1:cxs->cosim.num_cosim_leaks]
            CT_NODE** cosim_inode_list; // list of pointers to input control nodes [1:cxs->cosim.num_cosim_inodes]
            CT_NODE** cosim_onode_list; // list of pointers to output control nodes [1:cxs->cosim.num_cosim_onodes]

            // NOTE: these values are determined by setup_cosim_lists() function.
            IX num_cosim_inodes;    // number of input control nodes (CT_SET w/ names)
            IX num_cosim_onodes;    // number of output control nodes (CT_PAS w/ names)
            IX num_cosim_terms;     // number of terminals
            IX num_cosim_leaks;     // number of junction leaks
        }
    }
 
``contamx-lib`` Functions that Reference `AF_NODE`\ s
-----------------------------------------------------

`cxiSetZoneAddMass()`
~~~~~~~~~~~~~~~~~~~~~

This function currently only works for zones `1` to `cxs->nzone`, which includes Implicit SAHS zones. 

.. todo:: `cxiSetZoneAddMass()` will only work for zones having a non-zero mass.

.. code:: c
    
    IX cxiSetZoneAddMass(void* contamXState, IX zoneNumber, IX ctmNumber, R8 addMass)
    {
        double addMf = 0.0;
        struct AF_NODE *pn = cxs->cosim.cosim_zone_list[zoneNumber];
        if(pn->M > 0.0)
        {
            addMf = addMass / pn->M;
        }
        pn = cxs->cosim.cosim_zone_list[zoneNumber];
        pn->Mf[ctmNumber] += addMf;
    }

`cxiSetZoneTemperature()`
~~~~~~~~~~~~~~~~~~~~~~~~~

This function currently only works for zones `1` to `cxs->nzone`, which includes Implicit SAHS zones. 

.. code:: c

    IX cxiSetZoneTemperature(void* contamXState, IX zoneNumber, R8 temperature)
    {
        cxs->cosim.cosim_zone_list[zoneNumber]->T = temperature;
    }

`cxiSetJunctionTemperature()`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This function works for junctions `1` to `cxs->njct` which includes terminals. 

.. code:: c

    IX cxiSetJunctionTemperature(void* contamXState, IX jctNumber, R8 temperature)
    {
        cxs->cosim.cosim_jct_list[jctNumber]->T = temperature;
    }

TO DO
-----

.. todo:: 
    Add error handling.

.. todo:: 
    `relHt` of all AF_PATH items, i.e., Paths, DuctJunctions, and DuctTerminals, are 0.0. AF_PATH in ContamX does not include a relHt field. `relHt` is used to set the absolute coordinate `Z` which in turn is used to set relative node heights `Ht_m` and `Ht_n`. CHECK the ramifications of this for multiple levels. `Z` and other coordinates may not be relevant except for WPC-like API functions.

.. todo:: 
    Need to test and establish precedents between Control values determined in PRJ, cxiSetInputControlValue(), and cxiSetZoneTemperature(). Currently, an Input Control applied to the temperature of a zone will override a cxiSetZoneTemperature() for the timestep applied. Currently, it is best to utilize cxiSetZoneTemperature() to establish zone temperatures instead of applying controls to Tzone.

.. todo:: 
    Test errors, e.g., terminal number and leak number out of range in `getDuctTerminalFlow()` and `getDuctLeakFlow()`.
    
.. note:: 
    No wrapper is provided for cxiSetUseVolumeFlows(). This API function is specific to EnergyPlus.

