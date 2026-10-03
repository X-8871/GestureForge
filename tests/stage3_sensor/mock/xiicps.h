#ifndef MOCK_XIICPS_H
#define MOCK_XIICPS_H
#include "xil_types.h"
#define XST_SUCCESS 0
#define XST_FAILURE 1
typedef struct { UINTPTR BaseAddress; } XIicPs_Config;
typedef struct { int dummy; } XIicPs;
#ifdef SDT
XIicPs_Config *XIicPs_LookupConfig(UINTPTR);
#else
XIicPs_Config *XIicPs_LookupConfig(u16);
#endif
int XIicPs_CfgInitialize(XIicPs *, XIicPs_Config *, u32);
int XIicPs_SetSClk(XIicPs *, u32);
int XIicPs_BusIsBusy(XIicPs *);
int XIicPs_MasterSendPolled(XIicPs *, u8 *, int, u16);
int XIicPs_MasterRecvPolled(XIicPs *, u8 *, int, u16);
#endif
