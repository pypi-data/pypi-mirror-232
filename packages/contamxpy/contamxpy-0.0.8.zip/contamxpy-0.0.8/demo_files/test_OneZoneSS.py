from contamxpy import cxLib
import cxResults as cxr
import os
import sys
from optparse import OptionParser

# ============================================================================ setWthCtmInit() =====
# Set the initial conditions for the SetAmbt API test.
# This function is set as a parameter to instantiation of cxLib
#   to be called by the contamxpy.prjDataReadyFcnP() in order to set 
#   ambient boundary conditions for steady-state initialization.
# NOTE: The parameter {cxl as cxLib} is passed through contamx-lib to 
#   contamxpy.prjDataReadyFcnP() which in turn passes it to this function
#   to distinguish the instance of cxLib to be used.
#


def setWthCtmInit( cxl ):
    cxl.setAmbtPressure(101325.0)       # Pa
    cxl.setAmbtWindSpeed(7.397)         # m/s
    cxl.setAmbtWindDirection(270)       # deg
    cxl.setAmbtMassFraction(0, 0.0023254)  # 0.0023254 kg/kg = 2800 mg/m3
    cxl.setAmbtTemperature(293.15)      # K


# ===================================================================================== main() =====


def main():
    # ----- Manage option parser
    parser = OptionParser(usage="%prog [options] arg1\n\targ1=PRJ filename\n")
    parser.set_defaults(verbose=0)
    parser.add_option("-v", "--verbose", action="store", dest="verbose", type="int", default=0,
                      help="define verbose output level: 0=Min, 1=Medium, 2=Maximum.")
    (options, args) = parser.parse_args()

    # ----- Process command line options -v
    verbose = options.verbose

    if len(args) != 1:
        parser.error("Need one argument:\n  arg1 = PRJ file.")
        return
    else:
        # Get PRJ file name
        prjPath  = args[0]

    if ( not os.path.exists(prjPath) ):
        print("ERROR: PRJ file not found.")
        return

    msg_cmd = "Running test_OneZoneSS.py: arg1 = " + args[0] + " " + str(options)
    print(msg_cmd, "\n")

    if verbose > 1:
        print(f"cxLib attributes =>\n{chr(10).join(map(str, dir(cxLib)))}\n")

    # ----- Initialize contamx-lib object w/ wp_mode and cb_option.
    #      wp_mode = 0 => use wind pressure profiles, WTH and CTM files or associated API calls.
    #      cb_option = True => set callback function to get PRJ INFO from the ContamXState.
    myPrj = cxLib(prjPath, 0, True, setWthCtmInit)

    myPrj.setVerbosity(verbose)
    if verbose > 1:
        print(f"BEFORE setupSimulation()\n\tnCtms={myPrj.nContaminants}\n\tnZones={myPrj.nZones}\n\tnPaths={myPrj.nPaths}\n" )

    # ----- Query State for Version info
    verStr = myPrj.getVersion()
    if verbose >= 0:
        print(f"getVersion() returned {verStr}.")

    # ----------------------------------------------------------------
    # ------------------------------------ Initialize Simulation -----
    # ----------------------------------------------------------------
    # Returns 1 if not ok, else 0
    sim_not_ok = myPrj.setupSimulation(1)
    if (sim_not_ok > 0):
        print(f"ABORT - sim_not_ok Returned by setupSimulation() = {sim_not_ok}")
        print(" => invalid simulation parameters for co-simulation.")
        myPrj.endSimulation()
        return

    # ----- Get simulation run info
    dayStart = myPrj.getSimStartDate()
    dayEnd   = myPrj.getSimEndDate()
    secStart = myPrj.getSimStartTime()
    secEnd   = myPrj.getSimEndTime()
    tStep    = myPrj.getSimTimeStep()

    buildingVolume = 0.0
    for zone in myPrj.zones:
        buildingVolume += zone.volume
    buildingMass = 1.2041 * buildingVolume

    # ----- Calculate the simulation duration in seconds and total time steps
    simBegin = (dayStart - 1) * 86400 + secStart
    simEnd = (dayEnd - 1) * 86400 + secEnd
    if (simBegin <= simEnd):
        simDuration = simEnd - simBegin
    else:
        simDuration = 365 * 86400 - simEnd + simBegin
    numTimeSteps = 0
    if (simDuration != 0):
        numTimeSteps = int(simDuration / tStep)
        print(f"ABORT - PRJ settings => Transient simulation w/ {numTimeSteps} time steps.")
        return
    else:
        print("PRJ settings => Steady state simulation.")

    # ----- Get the current date/time after initial steady state simulation
    currentDate = myPrj.getCurrentDayOfYear()
    currentTime = myPrj.getCurrentTimeInSec()
    if verbose > 0:
        print(f"Sim days = {dayStart}:{dayEnd}")
        print(f"Sim times = {secStart}:{secEnd}")
        print(f"Sim time step = {tStep}")
        print(f"date = {currentDate} time = {currentTime}")

    # ----- Output SS results.
    cxr.printZoneMf(myPrj, currentDate, currentTime, myPrj.nZones, myPrj.nContaminants)
    cxr.writeAirflowRates(sys.stdout, True, myPrj, currentDate, currentTime)
    cxr.writeAirflowRates(sys.stdout, False, myPrj, currentDate, currentTime)
    
    # Calculate building Air Change Rate
    sumAbsFlows = 0.0
    for path in myPrj.paths:
        if path.envIndex > 0:
            flows = myPrj.getPathFlow(path.nr)
            netPathFlow = flows[0] + flows[1]
            sumAbsFlows += abs(netPathFlow)
    buildingAcr = 0.5 * 3600. * sumAbsFlows / buildingMass
    if verbose > 0:
        print(f"sumAbsFlows = {sumAbsFlows} [kg/s]")
        print(f"buildingVolume = {buildingVolume} [m3]")
        print(f"buildingMass = {buildingMass} [kg]")

    print(f"buildingAcr = {buildingAcr} [1/h]")
    print("Performed SS simulation.")
    myPrj.endSimulation()

# --- End main() ---#


if __name__ == "__main__":
    main()
