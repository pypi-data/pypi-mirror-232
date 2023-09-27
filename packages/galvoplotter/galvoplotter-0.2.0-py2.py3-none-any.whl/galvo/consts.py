listJumpTo = 0x8001
listEndOfList = 0x8002
listLaserOnPoint = 0x8003
listDelayTime = 0x8004
listMarkTo = 0x8005
listJumpSpeed = 0x8006
listLaserOnDelay = 0x8007
listLaserOffDelay = 0x8008
listMarkFreq = 0x800A
listMarkPowerRatio = 0x800B
listMarkSpeed = 0x800C
listJumpDelay = 0x800D
listPolygonDelay = 0x800F
listWritePort = 0x8011
listMarkCurrent = 0x8012
listMarkFreq2 = 0x8013
listFlyEnable = 0x801A
listQSwitchPeriod = 0x801B
listDirectLaserSwitch = 0x801C
listFlyDelay = 0x801D
listSetCo2FPK = 0x801E
listFlyWaitInput = 0x801F
listFiberOpenMO = 0x8021
listWaitForInput = 0x8022
listChangeMarkCount = 0x8023
listSetWeldPowerWave = 0x8024
listEnableWeldPowerWave = 0x8025
listFiberYLPMPulseWidth = 0x8026
listFlyEncoderCount = 0x8028
listSetDaZWord = 0x8029
listJptSetParam = 0x8050
listReadyMark = 0x8051

DisableLaser = 0x0002
EnableLaser = 0x0004
ExecuteList = 0x0005
SetPwmPulseWidth = 0x0006
GetVersion = 0x0007
GetSerialNo = 0x0009
GetListStatus = 0x000A
GetPositionXY = 0x000C
GotoXY = 0x000D
LaserSignalOff = 0x000E
LaserSignalOn = 0x000F
WriteCorLine = 0x0010
ResetList = 0x0012
RestartList = 0x0013
WriteCorTable = 0x0015
SetControlMode = 0x0016
SetDelayMode = 0x0017
SetMaxPolyDelay = 0x0018
SetEndOfList = 0x0019
SetFirstPulseKiller = 0x001A
SetLaserMode = 0x001B
SetTiming = 0x001C
SetStandby = 0x001D
SetPwmHalfPeriod = 0x001E
StopExecute = 0x001F
StopList = 0x0020
WritePort = 0x0021
WriteAnalogPort1 = 0x0022
WriteAnalogPort2 = 0x0023
WriteAnalogPortX = 0x0024
ReadPort = 0x0025
SetAxisMotionParam = 0x0026
SetAxisOriginParam = 0x0027
AxisGoOrigin = 0x0028
MoveAxisTo = 0x0029
GetAxisPos = 0x002A
GetFlyWaitCount = 0x002B
GetMarkCount = 0x002D
SetFpkParam2 = 0x002E
Fiber_SetMo = 0x0033  # open and close set by value
Fiber_GetStMO_AP = 0x0034
EnableZ = 0x003A
DisableZ = 0x0039
SetZData = 0x003B
SetSPISimmerCurrent = 0x003C
SetFpkParam = 0x0062
Reset = 0x0040
GetFlySpeed = 0x0038
FiberPulseWidth = 0x002F
FiberGetConfigExtend = 0x0030
InputPort = 0x0031  # ClearLockInputPort calls 0x04, then if EnableLockInputPort 0x02 else 0x01, GetLockInputPort
GetMarkTime = 0x0041
GetUserData = 0x0036
SetFlyRes = 0x0032

list_command_lookup = {
    0x8001: "listJumpTo",
    0x8002: "listEndOfList",
    0x8003: "listLaserOnPoint",
    0x8004: "listDelayTime",
    0x8005: "listMarkTo",
    0x8006: "listJumpSpeed",
    0x8007: "listLaserOnDelay",
    0x8008: "listLaserOffDelay",
    0x800A: "listMarkFreq",
    0x800B: "listMarkPowerRatio",
    0x800C: "listMarkSpeed",
    0x800D: "listJumpDelay",
    0x800F: "listPolygonDelay",
    0x8011: "listWritePort",
    0x8012: "listMarkCurrent",
    0x8013: "listMarkFreq2",
    0x801A: "listFlyEnable",
    0x801B: "listQSwitchPeriod",
    0x801C: "listDirectLaserSwitch",
    0x801D: "listFlyDelay",
    0x801E: "listSetCo2FPK",
    0x801F: "listFlyWaitInput",
    0x8021: "listFiberOpenMO",
    0x8022: "listWaitForInput",
    0x8023: "listChangeMarkCount",
    0x8024: "listSetWeldPowerWave",
    0x8025: "listEnableWeldPowerWave",
    0x8026: "listFiberYLPMPulseWidth",
    0x8028: "listFlyEncoderCount",
    0x8029: "listSetDaZWord",
    0x8050: "listJptSetParam",
    0x8051: "listReadyMark",
}

single_command_lookup = {
    0x0002: "DisableLaser",
    0x0004: "EnableLaser",
    0x0005: "ExecuteList",
    0x0006: "SetPwmPulseWidth",
    0x0007: "GetVersion",
    0x0009: "GetSerialNo",
    0x000A: "GetListStatus",
    0x000C: "GetPositionXY",
    0x000D: "GotoXY",
    0x000E: "LaserSignalOff",
    0x000F: "LaserSignalOn",
    0x0010: "WriteCorLine",
    0x0012: "ResetList",
    0x0013: "RestartList",
    0x0015: "WriteCorTable",
    0x0016: "SetControlMode",
    0x0017: "SetDelayMode",
    0x0018: "SetMaxPolyDelay",
    0x0019: "SetEndOfList",
    0x001A: "SetFirstPulseKiller",
    0x001B: "SetLaserMode",
    0x001C: "SetTiming",
    0x001D: "SetStandby",
    0x001E: "SetPwmHalfPeriod",
    0x001F: "StopExecute",
    0x0020: "StopList",
    0x0021: "WritePort",
    0x0022: "WriteAnalogPort1",
    0x0023: "WriteAnalogPort2",
    0x0024: "WriteAnalogPortX",
    0x0025: "ReadPort",
    0x0026: "SetAxisMotionParam",
    0x0027: "SetAxisOriginParam",
    0x0028: "AxisGoOrigin",
    0x0029: "MoveAxisTo",
    0x002A: "GetAxisPos",
    0x002B: "GetFlyWaitCount",
    0x002D: "GetMarkCount",
    0x002E: "SetFpkParam2",
    0x0033: "Fiber_SetMo",
    0x0034: "Fiber_GetStMO_AP",
    0x003A: "EnableZ",
    0x0039: "DisableZ",
    0x003B: "SetZData",
    0x003C: "SetSPISimmerCurrent",
    0x0062: "SetFpkParam",
    0x0040: "Reset",
    0x0038: "GetFlySpeed",
    0x002F: "FiberPulseWidth",
    0x0030: "FiberGetConfigExtend",
    0x0031: "InputPort",
    0x0041: "GetMarkTime",
    0x0036: "GetUserData",
    0x0032: "SetFlyRes",
}


def _bytes_to_words(r):
    b0 = r[1] << 8 | r[0]
    b1 = r[3] << 8 | r[2]
    b2 = r[5] << 8 | r[4]
    b3 = r[7] << 8 | r[6]
    return b0, b1, b2, b3
