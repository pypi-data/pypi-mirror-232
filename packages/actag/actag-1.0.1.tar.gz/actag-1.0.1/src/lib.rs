use pyo3::prelude::*;
use ndarray::prelude::*;

// Declare all submodules here
pub mod filters;
pub mod contours;
pub mod quad_fitting;
pub mod tag_detection;

// Convenience function to convert from a vector of vectors to a ndarray
fn vec_tup_to_arr2_f32(vec: Vec<(f64, f64)>) -> ndarray::Array2<f64> {
    let mut arr = ndarray::Array2::zeros((vec.len(), 2));
    for i in 0..vec.len() {
        arr[[i, 0]] = vec[i].0;
        arr[[i, 1]] = vec[i].1;
    }
    arr
}

// Convenience function to convert from a ref vector of vectors to a ndarray
fn vec_tup_to_arr2_f32_ref(vec: &Vec<(f64, f64)>) -> ndarray::Array2<f64> {
    let mut arr = ndarray::Array2::zeros((vec.len(), 2));
    for i in 0..vec.len() {
        arr[[i, 0]] = vec[i].0;
        arr[[i, 1]] = vec[i].1;
    }
    arr
}

// Convenience function to convert from a vector of vectors to a ndarray
pub fn vec2_to_arr2_i32(vec: Vec<Vec<i32>>) -> Array2<i32> {
    let mut arr = Array2::zeros((vec.len(), vec[0].len()));
    for i in 0..vec.len() {
        for j in 0..vec[0].len() {
            arr[[i, j]] = vec[i][j];
        }
    }
    arr
}

// Convenience function to convert from a ndarray to a vector of vectors
pub fn arr2_to_vec2_i32(arr: Array2<i32>) -> Vec<Vec<i32>> {
    let mut vec = Vec::new();
    for i in 0..arr.shape()[0] {
        let mut row = Vec::new();
        for j in 0..arr.shape()[1] {
            row.push(arr[[i, j]]);
        }
        vec.push(row);
    }
    vec
}

// Convenience function to convert from a ndarray to a vector of vectors
pub fn arr2_to_vec2_i32_ref(arr: &Array2<i32>) -> Vec<Vec<i32>> {
    let mut vec = Vec::new();
    for i in 0..arr.shape()[0] {
        let mut row = Vec::new();
        for j in 0..arr.shape()[1] {
            row.push(arr[[i, j]]);
        }
        vec.push(row);
    }
    vec
}

// Flood fill a four connected area based around a seed pixel. Changes the values to a new value.
#[pyfunction]
pub fn flood_fill(mut image: Vec<Vec<i32>>, sr: i32, sc: i32, new_val: i32) -> Vec<Vec<i32>> {
    use std::collections::VecDeque;
    use std::convert::TryFrom;

    let sr = usize::try_from(sr).unwrap();
    let sc = usize::try_from(sc).unwrap();

    let initial_val = image[sr][sc];

    if initial_val == new_val {
        return image;
    }

    let height = image.len();
    let width = image[0].len();

    let mut cells: VecDeque<(usize, usize)> = VecDeque::new();
    cells.push_back((sr, sc));

    while let Some((sr, sc)) = cells.pop_front() {
        let cell = &mut image[sr][sc];

        if *cell != initial_val {
            continue;
        }

        *cell = new_val;

        const OFFSETS: &[(usize, usize)] = &[(0, usize::MAX), (usize::MAX, 0), (0, 1), (1, 0)];

        for (delta_r, delta_c) in OFFSETS.iter().copied() {
            let new_r = sr.wrapping_add(delta_r);
            let new_c = sc.wrapping_add(delta_c);

            if new_r < height && new_c < width {
                cells.push_back((new_r, new_c));
            }
        }
    }

    image
}

/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name = "rust_impl")]
fn actag_optimized_functions(_py: Python, m: &PyModule) -> PyResult<()> {
    // Add functions from filters module
    m.add_function(wrap_pyfunction!(filters::median_filter, m)?)?;
    m.add_function(wrap_pyfunction!(filters::median_filter_multithread, m)?)?;
    m.add_function(wrap_pyfunction!(filters::adaptive_threshold, m)?)?;
    m.add_function(wrap_pyfunction!(filters::adaptive_threshold_multithread, m)?)?;

    // Add functions from the contours module
    m.add_function(wrap_pyfunction!(contours::get_contours, m)?)?;
    m.add_function(wrap_pyfunction!(contours::plot_contours, m)?)?;

    // Add functions from the quad_fitting module
    m.add_function(wrap_pyfunction!(quad_fitting::get_intersection_of_lines, m)?)?;
    m.add_function(wrap_pyfunction!(quad_fitting::least_squares_line_fit_python_wrap, m)?)?;
    m.add_function(wrap_pyfunction!(quad_fitting::get_random_point_and_fit_line_python_wrap, m)?)?;
    m.add_function(wrap_pyfunction!(quad_fitting::fit_quadrilaterals_to_contours, m)?)?;

    // Add functions from the tag_detection module
    m.add_function(wrap_pyfunction!(tag_detection::get_data_bit_locations, m)?)?;
    m.add_function(wrap_pyfunction!(tag_detection::check_quad_for_tag_python_wrap, m)?)?;
    m.add_function(wrap_pyfunction!(tag_detection::decode_tags, m)?)?;
    m.add_function(wrap_pyfunction!(tag_detection::convert_tag_detections_to_range_azi_locations, m)?)?;

    // Return Ok
    Ok(())
}