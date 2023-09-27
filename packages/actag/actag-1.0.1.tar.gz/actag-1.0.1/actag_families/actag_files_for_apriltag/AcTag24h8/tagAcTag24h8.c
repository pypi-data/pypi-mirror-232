#include <stdlib.h>
#include "tagAcTag24h8.h"

static uint64_t codedata[45] = {
   0x0000000000d35f2aUL,
   0x00000000006264efUL,
   0x0000000000da9317UL,
   0x0000000000ffd28eUL,
   0x0000000000d95741UL,
   0x0000000000685d06UL,
   0x00000000006f90f3UL,
   0x000000000014327fUL,
   0x00000000001a2a96UL,
   0x0000000000469dfaUL,
   0x000000000073115eUL,
   0x0000000000b3e4b3UL,
   0x000000000041aea2UL,
   0x0000000000212b6cUL,
   0x00000000005396e7UL,
   0x0000000000ac4a98UL,
   0x00000000008bc762UL,
   0x0000000000af97ecUL,
   0x0000000000cd705fUL,
   0x0000000000d47135UL,
   0x0000000000588f8bUL,
   0x0000000000c49a6eUL,
   0x00000000009f6d8fUL,
   0x00000000004e905cUL,
   0x00000000009ed44aUL,
   0x0000000000778ca1UL,
   0x00000000002ec24fUL,
   0x0000000000be6aa5UL,
   0x0000000000ed3536UL,
   0x0000000000b8773fUL,
   0x00000000004bc9e1UL,
   0x0000000000819548UL,
   0x00000000004a2342UL,
   0x0000000000c0a65cUL,
   0x0000000000d280baUL,
   0x000000000047b089UL,
   0x00000000002831e5UL,
   0x00000000007a9564UL,
   0x000000000025a38aUL,
   0x00000000002cd83dUL,
   0x00000000008f8b49UL,
   0x00000000009df5e3UL,
   0x0000000000f175d7UL,
   0x000000000041f70dUL,
   0x0000000000ce12e5UL,
};
apriltag_family_t *AcTag24h8_create()
{
   apriltag_family_t *tf = calloc(1, sizeof(apriltag_family_t));
   tf->name = strdup("AcTag24h8");
   tf->h = 8;
   tf->ncodes = 45;
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

void AcTag24h8_destroy(apriltag_family_t *tf)
{
   free(tf->bit_x);
   free(tf->bit_y);
   free(tf->name);
   free(tf);
}
