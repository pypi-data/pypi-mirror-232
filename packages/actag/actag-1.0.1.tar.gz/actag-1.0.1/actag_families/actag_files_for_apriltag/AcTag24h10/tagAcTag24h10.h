#ifndef _TAGSonar24H10
#define _TAGSonar24H10

#include "apriltag.h"

#ifdef __cplusplus
extern "C" {
#endif

apriltag_family_t *AcTag24h10_create();
void AcTag24h10_destroy(apriltag_family_t *tf);

#ifdef __cplusplus
}
#endif

#endif
