#ifndef _TAGSonar24H6
#define _TAGSonar24H6

#include "apriltag.h"

#ifdef __cplusplus
extern "C" {
#endif

apriltag_family_t *AcTag24h6_create();
void AcTag24h6_destroy(apriltag_family_t *tf);

#ifdef __cplusplus
}
#endif

#endif
