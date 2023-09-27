# AcTag: Opti-Acoustic Fiducial Markers for Underwater Localization and Mapping

[![Build Status](https://robots.et.byu.edu:4000/api/badges/frostlab/actag/status.svg)](https://robots.et.byu.edu:4000/frostlab/actag)
[![Documentation Status](https://readthedocs.org/projects/actag/badge/?version=latest)](https://actag.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/actag.svg)](https://badge.fury.io/py/actag)

```{toctree}
:hidden:
guides/quickstart.md
```

```{toctree}
:hidden:
:caption: Guides
guides/actag_families.md
guides/actag_construction.md
guides/actag_usage.md
guides/actag_detection.md
guides/developing.md
```

```{toctree}
:hidden:
:maxdepth: 4
:caption: Code Documentation
internal_documentation/actag_classes.md
internal_documentation/filtering.md
internal_documentation/adaptive_threshold.md
internal_documentation/contour_identification.md
internal_documentation/quad_fitting.md
internal_documentation/tag_decoding.md
internal_documentation/coding_standard.md
```

<img src="../actag_families/image_files/example_images/AcTagExampleUsage.png" alt="Hovering Autonomous Underwater Vehicle (AUV) in water with an AcTag. Examples of acoustic and optical output of tag detection are also shown.">

AcTag is a novel opti-acoustic fiducial marker that can be detected in both optical and acoustic images. When seen through an imaging sonar, AcTags provide the unique identification of four individual landmarks per tag, and provide relative range and azimuth values to each landmark. When seen with a camera, AcTags provide a valid 6-DOF pose estimate through the use of the [apriltag](https://github.com/AprilRobotics/apriltag) repository. In addition, AcTags are cheap, easy to manufacture, and can be easily detected with this open-source repository. Therefore, we believe that AcTag has significant potential to improve underwater robotic localization and mapping by enabling accurate tracking of objects in underwater environments.

<img src="../actag_families/image_files/example_images/AcTagFullLayout.png" alt="The physical and pixel layout of an AcTag.">

Physically, AcTags consist of a 1 mm aluminum face plate, a 12 mm layer of acoustic foam, and a back plate of thick aluminum or ACM. The face plate is cut with the tag ID pattern, the acoustic foam scatters sounds waves, and the back plate provides weight and structural integrity. A physical AcTag is shown in (a). This design causes the pixel layout of the AcTag to appear within the views of an imaging sonar and a camera.

The pixel layout of an AcTag consists of a center region of white pixels surrounded by a black square of pixels. The data bits then form a single pixel-wide square around the outer edge. An example AcTag with each of the pixels labeled is shown in (b); where ’d’ denotes a data bit, ’k’ a black bit, and ’w’ a white bit. This pixel layout allows for the AcTags to be detected and decoded by our [AcTag detection algorithm](./guides/actag_detection.md) and the [apriltag](https://github.com/AprilRobotics/apriltag) repository.

Head on over the [Quickstart](./guides/quickstart.md) guide in order to learn how to detect AcTags. Or, take a look at the [actag repository](https://bitbucket.org/frostlab/actag/src/master/) on BitBucket.

## Contact Us

For questions or inquiries, feel free to reach out to the team:

- [Kalin Norman](https://frostlab.byu.edu/directory/kalin-norman)
- [Daniel Butterfield](https://frostlab.byu.edu/directory/daniel-butterfield)
- [Frost Lab](https://frostlab.byu.edu/)