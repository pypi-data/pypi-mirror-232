#include <stdlib.h>
#include "tagAcTag24h10.h"

static uint64_t codedata[7] = {
   0x0000000000d35f2aUL,
   0x00000000006264efUL,
   0x00000000009714ffUL,
   0x00000000003d9e3eUL,
   0x000000000011acecUL,
   0x00000000000cab28UL,
   0x000000000003b65aUL,
};
apriltag_family_t *AcTag24h10_create()
{
   apriltag_family_t *tf = calloc(1, sizeof(apriltag_family_t));
   tf->name = strdup("AcTag24h10");
   tf->h = 10;
   tf->ncodes = 7;
   tf->codes = codedata;
   tf->nbits = 24;
   tf->bit_x = calloc(24, sizeof(uint32_t));
   tf->bit_y = calloc(24, sizeof(uint32_t));
   tf->bit_x[0] = -2;
   tf->bit_y[0] = -2;
   tf->bit_x[1] = -1;
   tf->bit_y[1] = -2;
   tf->bit_x[2] = 0;
   tf->bit_y[2] = -2;
   tf->bit_x[3] = 1;
   tf->bit_y[3] = -2;
   tf->bit_x[4] = 2;
   tf->bit_y[4] = -2;
   tf->bit_x[5] = 3;
   tf->bit_y[5] = -2;
   tf->bit_x[6] = 4;
   tf->bit_y[6] = -2;
   tf->bit_x[7] = 4;
   tf->bit_y[7] = -1;
   tf->bit_x[8] = 4;
   tf->bit_y[8] = 0;
   tf->bit_x[9] = 4;
   tf->bit_y[9] = 1;
   tf->bit_x[10] = 4;
   tf->bit_y[10] = 2;
   tf->bit_x[11] = 4;
   tf->bit_y[11] = 3;
   tf->bit_x[12] = 4;
   tf->bit_y[12] = 4;
   tf->bit_x[13] = 3;
   tf->bit_y[13] = 4;
   tf->bit_x[14] = 2;
   tf->bit_y[14] = 4;
   tf->bit_x[15] = 1;
   tf->bit_y[15] = 4;
   tf->bit_x[16] = 0;
   tf->bit_y[16] = 4;
   tf->bit_x[17] = -1;
   tf->bit_y[17] = 4;
   tf->bit_x[18] = -2;
   tf->bit_y[18] = 4;
   tf->bit_x[19] = -2;
   tf->bit_y[19] = 3;
   tf->bit_x[20] = -2;
   tf->bit_y[20] = 2;
   tf->bit_x[21] = -2;
   tf->bit_y[21] = 1;
   tf->bit_x[22] = -2;
   tf->bit_y[22] = 0;
   tf->bit_x[23] = -2;
   tf->bit_y[23] = -1;
   tf->width_at_border = 3;
   tf->total_width = 7;
   tf->reversed_border = true;
   return tf;
}

void AcTag24h10_destroy(apriltag_family_t *tf)
{
   free(tf->bit_x);
   free(tf->bit_y);
   free(tf->name);
   free(tf);
}
