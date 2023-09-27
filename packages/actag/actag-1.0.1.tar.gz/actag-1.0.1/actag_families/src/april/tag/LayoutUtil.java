/* Copyright (C) 2013-2016, The Regents of The University of Michigan.
All rights reserved.
This software was developed in the APRIL Robotics Lab under the
direction of Edwin Olson, ebolson@umich.edu. This software may be
available under alternative licensing terms; contact the address above.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the Regents of The University of Michigan.
*/

package april.tag;

import static java.lang.Math.*;

public class LayoutUtil {
    public static ImageLayout getLayout(String specifier) {
        // Get number of desired data bits and find the tag size
        int dataBits = Integer.parseInt(specifier);
        double tagSize = (Double.valueOf(dataBits) / 4.0) + 1.0;

        // Make sure the tag size is an integer and >= 5, otherwise the number of desired data bits is invalid
        if ((tagSize % 1) == 0 && tagSize >= 5.0) {
            return LayoutUtil.getSonarLayout((int)tagSize);
        } else {
            // Set tagSize to a big enough value to generate valid example data bit values
            if (tagSize <= 5.0) {
                tagSize = 5.5;
            }
            long closestValidDataBitsFloor = Math.round(Math.floor(tagSize - 1.0) * 4.0);
            long closestValidDataBitsCeil = Math.round(Math.ceil(tagSize - 1.0) * 4.0);
            throw new RuntimeException("Invalid number of data bits (" + dataBits + "):\n\n\tDue to AcTag " +
                                       "layout specifications, the data bits specified must be equal to " +
                                       "i * 4, where\n\ti is >= 4. Two valid data bit values close " +
                                       "to your desired value are " + closestValidDataBitsFloor + " and " +
                                       closestValidDataBitsCeil + ". Please\n\ttry again with a valid " + 
                                       "number of data bits.\n");
        }
    }

    private static int l1DistToEdge(int x, int y, int size) {
        return Math.min(Math.min(x, size - 1 - x), Math.min(y, size - 1 - y));
    }

    public static ImageLayout getSonarLayout(int size) {
        StringBuilder sb = new StringBuilder();
        for (int y = 0; y < size; y++) {
            for (int x = 0; x < size; x++) {
                if (LayoutUtil.l1DistToEdge(x, y, size) == 0) {
                    sb.append('d');
                } else if (LayoutUtil.l1DistToEdge(x, y, size) == 1) {
                    sb.append('b');
                } else {
                    sb.append('w');
                }
            }
        }
        return ImageLayout.Factory.createFromString("Sonar", sb.toString());
    }

    public static ImageLayout getClassicLayout(int size) {
        StringBuilder sb = new StringBuilder();
        for (int y = 0; y < size; y++) {
            for (int x = 0; x < size; x++) {
                if (LayoutUtil.l1DistToEdge(x, y, size) == 0) {
                    sb.append('w');
                } else if (LayoutUtil.l1DistToEdge(x, y, size) == 1) {
                    sb.append('b');
                } else {
                    sb.append('d');
                }
            }
        }
        // Classic layout has no name for backwards compatibility.
        return ImageLayout.Factory.createFromString("", sb.toString());
    }

    public static ImageLayout getStandardLayout(int size) {
        StringBuilder sb = new StringBuilder();
        for (int y = 0; y < size; y++) {
            for (int x = 0; x < size; x++) {
                if (LayoutUtil.l1DistToEdge(x, y, size) == 1) {
                    sb.append('b');
                } else if (LayoutUtil.l1DistToEdge(x, y, size) == 2) {
                    sb.append('w');
                } else {
                    sb.append('d');
                }
            }
        }
        return ImageLayout.Factory.createFromString("Standard", sb.toString());
    }

    public static ImageLayout getCircleLayout(int size) {
        StringBuilder sb = new StringBuilder();
        double cutoff = size/2.0 - 0.25;
        int borderDistance = (int) ceil(size/2.0 - cutoff*sqrt(0.5) - 0.5);
        for (int y = 0; y < size; y++) {
            for (int x = 0; x < size; x++) {
                if (l1DistToEdge(x, y, size) == borderDistance) {
                    sb.append('b');
                } else if (l1DistToEdge(x, y, size) == borderDistance+1) {
                    sb.append('w');
                } else if (LayoutUtil.l2DistToCenter(x, y, size) <= cutoff) {
                    sb.append('d');
                } else {
                    sb.append('x');
                }
            }
        }

        return ImageLayout.Factory.createFromString("Circle", sb.toString());
    }

    private static double l2DistToCenter(int x, int y, int size) {
        double r = size/2.0;
        return sqrt(pow(x + 0.5 - r, 2) + pow(y + 0.5 - r, 2));
    }
}
