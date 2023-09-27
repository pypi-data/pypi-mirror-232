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

import java.io.*;
import java.util.*;
import java.awt.image.*;
import java.util.concurrent.LinkedBlockingDeque;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;  
import java.util.concurrent.locks.ReentrantLock;
import javax.imageio.*;

public class TagFamilyGenerator
{
    private final ImageLayout layout;
    int nbits;
    int minhamming;

    ArrayList<Long> codelist;
    long starttime;

    long rotcodes[] = new long[16384];
    int nrotcodes = 0;

    static final long PRIME = 982451653;

    public TagFamilyGenerator(ImageLayout layout, int minhamming)
    {
        this.layout = layout;
        this.nbits = layout.getNumBits();
        this.minhamming = minhamming;
    }

    static final void printBoolean(PrintStream outs, long v, int nbits)
    {
        for (int b = nbits-1; b >= 0; b--)
            outs.printf("%d", (v & (1L<<b)) > 0 ? 1 : 0);
    }

    static final void printCodes(long codes[], int nbits)
    {
        for (int i = 0; i < codes.length; i++) {
            long w = codes[i];
            System.out.printf("%5d ", i);
            printBoolean(System.out, w, nbits);
            System.out.printf("    %0"+((int) Math.ceil(nbits/4))+"x\n", w);
        }
    }

    public static void printUsage()
    {
        System.out.println("\nUsage: ./generateAcTags.sh -d dataBits -h minimumHammingDistance [-i]");
        System.out.println("For example: ./generateAcTags.sh -d 24 -h 10 -i\n");
        System.out.println("Parameters:");
        System.out.println("\tData Bits: The number of data bits for this tag family. This value must be equal to i*4,");
        System.out.println("\twhere i is an integer >= 4. A higher number of data bits correlates with:");
        System.out.println("\t\t- A larger number of tags in the family.");
        System.out.println("\t\t- Less false positive detections.");
        System.out.println("\t\t- Less true positive detections as a result of smaller data bits.");
        System.out.println("\t\t- A higher possible minimum hamming distance.\n");
        System.out.println("\tMinimum Hamming Distance: The minimum number of data bits that can be flipped to find");
        System.out.println("\tanother tag in the family. This value must be an integer >= 1. The number of bit"); 
        System.out.println("\tcorrections allowed during AprilTag or AcTag detection can be specified by the user, but");
        System.out.println("\tit must be less than half of the minimum hamming distance. Therefore, a higher minimum");
        System.out.println("\thamming distance allows for more bit corrections. A higher number of bit corrections");
        System.out.println("\tcorrelates with:");
        System.out.println("\t\t- Significantly more true positive detections.");
        System.out.println("\t\t- Slightly more false positive detections.\n");
        System.out.println("\t-i: If set, this will generate image files for the specified family into the image_files");
        System.out.println("\tfolder. Note: If you are using WSL, this will not work unless you have a display server");
        System.out.println("\tlike XLaunch running.\n");
    }

    public static void main(String args[])
    {
        if (args.length < 2) {
            System.out.println("\n=============== ERROR: Missing required arguments ===============");
            printUsage();
            System.exit(1);
        }
        
        ImageLayout layout = LayoutUtil.getLayout("24");
        try {
            layout = LayoutUtil.getLayout(args[0]);
        } catch(NumberFormatException e)  {
            System.out.println("\n=============== ERROR: Invalid Data Bits Value (val=" + args[0] + ") ===============");
            System.out.println("NumberFormatException: " + e.getMessage());
            printUsage();
            System.exit(1);
        }

        int minhamming = 10;
        try {
            minhamming = Integer.parseInt(args[1]);
            if (minhamming <= 0) {
                throw new NumberFormatException("Hamming must be >= 1");
            }
        } catch(NumberFormatException e) {
            System.out.println("\n=============== ERROR: Invalid Minimum Hamming Distance (val=" + args[1] + ") ===============");
            System.out.println("NumberFormatException: " + e.getMessage());
            printUsage();
            System.exit(1);
        }

        TagFamilyGenerator tfg = new TagFamilyGenerator(layout, minhamming);
        tfg.compute();
        tfg.report(false);
    }

    boolean isCodePartiallyOkay(long v, int nRotCodesPartial, String layoutName)
    {
        // tag must be reasonably complex
        if (!isComplexEnough(v)) {
            return false;
        }

        // The tag must be different from itself when rotated.
        long rv1 = TagFamily.rotate90(v, nbits);
        long rv2 = TagFamily.rotate90(rv1, nbits);
        long rv3 = TagFamily.rotate90(rv2, nbits);

        // If it's a sonar tag, it also must be different from itself when the
        // bit order is reversed.
        long orien[] = new long[8];
        if (layoutName.equals("Sonar")) {
            long vRev = TagFamily.reverseBits(v, nbits);
            long rv1Rev = TagFamily.reverseBits(rv1, nbits);
            long rv2Rev = TagFamily.reverseBits(rv2, nbits);
            long rv3Rev = TagFamily.reverseBits(rv3, nbits);
            orien[0] = v;
            orien[1] = rv1; 
            orien[2] = rv2; 
            orien[3] = rv3; 
            orien[4] = vRev;
            orien[5] = rv1Rev;
            orien[6] = rv2Rev;
            orien[7] = rv3Rev;

            for (int i = 0; i < orien.length; i++) {
                for (int j = i+1; j < orien.length; j++) {
                    if (!hammingDistanceAtLeast(orien[i], orien[j], minhamming)) {
                        return false;
                    }
                }
            }
        } else if (!hammingDistanceAtLeast(v, rv1, minhamming) ||
            !hammingDistanceAtLeast(v, rv2, minhamming) ||
            !hammingDistanceAtLeast(v, rv3, minhamming) ||
            !hammingDistanceAtLeast(rv1, rv2, minhamming) ||
            !hammingDistanceAtLeast(rv1, rv3, minhamming) ||
            !hammingDistanceAtLeast(rv2, rv3, minhamming)) {

            return false;
        }

        // tag must be different from other tags.
        for (int widx = 0; widx < nRotCodesPartial; widx++) {
            long w = rotcodes[widx];
            if (layoutName.equals("Sonar")) {
                for (int i = 0; i < orien.length; i++) {
                    if (!hammingDistanceAtLeast(orien[i], w, minhamming)) {
                        return false;
                    }
                }
            }
            else if (!hammingDistanceAtLeast(v, w, minhamming)) {
                return false;
            }
        }

        return true;
    }

    boolean isComplexEnough(long v) {
        int energy = 0;
        int[][] tag = layout.renderToArray(v);
        for (int y = 0; y < tag.length; y++) {
            for (int x = 0; x < tag.length - 1; x++) {
                if ((tag[y][x] == 0 && tag[y][x + 1] == 1) || (tag[y][x] == 1 && tag[y][x + 1] == 0)) {
                    energy++;
                }
            }
        }

        for (int x = 0; x < tag.length; x++) {
            for (int y = 0; y < tag.length - 1; y++) {
                if ((tag[y][x] == 0 && tag[y+1][x] == 1) || (tag[y][x] == 1 && tag[y+1][x] == 0)) {
                    energy++;
                }
            }
        }

        int area = 0;
        for (int y = 0; y < tag.length; y++) {
            for (int x = 0; x < tag.length; x++) {
                if (tag[y][x] == 0 || tag[y][x] == 1) {
                    area++;
                }
            }
        }

        int maxEnergy = 2*area;
        return energy >= 0.3333*maxEnergy;
    }

    void union(int[][] components, int x0, int y0, int x1, int y1) {
        int c0 = components[y0][x0];
        int c1 = components[y1][x1];

        for (int y = 0; y < components.length; y++) {
            for (int x = 0; x < components.length; x++) {
                if (components[y][x] == c1) {
                    components[y][x] = c0;
                }
            }
        }
    }

    boolean isCodePartiallyOkay2(long v, int nRotCodesPartial, String layoutName) {
        // Generate all possible orientations of the tag
        long orien[] = new long[8];
        if (layoutName.equals("Sonar")) {
            long rv1 = TagFamily.rotate90(v, nbits);
            long rv2 = TagFamily.rotate90(rv1, nbits);
            long rv3 = TagFamily.rotate90(rv2, nbits);
            long vRev = TagFamily.reverseBits(v, nbits);
            long rv1Rev = TagFamily.reverseBits(rv1, nbits);
            long rv2Rev = TagFamily.reverseBits(rv2, nbits);
            long rv3Rev = TagFamily.reverseBits(rv3, nbits);
            orien[0] = v;
            orien[1] = rv1; 
            orien[2] = rv2; 
            orien[3] = rv3; 
            orien[4] = vRev;
            orien[5] = rv1Rev;
            orien[6] = rv2Rev;
            orien[7] = rv3Rev;
        }

        // tag must be different from other tags.
        for (int widx = nRotCodesPartial; widx < nrotcodes; widx++) {
            long w = rotcodes[widx];
            long wOrien[] = new long[8];
            wOrien[0] = w;
            wOrien[1] = TagFamily.rotate90(wOrien[0], nbits);
            wOrien[2] = TagFamily.rotate90(wOrien[1], nbits);
            wOrien[3] = TagFamily.rotate90(wOrien[2], nbits); 
            wOrien[4] = TagFamily.reverseBits(wOrien[0], nbits);
            wOrien[5] = TagFamily.reverseBits(wOrien[1], nbits);
            wOrien[6] = TagFamily.reverseBits(wOrien[2], nbits);
            wOrien[7] = TagFamily.reverseBits(wOrien[3], nbits);
            if (layoutName.equals("Sonar")) {
                for (int i = 0; i < orien.length; i++) {
                    for (int j = 0; j < wOrien.length; j++) {
                        if (!hammingDistanceAtLeast(orien[i], wOrien[j], minhamming)) {
                            return false;
                        }
                    }
                }
            }
            else if (!hammingDistanceAtLeast(v, w, minhamming)) {
                return false;
            }
        }
        return true;
    }

    class PartialApprovalTask implements Runnable {
        private HashMap<Long, PartialApprovalResult> map;
        private int nRotCodesPartial;
        private long V0;
        private long iter0;
        private long iter1;
        private String layoutName;

        PartialApprovalTask(HashMap<Long, PartialApprovalResult> map, int nRotCodesPartial, long V0, long iter0, long iter1, String layoutName) {
            this.map = map;
            this.nRotCodesPartial = nRotCodesPartial;
            this.V0 = V0;
            this.iter0 = iter0;
            this.iter1 = iter1;
            this.layoutName = layoutName;
        }

        @Override
        public void run() {
            // compute v = V0 + PRIME * iter0,
            // being very careful about overflow.
            // (consider the power-of-two expansion of iter0....)
            long v = V0;

            long acc = PRIME;
            long M = iter0;
            while (M > 0) {
                if ((M & 1) > 0) {
                    v += acc;
                    v &= ((1L<<nbits) - 1);
                }

                acc *= 2;
                acc &= ((1L << nbits) - 1);
                M >>= 1;
            }

            PartialApprovalResult result = new PartialApprovalResult();
            result.nRotCodesPartial = nRotCodesPartial;
            result.iter0 = this.iter0;
            result.iter1 = this.iter1;

            for (long iter = iter0; iter < iter1; iter++) {
                v += PRIME; // big prime.
                v &= ((1L<<nbits) - 1);

                if (isCodePartiallyOkay(v, nRotCodesPartial, this.layoutName)) {
                    result.goodCodes.add(v);
                }
            }

            synchronized (map) {
                map.put(result.iter0, result);
            }
        }
    }

    class PartialApprovalResult {
        ArrayList<Long> goodCodes = new ArrayList<Long>();
        int nRotCodesPartial;
        Long iter0;
        Long iter1;
    }

    class ReportingThread extends Thread {
        public void run() {
            long lastreporttime = System.currentTimeMillis();
            long lastNumCodes = 0;

            while (!Thread.interrupted()) {
                // print a partial report.
                if ((System.currentTimeMillis() - lastreporttime > 60 * 60 * 1000) ||
                        (codelist.size() > 1.1*lastNumCodes && System.currentTimeMillis() - lastreporttime > 60*1000)) {
                    System.out.printf("Saving partial AcTag family...\n");
                    report(true);
                    System.out.printf("\nPartial AcTag family saved. Continuing with computation...\n");
                    lastreporttime = System.currentTimeMillis();
                    lastNumCodes = codelist.size();
                }

                try {
                    Thread.sleep(10*1000L);
                } catch (InterruptedException e) {
                    break;
                }
            }
        }
    }

    class ApprovalThread extends Thread {
        private HashMap<Long, PartialApprovalResult> map;
        private Long iter;
        private String layoutName;

        ApprovalThread(HashMap<Long, PartialApprovalResult> map, String layoutName) {
            this.map = map;
            this.iter = 0L;
            this.layoutName = layoutName;
        }

        public void run() {
            while (true) {
                if (iter == (1L << nbits)) {
                    return;
                }

                PartialApprovalResult result;
                while(true) {
                    synchronized (map) {
                        if (map.containsKey(iter)) {
                            result = map.remove(iter);
                            this.iter = result.iter1;
                            break;
                        }
                    }

                    try {
                        sleep(1);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }

                for (Long v : result.goodCodes) {
                    if (isCodePartiallyOkay2(v, result.nRotCodesPartial, this.layoutName)) {
                        synchronized (codelist) {
                            codelist.add(v);
                            long rv1 = TagFamily.rotate90(v, nbits);
                            long rv2 = TagFamily.rotate90(rv1, nbits);
                            long rv3 = TagFamily.rotate90(rv2, nbits);
                            int amountOfInc = 4;

                            if (this.layoutName.equals("Sonar")) {
                                amountOfInc = 8;
                            }

                            // grow?
                            if (nrotcodes + amountOfInc >= rotcodes.length) {
                                long newrotcodes[] = new long[rotcodes.length*2];
                                System.arraycopy(rotcodes, 0, newrotcodes, 0, rotcodes.length);
                                rotcodes = newrotcodes;
                            }

                            rotcodes[nrotcodes++] = v;
                            rotcodes[nrotcodes++] = rv1;
                            rotcodes[nrotcodes++] = rv2;
                            rotcodes[nrotcodes++] = rv3;
                            if (this.layoutName.equals("Sonar")) {
                                long vRev = TagFamily.reverseBits(v, nbits);
                                long rv1Rev = TagFamily.reverseBits(rv1, nbits);
                                long rv2Rev = TagFamily.reverseBits(rv2, nbits);
                                long rv3Rev = TagFamily.reverseBits(rv3, nbits);

                                rotcodes[nrotcodes++] = vRev;
                                rotcodes[nrotcodes++] = rv1Rev;
                                rotcodes[nrotcodes++] = rv2Rev;
                                rotcodes[nrotcodes++] = rv3Rev;
                            }
                        }
                    }
                }
            }
        }
    }

    public TagFamily compute()
    {
        assert(codelist == null);

        codelist = new ArrayList<Long>(); // code lists
        starttime = System.currentTimeMillis();

        // begin our search at a random position to avoid any bias
        // towards small numbers (which tend to have larger regions of
        // solid black).
        long V0 = 0x445965L; // Seed with the tag we've used in our paper

        long lastprogresstime = starttime;
        long lastprogressiters = 0;
        double lastRate = 0;

        int nthreads = Runtime.getRuntime().availableProcessors();
        System.out.printf("Using %d threads.\n", nthreads);

        ThreadPoolExecutor pool = new ThreadPoolExecutor(nthreads, nthreads, 0, TimeUnit.SECONDS, new LinkedBlockingQueue<Runnable>());
        HashMap<Long, PartialApprovalResult> map = new HashMap<Long, PartialApprovalResult>();
        int mapMax = 300;

        Thread approvalThread = new ApprovalThread(map, layout.getName());
        approvalThread.start();
        Thread reportingThread = new ReportingThread();
        reportingThread.start();

        long iter = 0;
        long chunksize = 50000;
        if(layout.getName().equals("Sonar")) {
            chunksize = chunksize / 8;
        }

        boolean firstError = false;

        while (true) {
            // print a progress report.
            long now = System.currentTimeMillis();
            if (now - lastprogresstime > 5000) {
                double donepercent = (iter*100.0)/(1L<<nbits);
                double dt = (now - lastprogresstime)/1000.0;
                long diters = iter - lastprogressiters;
                double rate = diters / dt; // iterations per second
                double secremaining = ((long) (1L<<nbits) - iter) / rate;
                synchronized (System.out) {
                    System.out.printf("%8.4f%%  codes: %-5d (%.0f iters/sec, %.2f minutes = %.2f hours)           \n",
                        donepercent, codelist.size(), rate, secremaining / (60.0), secremaining / 3600.0);
                    if (rate == 0 && !firstError && lastRate == 0) {
                        System.out.printf("\n ============ ERROR: Unknown termination time ========================================================\n");
                        System.out.printf(" - Partial Families will automatically be saved if you don't want to wait the full computation time.\n");
                        System.out.printf("   Wait for the \"Partial AcTag family saved. Continuing with computation...\" line in the terminal\n");
                        System.out.printf("   output, and then hit CTRL-C. The generation script will finish generating the partial AcTag family.\n");
                        System.out.printf(" - To speed up computation, consider increasing the hamming distance.\n");
                        System.out.printf(" - If you need an accurate time estimate, consider dropping the value of \"chunksize\" on line 459 of\n");
                        System.out.printf("   src/april/tag/TagFamilyGenerator.java.\n");
                        System.out.printf(" =====================================================================================================\n\n");
                        firstError = true;
                    } 
                }
                lastprogresstime = now;
                lastprogressiters = iter;
                lastRate = rate;
            }

            if (pool.getQueue().size() == 0) {
                if (iter < 1L << nbits) {
                    boolean addTask = false;
                    synchronized (map) {
                        addTask = map.size() < mapMax;
                    }

                    if (addTask) {
                        synchronized (codelist) {
                            long iter0 = iter;
                            iter = Math.min(iter + chunksize, 1L << nbits);
                            pool.execute(new PartialApprovalTask(map, codelist.size(), V0, iter0, iter, layout.getName()));
                        }
                        try {
                            Thread.sleep(1);
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                        }
                        continue;
                    }
                }
            }

            if (!approvalThread.isAlive()) {
                System.out.println("Approval thread dead. Done!");
                break;
            }

            try {
                Thread.sleep(10);
            } catch (InterruptedException e) {
                System.out.println("Interrupted.");
                e.printStackTrace();
            }
        }

        reportingThread.interrupt();
        pool.shutdown();

        long codes[] = new long[codelist.size()];
        for (int i = 0; i < codelist.size(); i++) {
            codes[i] = codelist.get(i);
        }

        return new TagFamily(layout, minhamming, codes);
    }

    void report(boolean isPartialFamily)
    {
        int nCodes;
        synchronized (codelist) {
            nCodes = codelist.size();
        }

        // If number of codes is zero, exit the program
        if (nCodes == 0) {
            System.out.println("ERROR: No tags found in this family. Increase the # of data bits or decrease the hamming distance");
            System.exit(1);
        }

        long codes[] = new long[nCodes];
        for (int i = 0; i < nCodes; i++)
            codes[i] = codelist.get(i);

        int hds[] = new int[nbits+1];
        int hdtotal = 0;

        // compute hamming distance table
        for (int i = 0; i < nCodes; i++) {
            long rv0 = codelist.get(i);
            long rv1 = TagFamily.rotate90(rv0, nbits);
            long rv2 = TagFamily.rotate90(rv1, nbits);
            long rv3 = TagFamily.rotate90(rv2, nbits);

            long rv0Rev = 0;
            long rv1Rev = 0;
            long rv2Rev = 0;
            long rv3Rev = 0;
            if(layout.getName().equals("Sonar")) {
                rv0Rev = TagFamily.reverseBits(rv0, nbits);
                rv1Rev = TagFamily.reverseBits(rv1, nbits);
                rv2Rev = TagFamily.reverseBits(rv2, nbits);
                rv3Rev = TagFamily.reverseBits(rv3, nbits);
            }

            for (int j = i+1; j < nCodes; j++) {
                int dist = 1;
                if(layout.getName().equals("Sonar")) {
                    dist = Math.min(Math.min(Math.min(hammingDistance(rv0, codelist.get(j)),
                                                      hammingDistance(rv1, codelist.get(j))),
                                             Math.min(hammingDistance(rv2, codelist.get(j)),
                                                      hammingDistance(rv3, codelist.get(j)))),
                                    Math.min(Math.min(hammingDistance(rv0Rev, codelist.get(j)),
                                                      hammingDistance(rv1Rev, codelist.get(j))),
                                             Math.min(hammingDistance(rv2Rev, codelist.get(j)),
                                                      hammingDistance(rv3Rev, codelist.get(j)))));
                } else {
                    dist = Math.min(Math.min(hammingDistance(rv0, codelist.get(j)),
                                             hammingDistance(rv1, codelist.get(j))),
                                    Math.min(hammingDistance(rv2, codelist.get(j)),
                                             hammingDistance(rv3, codelist.get(j))));
                }
                hds[dist]++;
                if (dist < minhamming) {
                    System.out.printf("ERROR, dist = %3d: %d %d\n", dist, i, j);
                }
                hdtotal++;
            }
        }

        // Compute hamming distances in camera if we're generating a sonar tag family.
        int cameraMinHam = minhamming;
        int hdsCam[] = new int[nbits+1];

        if(layout.getName().equals("Sonar")) {
            for (int i = 0; i < nCodes; i++) {
                long rv0 = codelist.get(i);
                long rv1 = TagFamily.rotate90(rv0, nbits);
                long rv2 = TagFamily.rotate90(rv1, nbits);
                long rv3 = TagFamily.rotate90(rv2, nbits);

                for (int j = i+1; j < nCodes; j++) {
                    int dist = Math.min(Math.min(hammingDistance(rv0, codelist.get(j)),
                                                    hammingDistance(rv1, codelist.get(j))),
                                    Math.min(hammingDistance(rv2, codelist.get(j)),
                                                    hammingDistance(rv3, codelist.get(j)))); 

                    hdsCam[dist]++;
                    if (dist < cameraMinHam) {
                        cameraMinHam = dist;
                    }
                }
            }
        }

        synchronized (System.out) {
            String cname = String.format("AcTag%dh%d", nbits, minhamming);
            try {
                final String dir = System.getProperty("user.dir");
                FileWriter fileWriter = new FileWriter(dir + "/../python/actag/generated_families/" + cname + "Sonar.java");
                PrintWriter printWriter = new PrintWriter(fileWriter);
                String cnameCam = String.format("AcTag%dh%d", nbits, cameraMinHam);
                if (isPartialFamily) {
                    printWriter.printf("// WARNING: This AcTag family MAY BE INCOMPLETE. If you need all the\n");
                    printWriter.printf("// tags in this family, please delete this file and regenerate.\n\n");
                }
                printWriter.printf("/** Tag family with %d distinct codes.\n", codes.length);
                if(layout.getName().equals("Sonar")) {
                    printWriter.printf("    bits: %d,\n    minimum hamming in sonar: %d,\n", nbits, minhamming);
                    printWriter.printf("    minimum hamming in camera: %d\n\n", cameraMinHam);
                } else {
                    printWriter.printf("    bits: %d,  minimum hamming: %d\n\n", nbits, minhamming);
                }

                // compute some ROC statistics, assuming randomly-visible targets
                // as a function of how many bits we're willing to correct.
                printWriter.printf("    Max bits corrected (Sonar)       False positive rate (Sonar)\n");

                for (int cbits = 0; cbits <= (minhamming - 1) / 2; cbits++) {
                    long validCodes = 0; // how many input codes will be mapped to a single valid code?
                    // it's the number of input codes that have 0 errors, 1 error, 2 errors, ..., cbits errors.
                    for (int i = 0; i <= cbits; i++)
                        validCodes += choose(nbits, i);

                    validCodes *= codes.length; // total number of codes

                    printWriter.printf("          %3d             %15.8f %%\n", cbits, (100.0 * validCodes) / (1L << nbits));
                }

                // compute some ROC statistics, assuming randomly-visible targets
                // as a function of how many bits we're willing to correct.
                printWriter.printf("\n    Max bits corrected (Camera)       False positive rate (Camera)\n");

                for (int cbits = 0; cbits <= (cameraMinHam - 1) / 2; cbits++) {
                    long validCodes = 0; // how many input codes will be mapped to a single valid code?
                    // it's the number of input codes that have 0 errors, 1 error, 2 errors, ..., cbits errors.
                    for (int i = 0; i <= cbits; i++)
                        validCodes += choose(nbits, i);

                    validCodes *= codes.length; // total number of codes

                    printWriter.printf("          %3d             %15.8f %%\n", cbits, (100.0 * validCodes) / (1L << nbits));
                }

                printWriter.printf("\n    Generation time: %f s\n\n", (System.currentTimeMillis() - starttime) / 1000.0);

                printWriter.printf("    Hamming distance between pairs of codes in sonar (accounting for rotation and reversal):\n\n");
                for (int i = 0; i < hds.length; i++) {
                    printWriter.printf("    %4d  %d\n", i, hds[i]);
                }

                printWriter.printf("\n    Hamming distance between pairs of codes in camera (accounting for rotation):\n\n");
                for (int i = 0; i < hdsCam.length; i++) {
                    printWriter.printf("    %4d  %d\n", i, hdsCam[i]);
                }

                // Print output for the sonar.
                printWriter.printf("**/\n");
                printWriter.printf("package april.tag;\n\n");
                printWriter.printf("public class %sSonar extends TagFamily\n", cname);
                printWriter.printf("{\n");

                int maxLength = 8192;
                int numSubMethods = (maxLength + codes.length - 1) / maxLength;
                for (int i = 0; i < numSubMethods; i++) {
                    printWriter.printf("\tprivate static class ConstructCodes%d {\n", i);
                    printWriter.printf("\t\tprivate static long[] constructCodes() {\n");
                    printWriter.printf("\t\t\treturn new long[] { ");
                    int jMax = Math.min(maxLength, codes.length - i * maxLength);
                    for (int j = 0; j < jMax; j++) {
                        long w = codes[i * maxLength + j];
                        printWriter.printf("0x%0" + ((int) Math.ceil(nbits / 4)) + "xL", w);
                        if (j == jMax - 1) {
                            printWriter.printf(" };\n\t\t}\n\t}\n\n");
                        } else {
                            printWriter.printf(", ");
                        }
                    }
                }

                printWriter.printf("\tprivate static long[] constructCodes() {\n");
                printWriter.printf("\t\tlong[] codes = new long[%d];\n", codes.length);
                for (int i = 0; i < numSubMethods; i++) {
                    printWriter.printf("\t\tSystem.arraycopy(ConstructCodes%d.constructCodes(), 0, codes, %d, %d);\n",
                            i, i * maxLength, Math.min(maxLength, codes.length - i * maxLength));
                }
                printWriter.printf("\t\treturn codes;\n");
                printWriter.printf("\t}\n\n");


                printWriter.printf("\tpublic %sSonar()\n", cname);
                printWriter.printf("\t{\n");
                printWriter.printf("\t\tsuper(ImageLayout.Factory.createFromString(\"%s\", \"%s\"), %d, constructCodes());\n",
                        layout.getName(), layout.getDataString(), minhamming);
                printWriter.printf("\t}\n");
                printWriter.printf("}\n");
                printWriter.printf("\n");

                // Print output for the camera
                printWriter.close();
                FileWriter fileWriter2 = new FileWriter(dir + "/../python/actag/generated_families/" + cnameCam + ".java");
                PrintWriter printWriter2 = new PrintWriter(fileWriter2);
                printWriter2.printf("package april.tag;\n\n");
                printWriter2.printf("public class %s extends TagFamily\n", cnameCam);
                printWriter2.printf("{\n");

                for (int i = 0; i < numSubMethods; i++) {
                    printWriter2.printf("\tprivate static class ConstructCodes%d {\n", i);
                    printWriter2.printf("\t\tprivate static long[] constructCodes() {\n");
                    printWriter2.printf("\t\t\treturn new long[] { ");
                    int jMax = Math.min(maxLength, codes.length - i * maxLength);
                    for (int j = 0; j < jMax; j++) {
                        long w = codes[i * maxLength + j];
                        printWriter2.printf("0x%0" + ((int) Math.ceil(nbits / 4)) + "xL", w);
                        if (j == jMax - 1) {
                            printWriter2.printf(" };\n\t\t}\n\t}\n\n");
                        } else {
                            printWriter2.printf(", ");
                        }
                    }
                }

                printWriter2.printf("\tprivate static long[] constructCodes() {\n");
                printWriter2.printf("\t\tlong[] codes = new long[%d];\n", codes.length);
                for (int i = 0; i < numSubMethods; i++) {
                    printWriter2.printf("\t\tSystem.arraycopy(ConstructCodes%d.constructCodes(), 0, codes, %d, %d);\n",
                            i, i * maxLength, Math.min(maxLength, codes.length - i * maxLength));
                }
                printWriter2.printf("\t\treturn codes;\n");
                printWriter2.printf("\t}\n\n");


                printWriter2.printf("\tpublic %s()\n", cnameCam);
                printWriter2.printf("\t{\n");
                printWriter2.printf("\t\tsuper(ImageLayout.Factory.createFromString(\"%s\", \"%s\"), %d, constructCodes());\n",
                        layout.getName(), layout.getDataString(), cameraMinHam);
                printWriter2.printf("\t}\n");
                printWriter2.printf("}\n");
                printWriter2.printf("\n");

                // Close the printWriter2
                printWriter2.close();

            } catch(Exception e) {
                System.out.println(e.toString());
            }
        }
    }

    static long choose(int n, int c)
    {
        long v = 1;
        for (int i = 0; i < c; i++)
            v *= (n-i);
        for (int i = 1; i <= c; i++)
            v /= i;
        return v;
    }

    /** Compute the hamming distance between two longs. **/
    public static final int hammingDistance(long a, long b)
    {
        return popCount2(a^b);
    }

    public static final boolean hammingDistanceAtLeast(long a, long b, int minval)
    {
        long w = a^b;

        int count = 0;

        while (w != 0) {
            count += popCountTable[(int) (w&(popCountTable.length-1))];
            if (count >= minval)
                return true;

            w >>= popCountTableShift;
        }

        return false;
    }

    /** How many bits are set in the long? **/
    static final int popCountReal(long w)
    {
        return Long.bitCount(w);
    }


    static final int popCountTableShift = 16;
    static final byte[] popCountTable = new byte[1<<popCountTableShift];
    static {
        for (int i = 0; i < popCountTable.length; i++) {
            popCountTable[i] = (byte) popCountReal(i);
        }
    }

    public static final int popCount2(long w)
    {
        int count = 0;

        while (w != 0) {
            count += popCountTable[(int) (w&(popCountTable.length-1))];
            w >>= popCountTableShift;
        }
        return count;
    }
}
