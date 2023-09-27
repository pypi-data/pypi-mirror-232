#ifndef _TAGSonar24H8
#define _TAGSonar24H8

#include "apriltag.h"

#ifdef __cplusplus
extern "C" {
#endif

apriltag_family_t *AcTag24h8_create();
void AcTag24h8_destroy(apriltag_family_t *tf);

#ifdef __cplusplus
}
#endif

#endif
