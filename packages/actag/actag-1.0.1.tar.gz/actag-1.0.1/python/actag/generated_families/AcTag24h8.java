/** Tag family with 45 distinct codes.
    bits: 24,
    minimum hamming in sonar: 8,
    minimum hamming in camera: 8

    Max bits corrected (Sonar)       False positive rate (Sonar)
            0                  0.00026822 %
            1                  0.00670552 %
            2                  0.08073449 %
            3                  0.62361360 %

    Max bits corrected (Camera)       False positive rate (Camera)
            0                  0.00026822 %
            1                  0.00670552 %
            2                  0.08073449 %
            3                  0.62361360 %

    Generation time: 38.807000 s

    Hamming distance between pairs of codes in sonar (accounting for rotation and reversal):

       0  0
       1  0
       2  0
       3  0
       4  0
       5  0
       6  0
       7  0
       8  567
       9  82
      10  310
      11  4
      12  27
      13  0
      14  0
      15  0
      16  0
      17  0
      18  0
      19  0
      20  0
      21  0
      22  0
      23  0
      24  0

    Hamming distance between pairs of codes in camera (accounting for rotation):

       0  0
       1  0
       2  0
       3  0
       4  0
       5  0
       6  0
       7  0
       8  327
       9  59
      10  400
      11  27
      12  163
      13  0
      14  14
      15  0
      16  0
      17  0
      18  0
      19  0
      20  0
      21  0
      22  0
      23  0
      24  0
**/
package april.tag;

public class AcTag24h8 extends TagFamily
{
	private static class ConstructCodes0 {
		private static long[] constructCodes() {
			return new long[] { 0xd35f2aL, 0x6264efL, 0xda9317L, 0xffd28eL, 0xd95741L, 0x685d06L, 0x6f90f3L, 0x14327fL, 0x1a2a96L, 0x469dfaL, 0x73115eL, 0xb3e4b3L, 0x41aea2L, 0x212b6cL, 0x5396e7L, 0xac4a98L, 0x8bc762L, 0xaf97ecL, 0xcd705fL, 0xd47135L, 0x588f8bL, 0xc49a6eL, 0x9f6d8fL, 0x4e905cL, 0x9ed44aL, 0x778ca1L, 0x2ec24fL, 0xbe6aa5L, 0xed3536L, 0xb8773fL, 0x4bc9e1L, 0x819548L, 0x4a2342L, 0xc0a65cL, 0xd280baL, 0x47b089L, 0x2831e5L, 0x7a9564L, 0x25a38aL, 0x2cd83dL, 0x8f8b49L, 0x9df5e3L, 0xf175d7L, 0x41f70dL, 0xce12e5L };
		}
	}

	private static long[] constructCodes() {
		long[] codes = new long[45];
		System.arraycopy(ConstructCodes0.constructCodes(), 0, codes, 0, 45);
		return codes;
	}

	public AcTag24h8()
	{
		super(ImageLayout.Factory.createFromString("Sonar", "ddddddddbbbbbddbwwwbddbwwwbddbwwwbddbbbbbdddddddd"), 8, constructCodes());
	}
}

