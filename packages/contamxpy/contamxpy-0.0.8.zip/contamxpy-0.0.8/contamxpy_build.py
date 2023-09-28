from __future__ import annotations

# platform.system() => Linux, Windows, Darwin (Mac)
import platform

# Using the "out-of-line", "API mode"
from cffi import FFI


CDEF = '''\
    // see types.h
    typedef int32_t IX;
    typedef float R4;
    typedef double R8;
    typedef uint16_t U2;

    typedef struct zone_cosim_dsc
    {
        IX nr;
        U2 flags;
        float Vol;
        char level_name[48]; // #define NAMEFIELDLEN 48
        IX level_nr;
        char name[48];       // #define NAMEFIELDLEN 48
    } ZONE_COSIM_DSC;

    typedef struct path_cosim_dsc
    {
        IX nr;
        U2 flags;
        IX from_zone;
        IX to_zone;
        IX ahs_nr;
        R4 X;
        R4 Y;
        R4 Z;
        IX envIndex;
    } PATH_COSIM_DSC;

    typedef struct jct_cosim_dsc
    {
        IX nr;
        U2 flags;
        IX containing_zone;
        IX envIndex;
    } JCT_COSIM_DSC;

    // Also used for Duct Leaks associated with Duct Junctions
    typedef struct term_cosim_dsc
    {
        IX nr;
        U2 flags;
        R4 X;
        R4 Y;
        R4 Z;
        R4 relHt;
        IX to_zone;
        IX envIndex;
    } TERM_COSIM_DSC;

    typedef struct control_cosim_dsc
    {
        IX nr;
        char name[48];   // #define NAMEFIELDLEN 48
    } CONTROL_COSIM_DSC;

    typedef struct ahs_cosim_dsc
    {
        IX nr;
        char name[48];  // #define NAMEFIELDLEN 48
        IX zone_ret;
        IX zone_sup;
        IX path_rec;
        IX path_oa;
        IX path_exh;
    } AHS_COSIM_DSC;

    // Callback function - extern => to be python function defined in contamxpy.py.
    extern "Python" void prjDataReadyFcnP(void *, void *);
    // {prjDataReadyFcnP} will set to function defined in {cxLib} class of {contamxpy}.
    void cxiRegisterCallback_PrjDataReady( void* contamXState, void* pUserData, void ( *prjDataReadyFcnP )( void*, void* ) );

    void* cxiGetContamState();
    void cxiSetWindPressureMode(void* contamXState, IX useWP);
    IX cxiSetupSimulation(void* contamXState, char* projectPath, IX useCosim);
    IX cxiGetVersion(void* contamXState, char* strVersion);

    IX cxiGetSimulationStartDate(void* contamXState);
    IX cxiGetSimulationStartTime(void* contamXState);
    IX cxiGetSimulationEndDate(void* contamXState);
    IX cxiGetSimulationEndTime(void* contamXState);
    IX cxiGetSimulationTimeStep(void* contamXState);
    IX cxiGetCurrentDate(void* contamXState);
    IX cxiGetCurrentTime(void* contamXState);
    void cxiDoCoSimStep(void* contamXState, IX stepForward);
    void cxiEndSimulation(void* contamXState);

    // These functions will be utilized within the callback function, prjDataReadyFcnP(),
    //   to populate class variables for access by the calling/driver
    //   program which imports {contamxpy}
    IX cxiGetNumCtms(void* contamXState);
    IX cxiGetCtmName(void* contamXState, IX ctmNumber, char* strName);
    IX cxiGetNumZones(void* contamXState);
    IX cxiGetZoneInfo(void* contamXState, IX zoneNumber, ZONE_COSIM_DSC* pZoneInfo);
    IX cxiGetNumPaths(void* contamXState);
    IX cxiGetPathInfo(void* contamXState, IX pathNumber, PATH_COSIM_DSC* pPath);
    IX cxiGetNumAHS(void* contamXState);
    IX cxiGetAhsInfo(void* contamXState, IX ahsNumber, AHS_COSIM_DSC* pAhsInfo);
    IX cxiGetAHSNumber(void* contamXState, const char* ahsName, IX* pAhsNumber);
    IX cxiGetNumTerminals(void* contamXState);
    IX cxiGetTermInfo(void* contamXState, IX termNumber, TERM_COSIM_DSC* pTerm);
    IX cxiGetNumJunctions(void* contamXState);
    IX cxiGetJunctionInfo(void* contamXState, IX jctNumber, JCT_COSIM_DSC* pJct);
    IX cxiGetNumLeaks(void* contamXState);
    IX cxiGetLeakInfo(void* contamXState, IX leakNumber, TERM_COSIM_DSC* pLeak);
    IX cxiGetNumInputCtrlNodes(void* contamXState);
    IX cxiGetInputControlInfo(void* contamXState, IX inputControlIndex, CONTROL_COSIM_DSC* pControl);
    IX cxiGetNumOutputCtrlNodes(void* contamXState);
    IX cxiGetOutputControlInfo(void* contamXState, IX outputControlIndex, CONTROL_COSIM_DSC* pControl);

    // Set Ambient
    IX cxiSetAmbtTemperature(void* contamXState, R4 ambtTemp);
    IX cxiSetAmbtPressure(void* contamXState, R4 ambtPres);
    IX cxiSetAmbtWndSpd(void* contamXState, R4 wndSpd);
    IX cxiSetAmbtWndDir(void* contamXState, R4 wndDir);
    IX cxiSetAmbtMassFraction(void* contamXState, IX ctmNumber, R8 Mf);
    IX cxiSetEnvelopeWP(void* contamXState, IX envIndex, R4 wP);
    IX cxiSetEnvelopeMF(void* contamXState, IX envIndex, IX ctmNumber, R8 Mf);

    // Set Other
    IX cxiSetZoneTemperature(void* contamXState, IX zoneNumber, R8 temperature);
    IX cxiSetZoneAddMass(void* contamXState, IX zoneNumber, IX ctmNumber, R8 addMass);
    IX cxiSetJunctionTemperature(void* contamXState, IX jctNumber, R8 temperature);
    IX cxiSetSupplyReturnPathFlow(void* contamXState, IX pathNumber, R4 flow);
    IX cxiSetAHSPercentOA(void* contamXState, IX ahsNumber, R4 OAValue);

    // Controls
    IX cxiSetInputControlValue(void* contamXState, IX inputCtrlNumber, R4 ctrlValue);
    IX cxiGetOutputControlValue(void* contamXState, IX outputCtrlNumber, R4* pCtrlValue);

    // Results
    IX cxiGetZoneMF(void* contamXState, IX zoneNumber, IX ctmNumber, R8* pMassFraction);
    IX cxiGetEnvelopeExfil(void* contamXState, IX envIndex, IX ctmNumber, R8* pMass);
    IX cxiGetPathFlows(void* contamXState, IX pathNumber, R8* pFlow0, R8* pFlow1);
    IX cxiGetTermFlow(void* contamXState, IX termNumber, R8* pFlow);
    IX cxiGetLeakFlow(void* contamXState, IX leakNumber, R8* pFlow);

    //=========================================================== TODO ================
    void cxiSetErrorFunction(void* contamXState, void (*errorAuxFcnP)(void *cxs,const char* const headerStr, char* const messageStr, int* const nonFatalErrorCt));
      IX cxiSetAmbtHumRatio(void* contamXState, R4 humRatio);
    //IX cxiGetZoneNumber(void* contamXState, const char* zoneName, IX zoneLevelNumber, IX* pZoneNumber);
    //IX cxiGetZoneVolume(void* contamXState, IX zoneNumber, R4 *pVolume);
    //IX cxiSetZoneHumRatio(void* contamXState, IX zoneNumber, R8 humRatio);


    // Duct Leakage
    ////IX cxiGetLeakNumber(void* contamXState, IX jctNumber, IX* pLeakNumber);
'''

SRC = '''\
    #include "include//contam-x-cosim.h"
'''

ffibuilder = FFI()
ffibuilder.cdef(CDEF)

strPlatform = platform.system()
print("Platform = ", strPlatform)

if strPlatform == "Windows":
    ffibuilder.set_source(
        "_contamxpy", SRC,
        include_dirs=['.', 'include'],  # C header files for contam-x-lib
        libraries=['contamx-lib'],     # Library to link with (.lib, .dll)
    )
else:
    ffibuilder.set_source(
        "_contamxpy", SRC,
        include_dirs=['.', 'include'],       # C header files for contam-x-lib
        extra_objects=['libcontamx-lib.a'],  # static shared object
    )

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
