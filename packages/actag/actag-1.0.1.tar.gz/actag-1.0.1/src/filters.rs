use pyo3::prelude::*;
use ndarray::prelude::*;
use ndarray::OwnedRepr;
use ndarray::s;
use std::cmp;

// This helper function pads a vector image according to the "edge" scheme
fn pad_edge_vector(data: &Vec<Vec<i32>>, radius: usize) -> Vec<Vec<i32>> {
    let mut padded_data = data.clone();

    let first_val = padded_data[0].clone();
    let last_val = padded_data[padded_data.len() - 1].clone();
    for _i in 0..radius {
        padded_data.insert(0, first_val.clone());
        padded_data.push(last_val.clone());
    }

    for i in 0..padded_data.len() {
        let first_val = padded_data[i][0];
        let last_val = padded_data[i][padded_data[i].len() - 1];
        for _j in 0..radius {
            padded_data[i].insert(0, first_val);
            padded_data[i].push(last_val);
        }
    }
    padded_data
}

// This helper function does the opposite of pad_edge_vector()
fn unpad_edge_vector(filtered_vec: &Vec<Vec<i32>>, radius: usize) -> Vec<Vec<i32>> {
    let mut result = Vec::new();
    for i in radius..(filtered_vec.len()-radius) {
        let mut result_row = Vec::new();
        for j in radius..(filtered_vec[0].len()-radius) {
            result_row.push(filtered_vec[i][j])
        }
        result.push(result_row);
    }
    result
}

/// Rust equivalent of :func:`actag.median_filter.median_filter`.
///
/// :param data: 2D image.
/// :type img: Vec<Vec<i32>>
/// :param radius: Radius of the kernel.
/// :type radius: usize
/// :return: Filtered image.
/// :rtype: Vec<Vec<i32>>
///
#[pyfunction]
pub fn median_filter(data: Vec<Vec<i32>>, radius: usize) -> Vec<Vec<i32>> {
    // Pad the input data with the shape of radius
    let padded_data = pad_edge_vector(&data, radius);

    // Initialize input array and output array for the median filter
    let arr = crate::vec2_to_arr2_i32(padded_data);
    let mut filtered = ndarray::Array2::zeros((arr.shape()[0], arr.shape()[1]));

    // Iterate through each pixel
    for i in 0..arr.shape()[0] {
        for j in 0..arr.shape()[1] {
            // Get slice indices, ensuring they don't go out of bounds
            let r1 = cmp::max(0, i as i32 - radius as i32) as usize;
            let r2 = cmp::min((arr.shape()[0] as i32) - 1, i as i32 + radius as i32) as usize;
            let c1 = cmp::max(0, j as i32 - radius as i32) as usize;
            let c2 = cmp::min((arr.shape()[1] as i32) - 1, j as i32 + radius as i32) as usize;
            // Get the window of appropriate radius size
            let window = arr.slice(s![r1..=r2, c1..=c2]);
            let mut window_1d: Vec<&i32> = window.iter().collect();
            window_1d.sort();
            // Get the median value and update the output array
            let median = match window_1d.len() % 2 {
                0 => (*window_1d[window_1d.len() / 2] as f32 + *window_1d[window_1d.len() / 2 - 1] as f32) / 2.,
                _ => *window_1d[window_1d.len() / 2] as f32
            };
            filtered[[i, j]] = median as i32;
        }
    }
    let filtered_vec = crate::arr2_to_vec2_i32(filtered);

    // Crop the image to remove the outer padding used for the filter
    unpad_edge_vector(&filtered_vec, radius)
}

/// Rust equivalent of :func:`actag.median_filter.median_filter_multiprocessed`.
///
/// :param data: 2D image.
/// :type img: Vec<Vec<i32>>
/// :param radius: Radius of the kernel.
/// :type radius: usize
/// :param cpu_option: The number of CPUS to use. If None, all available CPUs will be used.
/// :type cpu_ooption: Option<usize>
/// :return: Filtered image.
/// :rtype: Vec<Vec<i32>>
///
#[pyfunction]
pub fn median_filter_multithread(data: Vec<Vec<i32>>, radius: usize, cpu_option: Option<usize>) -> Vec<Vec<i32>> {
    // Pad the input data with the shape of radius
    let padded_data = pad_edge_vector(&data, radius);

    // Initialize input array and output array
    let arr = crate::vec2_to_arr2_i32(padded_data);
    let mut filtered = ndarray::Array2::zeros((arr.shape()[0], arr.shape()[1]));

    // Get available cpus
    let available_cpus = num_cpus::get();

    // Determine number of threads to use
    let threads = match cpu_option {
        Some(cpus) => if cpus < available_cpus && cpus >= 1 { cpus } else { available_cpus },
        None => available_cpus
    };
    let rows_per_thread = (arr.shape()[0]/ threads) + 1;

    // Split the result image into bands
    let bands = filtered.axis_chunks_iter_mut(Axis(0), rows_per_thread);

    // Create a reference to the array to share across threads
    let arr_ref = &arr;

    // Run the median filter
    crossbeam::scope(|spawner| {
        // For each band...
        for (k, mut band) in bands.enumerate() {
            // Create the thread for this band
            spawner.spawn(
                move |_| {
                // Iterate through each pixel
                for i in 0..band.shape()[0] {
                    for j in 0..band.shape()[1] {
                        // Get slice indices, ensuring they don't go out of bounds
                        let r1 = cmp::max(0, (i+(k*rows_per_thread)) as i32 - radius as i32) as usize;
                        let r2 = cmp::min((arr_ref.shape()[0] as i32) - 1, (i+(k*rows_per_thread)) as i32 + radius as i32) as usize;
                        let c1 = cmp::max(0, j as i32 - radius as i32) as usize;
                        let c2 = cmp::min((arr_ref.shape()[1] as i32) - 1, j as i32 + radius as i32) as usize;
                        // Get the window of appropriate radius size
                        let window = arr_ref.slice(s![r1..=r2, c1..=c2]);
                        let mut window_1d: Vec<&i32> = window.iter().collect();
                        window_1d.sort();
                        // Get the median value and update the output array
                        let median = match window_1d.len() % 2 {
                            0 => (*window_1d[window_1d.len() / 2] as f32 + *window_1d[window_1d.len() / 2 - 1] as f32) / 2.,
                            _ => *window_1d[window_1d.len() / 2] as f32
                        };
                        band[[i, j]] = median as i32;
                    }
                }
            });
        }
    }).unwrap();

    // Return the filtered image
    let filtered_vec = crate::arr2_to_vec2_i32(filtered);

    // Crop the image to remove the outer padding used for the filter
    unpad_edge_vector(&filtered_vec, radius)
}

/// Rust equivalent of :func:`actag.adaptive_threshold.adaptive_threshold`.
/// 
/// :param data: 2D image.
/// :type data: Vec<Vec<i32>>
/// :param radius: Radius of the kernel.
/// :type radius: usize
/// :param offset: Offset value.
/// :type offset: f64
/// :return: Binarized image.
/// :rtype: Vec<Vec<i32>>
/// 
#[pyfunction]
pub fn adaptive_threshold(data: Vec<Vec<i32>>, radius: usize, offset: f32) -> Vec<Vec<i32>> {
    // Initialize input and output arrays
    let arr = crate::vec2_to_arr2_i32(data);
    let mut binarized = ndarray::Array2::zeros((arr.shape()[0], arr.shape()[1]));

    // Iterate through each pixel
    for i in 0..arr.shape()[0] {
        for j in 0..arr.shape()[1] {
            // Get slice indices, ensuring they don't go out of bounds
            let r1 = cmp::max(0, i as i32 - radius as i32) as usize;
            let r2 = cmp::min((arr.shape()[0] as i32) - 1, i as i32 + radius as i32) as usize;
            let c1 = cmp::max(0, j as i32 - radius as i32) as usize;
            let c2 = cmp::min((arr.shape()[1] as i32) - 1, j as i32 + radius as i32) as usize;
            // Get the window of appropriate radius size
            let window = arr.slice(s![r1..=r2, c1..=c2]);
            let window_1d: Vec<&i32> = window.iter().collect();
            // Threshold is the mean of the window's extrema, including the offset
            let threshold = ((*window_1d.iter().min().unwrap() + *window_1d.iter().max().unwrap()) as f32 / 2.) - offset;
            // Assign the output to a 0 or 1, if it is below or above the threshold, respectively
            binarized[[i, j]] = match arr[[i, j]] as f32 >= threshold {
                true => 1,
                false => 0
            };
        }
    }
    // Return the binary array
    crate::arr2_to_vec2_i32(binarized)
}

/// Rust equivalent of :func:`actag.adaptive_threshold.adaptive_threshold_multiprocessed`.
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
#[pyfunction]
pub fn adaptive_threshold_multithread(data: Vec<Vec<i32>>, radius: usize, offset: f64, cpu_option: Option<usize>) -> Vec<Vec<i32>> {

    // Initialize input and output arrays
    let arr: ArrayBase<OwnedRepr<i32>, Dim<[usize; 2]>> = crate::vec2_to_arr2_i32(data);
    let mut binarized: ArrayBase<OwnedRepr<i32>, Dim<[usize; 2]>> = ndarray::Array2::zeros((arr.shape()[0], arr.shape()[1]));

    // Get available cpus
    let available_cpus = num_cpus::get();

    // Determine number of threads to use
    let threads = match cpu_option {
        Some(cpus) => if cpus < available_cpus && cpus >= 1 { cpus } else { available_cpus },
        None => available_cpus
    };
    let rows_per_thread = (arr.shape()[0]/ threads) + 1;

    // Split the result image into bands
    let bands = binarized.axis_chunks_iter_mut(Axis(0), rows_per_thread);

    // Create a reference to the array to share across threads
    let arr_ref = &arr;

    // Run the adaptive_threshold algorithm 
    crossbeam::scope(|spawner| {
        // For each band...
        for (k, mut band) in bands.enumerate() {
            // Create the thread for this band
            spawner.spawn(move |_| {
                // Iterate through each pixel
                for i in 0..band.shape()[0] {
                    for j in 0..band.shape()[1] {
                        // Get slice indices, ensuring they don't go out of bounds
                        let r1 = cmp::max(0, (i+(k*rows_per_thread)) as i32 - radius as i32) as usize;
                        let r2 = cmp::min((arr_ref.shape()[0] as i32) - 1, (i+(k*rows_per_thread)) as i32 + radius as i32) as usize;
                        let c1 = cmp::max(0, j as i32 - radius as i32) as usize;
                        let c2 = cmp::min((arr_ref.shape()[1] as i32) - 1, j as i32 + radius as i32) as usize;
                        // Get the window of appropriate radius size
                        let window = arr_ref.slice(s![r1..=r2, c1..=c2]);
                        let window_1d: Vec<&i32> = window.iter().collect();
                        // Threshold is the mean of the window's extrema, including the offset
                        let threshold = ((*window_1d.iter().min().unwrap() + *window_1d.iter().max().unwrap()) as f64 / 2.) - offset;
                        // Assign the output to a 0 or 1, if it is below or above the threshold, respectively
                        band[[i, j]] = match arr_ref[[(i+(k*rows_per_thread)), j]] as f64 >= threshold {
                            true => 1,
                            false => 0
                        };
                    }
                }
            });
        }
    }).unwrap();

    // Return the binary array
    crate::arr2_to_vec2_i32(binarized)
}
