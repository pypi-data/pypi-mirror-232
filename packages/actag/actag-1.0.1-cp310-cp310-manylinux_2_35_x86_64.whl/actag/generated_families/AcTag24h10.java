/** Tag family with 7 distinct codes.
    bits: 24,
    minimum hamming in sonar: 10,
    minimum hamming in camera: 10

    Max bits corrected (Sonar)       False positive rate (Sonar)
            0                  0.00004172 %
            1                  0.00104308 %
            2                  0.01255870 %
            3                  0.09700656 %
            4                  0.54035783 %

    Max bits corrected (Camera)       False positive rate (Camera)
            0                  0.00004172 %
            1                  0.00104308 %
            2                  0.01255870 %
            3                  0.09700656 %
            4                  0.54035783 %

    Generation time: 7.874000 s

    Hamming distance between pairs of codes in sonar (accounting for rotation and reversal):

       0  0
       1  0
       2  0
       3  0
       4  0
       5  0
       6  0
       7  0
       8  0
       9  0
      10  15
      11  6
      12  0
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
       8  0
       9  0
      10  15
      11  5
      12  0
      13  1
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
**/
package april.tag;

public class AcTag24h10 extends TagFamily
{
	private static class ConstructCodes0 {
		private static long[] constructCodes() {
			return new long[] { 0xd35f2aL, 0x6264efL, 0x9714ffL, 0x3d9e3eL, 0x11acecL, 0x0cab28L, 0x03b65aL };
		}
	}

	private static long[] constructCodes() {
		long[] codes = new long[7];
		System.arraycopy(ConstructCodes0.constructCodes(), 0, codes, 0, 7);
		return codes;
	}

	public AcTag24h10()
	{
		super(ImageLayout.Factory.createFromString("Sonar", "ddddddddbbbbbddbwwwbddbwwwbddbwwwbddbbbbbdddddddd"), 10, constructCodes());
	}
}

