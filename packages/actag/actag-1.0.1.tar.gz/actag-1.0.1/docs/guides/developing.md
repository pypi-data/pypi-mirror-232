# Developing AcTag

The [actag repository](https://bitbucket.org/frostlab/actag/src/master/) is an open-source library licensed under the [BSD 2-Clause License](https://bitbucket.org/frostlab/actag/src/master/LICENSE.md). As such, we encourage users to alter the code to fit their needs and to contribute back to the repository. This guide will explain how to make [modifications](#modifying-actag) to the code and how to [contribute](#contributing-to-actag) changes to our open-source library.

## Modifying AcTag

If you will only be making changes on your own machine, and have no intention of having those changes be added into the repository later on, then either download or clone the [actag](https://bitbucket.org/frostlab/actag/src/master/) repository. 
If you would like to make changes and have them incorporated into the [actag](https://bitbucket.org/frostlab/actag/src/master/) repository then please fork the repository and refer to the [Contributing to AcTag](#contributing-to-actag) section of this page.

The repository is split up into three main sections: 

- [Detection](#detection): The code that detects AcTags in sonar imagery. 
- [Generation](#generation): The code that generates AcTag families.
- [Documentation](#documentation): The code that generates the documentation for the repository.

Please see the corresponding section below for infomation on how to modify each corresponding section of the codebase.

### Detection

The detection code for AcTag is split up between two different folders. The [python](https://bitbucket.org/frostlab/actag/src/master/python/actag/) folder contains [Python](https://docs.python.org/3/) code for detecting AcTags, and the [src](https://bitbucket.org/frostlab/actag/src/master/src/) folder contains [Rust](https://www.rust-lang.org/learn) code that mimics the functionality of the Python code. Why are there two identical versions of the code, you may ask? The answer is that the Python code is much easier to develop with, but the Rust code runs significantly faster. Therefore, we recommend that you start by modifying the Python code. Later, if you need better performance, you can replicate those changes on the Rust side. 


#### Rebuilding
To run any modifications, you will need to reinstall the AcTag library into your Python environment. To do so, run the following commands from the root of the repository:

```bash
pip uninstall actag
maturin build --release
pip install target/wheels/*.whl
```

*NOTE: If you are familiar with maturin, you may be tempted to run ```maturin develop --release``` instead of the previous three commands. However, this fundamentally alters the file structure of the python library, leading to a ``FileNotFoundError`` when you try to load your AcTag family files. For this reason, running ```maturin develop --release``` is currently unsupported.*

If you want to test Python modifications, you will need to set the ```use_optimized_rust_code``` parameter of the {class}`AcTag <actag.AcTag>` class to ```False```. Otherwise, the algorithm will run the Rust code instead of the Python code. For example:

```python
from actag import AcTag

detector = AcTag(min_range=0.1, max_range=1.5, horizontal_aperture=1.0472, 
                 tag_family="AcTag24h10", tag_size=0.130628571428644, 
                 use_optimized_rust_code=False)
```

Remember to set this value back to ```True``` if you want to test any Rust modifications. 

#### Test Cases

If you decide that you want to develop first in Python and then replicate your changes in Rust, there is a helpful file that can be used to guarantee identical output between the two versions. [test_cases.py](https://bitbucket.org/frostlab/actag/src/master/tests/test_cases.py) runs multiple tests cases that matches up the output between the Python and Rust functions. If you make any modifications to both the Rust and Python versions of a function, you can run this file to make sure that their outputs are still identical. *NOTE: One of the unit tests, ```test_get_tags_in_family()```, compares the returns of the {meth}`AcTagParams.get_tags_in_family <actag.tag_parameters.AcTagParams.get_tags_in_family>` function to pre-determined values in the [test_data](https://bitbucket.org/frostlab/actag/src/master/tests/test_data/) folder. This test will fail by default if you make any changes to that function.*

You can run the [test_cases.py](https://bitbucket.org/frostlab/actag/src/master/tests/test_cases.py) file by running the following command in the root directory of the [actag](https://bitbucket.org/frostlab/actag/src/master/) repository, after [rebuilding](#rebuilding) the library:

```bash
python tests/test_cases.py
```

If you want to write test cases for just the Rust code, you can place your ```rs``` test files in the [tests](https://bitbucket.org/frostlab/actag/src/develop/tests/) folder, and then run the following command in the root directory of the [actag](https://bitbucket.org/frostlab/actag/src/master/) repository:

```bash
cargo test --no-default-features
```

NOTE: It is not necessary to [rebuild](#rebuilding) the library before running these tests, as the ```cargo test``` command builds the Rust code automatically.

### Generation

The [actag_families](https://bitbucket.org/frostlab/actag/src/master/actag_families/) folder contains all of the code for generating custom AcTag families. This module is written in Java, and was originally released as part of the [apriltag-generation](https://github.com/AprilRobotics/apriltag-generation) repository. Here, the code has been further modified to work with AcTag and to be more user-friendly. Most notably, when determining the hamming distance of a potential tag family member to any of the tags in the current family, our version considers possible tag reversals in addition to tag rotations. This is necessary due to the fact that the data bits in an AcTag can be rotated AND reversed when viewed by a sonar, which isn't possible with a camera.

The generation code can be found in the [actag_families/src/april](https://bitbucket.org/frostlab/actag/src/master/actag_families/src/april/) folder, and can be built by running the ```ant``` command in the [actag_families](https://bitbucket.org/frostlab/actag/src/master/actag_families/) folder. However, because the [generateAcTags.sh](https://bitbucket.org/frostlab/actag/src/master/actag_families/generateAcTags.sh) script runs the ```ant``` command automatically, you can also just run that script to build the code. For information on running the script, please see [Picking an AcTag Family](actag_families.md).

After generating, most of the Actag family files can be found in the [actag_families](https://bitbucket.org/frostlab/actag/src/master/actag_families/) folder. The image files will be located in the ["actag_families/image_files/"](https://bitbucket.org/frostlab/actag/src/master/actag_families/image_files/) folder, and the C files for use with [apriltag](https://github.com/AprilRobotics/apriltag) will be located in the ["actag_families/actag_files_for_apriltag/"](https://bitbucket.org/frostlab/actag/src/master/actag_families/actag_files_for_apriltag/) folder. However, the java file for the AcTag family will instead be found in the ["python/actag/generated_families/"](https://bitbucket.org/frostlab/actag/src/master/python/actag/generated_families/) folder. This is because the java files need to be located in the same directory as the detection code for them to be included when the library is [built](#rebuilding).

This means that if you want to pass your custom AcTag family to the {class}`AcTag <actag.AcTag>` class by name (ex. ```AcTag16h4```), and not with a file path, you can simply [rebuild](#rebuilding) the detection code to make this possible.

### Documentation

The [docs](https://bitbucket.org/frostlab/actag/src/master/docs/) folder contains all of the code for generating documentation for the library. The documentation is generated using [Sphinx](https://www.sphinx-doc.org/en/master/), uploaded to [readthedocs](https://actag.readthedocs.io/en/latest/), and built with the provided [.readthedocs.yaml](https://bitbucket.org/frostlab/actag/src/master/.readthedocs.yaml) file. It also uses the [sphinx_rtd_theme](https://sphinx-rtd-theme.readthedocs.io/en/stable/).

#### Setup

Download the [actag](https://bitbucket.org/frostlab/actag/src/master/) repository, and install any dependencies for the docs by running the following command from the root folder:

```bash
pip install -r docs/requirements.txt
```

#### Build

Navigate to the [docs](https://bitbucket.org/frostlab/actag/src/master/docs/) folder and run the following command to build the documentation locally:

```bash
make html
```

To view the documentation, open the new ```index.html``` file, which should be located in the ```docs/build/html/``` folder.

#### Modifying

Our documentation is written using [Markedly Structured Text (MyST)](https://myst-parser.readthedocs.io/en/latest/), which is an extended version of Markdown that supports integration with sphinx features. Files that use this format are [index.md](https://bitbucket.org/frostlab/actag/src/master/docs/index.md), [guides](https://bitbucket.org/frostlab/actag/src/master/docs/guides/), and [internal documentation](https://bitbucket.org/frostlab/actag/src/master/docs/internal_documentation/).

Most of the function and class documentation is written in the Python and Rust files themselves as docstrings. These docstrings are written in [reStructuredText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html), and follow our own [Docstring Standard](../internal_documentation/coding_standard.md). Please follow the standard when editing or writing new docstrings.

## Contributing to AcTag

If you would like to contribute to AcTag, thank you! Your efforts make this open-source repository better for everyone. To contribute, simply submit a pull request on [Bitbucket](https://bitbucket.org/frostlab/actag/pull-requests/). However, before your submit your request, please review the following instructions to make sure your code lines up with the rest of the repository:

- If you have made changes to the [detection](#detection) code, it is ideal for the changes to be replicated on both the Python and Rust sides of the code. In addition, comprehensive test cases assuring identical output between the two versions of the code should be added to the [test_cases.py](https://bitbucket.org/frostlab/actag/src/master/tests/test_cases.py) file if the current test cases aren't comprehensive enough. When run, all of the test cases should pass.

- For the [generation](#generation) code, any code that changes the AcTags in an AcTag family will be rejected, as we want to keep the tags in each family consistent. However, any other changes, like optimizations, bug fixes, or quality-of-life improvements, are more than welcome!

- Changes to the [detection](#detection) or [generation](#generation) code should be represented with changes to the [documentation](#documentation). Docstrings must follow the [Docstring Standard](../internal_documentation/coding_standard.md).

If your pull request is missing any of the above requirements, it's likely that the merging of your code may be delayed or rejected, as we will have to personally edit your code so that it fits the above requirements. In addition, some pull requests may not be merged if they deviate from the main goal of the [actag](https://bitbucket.org/frostlab/actag/src/master/) repository. However, even if you can't fulfill all of the requirements, we recommend that you submit the pull request anyway! We will do the best we can within our means to incorporate improvements from the community.

If you have any further questions about developing or contributing to AcTag, please [contact us](../index.md#contact-us).