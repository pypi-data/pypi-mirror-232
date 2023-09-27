#ifndef _TAGSonar24H4
#define _TAGSonar24H4

#include "apriltag.h"

#ifdef __cplusplus
extern "C" {
#endif

apriltag_family_t *AcTag24h4_create();
void AcTag24h4_destroy(apriltag_family_t *tf);

#ifdef __cplusplus
}
#endif

#endif
