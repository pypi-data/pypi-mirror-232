# Docstring Standard

This is the coding standard used for writing Docstrings for Sphinx, using the [Sphinx docstring format](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html#the-sphinx-docstring-format). Note that there is currently no standard for the code itself, or the inline comments.

## General

1. Each function and class needs a description, and each parameter for each class needs a ```:param:``` and ```:type:``` description. If the function returns something, it should have a ```:return:``` and ```:rtype:``` description. If it returns nothing, it should only have a ```:return:``` description to specify that ```None``` is returned. A class should have no ```return:``` or ```rtype:``` description. Finally, use the ```:raises:``` description to specify any exceptions that may be raised. It should start with the words ```Raised if...```.

2. Each function, class, ```:param:```, ```:return:```, and  ```:raises:``` description should follow [sentence case](https://en.wikipedia.org/wiki/Letter_case#Sentence_case) and end each clause or sentence with a period.

3. Each ```:type:``` and ```:rtype:``` description should contain the type of the parameter without anything else. There should be no period at the end, and the type shouldn't be capitalized unless the type itself is capitalized. If more detail is necessary, include this information in the ```:param:``` or ```:return:``` description.

4. Do not include raw links in docstrings. Instead, follow this guide to [link to external webpages](https://sublime-and-sphinx-guide.readthedocs.io/en/latest/references.html#links-to-external-web-pages).

5. When referencing other functions in the code, use the [:func:](https://stackoverflow.com/questions/71798784/sphinx-autodoc-how-to-cross-link-to-a-function-documented-on-another-page>) or ``:meth:`` directives:

```
:func:`actag.rust_impl.median_filter`
```

6. When referencing other parameters, surround them with double backticks to create the following effect: ```parameter```. Do the same for any calculations, code blocks, file paths, or other code-related text.

7. Add a space between the general function/class summary and the other descriptions.

### Python
1. Use ```'''``` when starting and ending docstrings. 

2. A function or class description should start on the line following the ```'''```, as shown below:

```python
'''
My description starts here...
```

3. The text in a docstring should all start at the same indentation level as the starting ```'''```. The
ending ```'''``` should also be on the same indentation level.

#### Example Python Docstring

```python
'''
`Median filter <https://en.wikipedia.org/wiki/Median_filter>`_ for 2D images.

:param img: 2D image.
:type img: np.ndarray
:param kernel_radius: Radius of the kernel.
:type kernel_radius: int
:return: Filtered image.
:rtype: np.ndarray
'''
```

### Rust

1. Use ```///``` to the left side of all docstrings. 

2. There should be no ```///``` above the beginning of the docstring, but there should
be a ```///``` below the ending of the docstring.

#### Example Rust Docstring

```rust
/// Rust equivalent of :func:`adaptive_threshold.adaptive_threshold_multiprocessed`.
/// 
/// :param data: 2D image.
/// :type data: Vec<Vec<i32>>
/// :param radius: Radius of the kernel.
/// :type radius: usize
/// :param offset: Offset value.
/// :type offset: f64
/// :param cpu_option: Number of CPUs to use. If ``None``, all available CPUs will be used.
/// :type cpu_option: Option<usize>
/// :return: Binarized image.
/// :rtype: Vec<Vec<i32>>
/// 
```
