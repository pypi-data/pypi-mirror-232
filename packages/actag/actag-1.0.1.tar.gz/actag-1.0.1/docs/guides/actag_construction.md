# Constructing AcTags

Once you've [picked an AcTag family](./actag_families.md) to use, you can begin constructing physical AcTags. AcTags were designed to be cheap and easy to manufacture. Below is the AcTag Bill of Materials for a 1' tag and a 2' tag:

| Material                                            | Unit Cost  | Materials for 1' AcTag  | Materials for 2' AcTag  | Provider | Link |
| ----------------------------------------------------|------------|--------------------|--------------------|----------|------|
| 1 mm Aluminum Sheet (5052 or 6061) cut w/Tag Design | Varies, but there is a $30 order minimum | 1 Cut sheet (~$10)         | 1 Cut sheet (~$45)      | SendCutSend            | https://www.sendcutsend.com                                             |
| 1/2" Acoustic Foam (18" by 24")    | $10.98 for 1 piece | 12" by 12" square, or 1/3 of a unit ($3.66) | 24" by 24" square, or 4/3rd of a unit ($14.66) | Sonic Barrier / Amazon   | https://www.amazon.com/Sonic-Barrier-Acoustic-Foam-PSA/dp/B0007XFBE0 |
| 1' by 1' Thick Aluminum ACM Sheet | $6.92 for 1 sheet | 1 unit ($6.92) | N/A | Home Depot | https://www.homedepot.com/p/Falken-Design-12-in-x-12-in-x-1-8-in-Thick-Aluminum-Composite-ACM-White-Sheet-Falken-Design-ACM-WT-1-8-1212/308670327 |
| 2' by 2' Thick Aluminum ACM Sheet  | $23.28 for 1 sheet | N/A | 1 unit ($23.28)  | Home Depot | https://www.homedepot.com/p/Falken-Design-24-in-x-24-in-x-1-8-in-Thick-Aluminum-Composite-ACM-Brushed-Silver-Sheet-Falken-Design-ACM-BR-S-1-8-2424/308670311 |
| #6 x 1 in. inch Metal Screws  | $1.38 for 10 screws | 4 screws, or 2/5th of a unit ($0.60)    | 8 screws, or 4/5th of a unit ($1.20)    | Home Depot       | https://www.homedepot.com/p/Everbilt-6-x-1-in-Phillips-Flat-Head-Zinc-Plated-Sheet-Metal-Screw-10-Pack-805421/204275312 |
| #6-32 Steel Cap Nuts          | $1.97 for 25 nuts | 4 nuts, or 4/25th of a unit ($0.32)    | 8 nuts, or 8/25th of a unit ($0.64)    | Home Depot       | https://www.homedepot.com/p/6-32-Zinc-Plated-Steel-Acorn-Cap-Nuts-25-Pack-9077023/310518794 |
| 1/2" Steel Spacers            | $4.37 for 5 spacers      | 4 spacers, or 4/5th of a unit ($3.50)    | 8 spacers, or 8/5th of a unit ($6.99)  | Home Depot       | https://www.homedepot.com/p/Hillman-Seamless-Steel-Spacers-1-4-in-I-D-x-3-8-in-O-D-x-1-2-in-Length-880414/204726284 |

Note that all monetary values are in U.S. dollars. The products specified may only be available in the United States, so costs may vary depending on your region. Also note that manufacturing a single tag (instead of in bulk) will likely result in a higher cost, as there will be leftover unused materials. When manufacturing multiple 1' AcTags, the cost per tag is around \$35, and when manufacturing multiple 2' AcTags, the cost per tag is around $124.50.

Use the AcTag BOM to buy the materials for your AcTag. Decide whether you want a 1' tag or a 2' tag, and then purchase the number of units necessary to built it. If a specific material is out-of-stock or not available in your region, feel free to find substitutes that fulfill the same specifications of the original product. 

To order the ``1 mm Aluminum Sheet (5052 or 6061) cut w/Tag Design``, you'll need to provide a ``.dxf`` file containing the shape of the black pixels on your AcTag. Refer to [Picking an Actag Family](./actag_families.md) for information on acquiring image files for the AcTags in your chosen family, and use the corresponding image to recreate the black tag face using CAD software. Note that if there are any "floating" data bits in the corners of your AcTag, you will need to connect these to the rest of the AcTag face in your CAD design. You can also add holes for screws to this CAD file, as explained in step #1 of the tag construction process below. Export this file to ``.dxf`` format, and it will now be ready for cutting with [SendCutSend](https://www.sendcutsend.com). Below is an example of an AcTag image file along with it's corresponding ``.dxf`` file:

<img src="../../actag_families/image_files/example_images/AcTagToDXFExample.png" alt="An AcTag Image file to it's corresponding .dxf file.">

Note that although ordering through [SendCutSend](https://www.sendcutsend.com) is a convenient option, there may be cheaper alternatives. For example, buying uncut sheets of aluminum and having them cut using a water jet could allow you to manufacture AcTag faces at a lower cost. However, this will depend on the availability and cost of these services and materials in your area. Feel free to use any method you like to manufacture your AcTag faces.

Once you have the materials, follow the instruction below to build your AcTag:

1. Drill holes in the ``1 mm Aluminum Sheet (5052 or 6061) cut w/Tag Design``, which I'll refer to as the "tag face". The holes should have a diameter of  around 0.138" (9/64") so that the ``#6 x 1 in. inch Metal Screws`` will fit in them. For 1' tags, you'll need four holes for each of the corner black pixels. For 2' tags, you'll need four holes for each of the corner black pixels, and four more holes that are in-between the corner holes.

2. Take the ``Thick Aluminum ACM Sheet`` (which I'll call the "tag back") and put it behind the tag face. Line them up so that the edges of the tag back match up with the edges of the data bits on the tag face. Then, drill holes in the tag back to match the holes in the tag face. Make sure that the holes line up between both sheets.

3. Take the ``1/2" Acoustic Foam`` and use an [electric knife](https://www.amazon.com/BLACK-DECKER-Electric-Carving-EK500B/dp/B01K1JJAI2/ref=asc_df_B01K1JJAI2/?tag=hyprod-20&linkCode=df0&hvadid=167145808484&hvpos=&hvnetw=g&hvrand=2169805846443213337&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9029858&hvtargid=pla-307386551262&psc=1) to cut it to the size of the tag back. Line up the edges of the acoustic foam with the edges of the tag back. If the acoustic foam comes with sticky adhesive, you can attach the foam to the tag back.

4. Using the holes in the tag back as a guide, make holes in the acoustic foam for the ``1/2" Steel Spacers``. Slot a steel spacer into each hole.

5. Re-align the tag face with the tag back (with the acoustic foam and steel spacers in between). Use the ``#6 x 1 in. inch Metal Screws`` and the ``#6-32 Steel Cap Nuts`` to connect the tag face to the tag back. The screws should be put through the tag face, with the cap nuts on the tag back. 

Congratulations, your AcTag is complete! It is ready to be viewed by a sonar and a camera, so feel free to start [capturing footage](actag_usage.md) of your AcTag. When you are ready to detect your AcTag with an imaging sonar or camera, see [Detecting AcTags](actag_detection.md) for more information.

(markdown-header-modifying-actags)=
## Modifying AcTags
There are many reasons why you would want to modify your AcTag. Perhaps you want to save money by using multiple different tag faces with one tag back. You may want to attach a weight or a mounting surface to an AcTag to help it stay underwater, or you may want to attach a buoy to avoid losing it. Whatever the reason, AcTags are pretty easy to customize.

To customize an AcTag, you'll want to seperate the tag back from the rest of the materials. First, unscrew the tag face from the tag back and set aside the screws and nuts. Remove the steel spacers from the foam. If it's possible to remove the foam, do so.

Now that you have your tag back, you can drill holes in it and add custom designed modules for your specific purpose, whether it be a weight, a mounting surface, a buoy connection, or something else. We know that each robotic application is unique so we encourage modification of the AcTags for your specific use cases, noting that the tag face should remain unmodified to ensure tag detection is uncompromised.

Once you are finished adding any custom modules, replace the steel spacers (and the foam if it was removed). Using the screws and the cap nuts, reattach the tag face to the tag back. Now, you are ready to use your customized AcTag.