use std::ops::Mul;
use nalgebra::{linalg::SVD, matrix, Matrix3xX};
use rug::float::Round;
use rug::Float;
use pyo3::prelude::*;

/// Rust equivalent of :func:`actag.tag_decoding.get_data_bit_locations`.
/// 
/// :param quad: The quadrilateral to use as the central white square of the AcTag.
/// :type quad: Vec<(i64, i64)>
/// :param data_bits: The number of data bits in the AcTag family.
/// :type data_bits: u64
/// :return: The locations of the data bits in the sonar image.
/// :rtype: Vec<(u64, u64)>
/// 
#[pyfunction]
pub fn get_data_bit_locations(quad: Vec<(i64, i64)>, data_bits: u64) -> Vec<(u64, u64)> {
    // Given the tag parameters, determine the coordinates of the tag corners
    let tag_pixels_across = (data_bits + 4) / 4;
    let tag_corner_coordinates = matrix![
        2.0, 2.0, (tag_pixels_across - 2) as f64, (tag_pixels_across - 2) as f64;
        2.0, (tag_pixels_across - 2) as f64, (tag_pixels_across - 2) as f64, 2.0;
        1.0, 1.0, 1.0, 1.0];

    // Ensure the tag corner coordinates from the image are in the correct format
    let sonar_image_coordinates = matrix![
        quad[0].0 as f64, quad[1].0 as f64, quad[2].0 as f64, quad[3].0 as f64;
        quad[0].1 as f64, quad[1].1 as f64, quad[2].1 as f64, quad[3].1 as f64;
        1.0, 1.0, 1.0, 1.0];

    // Solve for the homography where sonar_coords = H @ tag_coords, so H = sonar_coords @ pinv(tag_coords)
    let tag_points_inv = SVD::new(tag_corner_coordinates, true, true).pseudo_inverse(1e-13).unwrap();
    let mut h = sonar_image_coordinates * tag_points_inv;

    // Round homography to 8 decimal places, so that it's identical to Python
    for i in 0..h.len() {
        h[i] = (h[i] * 1e8 as f64).round() / 1e8; 
    }

    // Create the array of data bit locations in the tag image
    let tag_dim = (data_bits + 4) / 4;
    let mut data_bit_tag_coords = Matrix3xX::from_element(data_bits as usize, 1.0);
    let mut col_idx = 0;
    for i in 0..(tag_dim-1) {
        data_bit_tag_coords[col_idx] = 0.5;
        data_bit_tag_coords[1 + col_idx] = 0.5 + (i as f64);
        col_idx += 3;
    }
    for i in 0..(tag_dim-1) {
        data_bit_tag_coords[col_idx] = 0.5 + (i as f64);
        data_bit_tag_coords[1 + col_idx] = (tag_dim as f64) - 0.5;
        col_idx += 3;
    }
    for i in 0..(tag_dim-1) {
        data_bit_tag_coords[col_idx] = (tag_dim as f64) - 0.5;
        data_bit_tag_coords[1 + col_idx] = (tag_dim as f64) - 0.5 - (i as f64);
        col_idx += 3;
    }
    for i in 0..(tag_dim-1) {
        data_bit_tag_coords[col_idx] = (tag_dim as f64) - 0.5 - (i as f64);
        data_bit_tag_coords[1 + col_idx] = 0.5;
        col_idx += 3;
    }

    // Map the data bit locations into the sonar image
    let data_bit_sonar_img_vals = h.mul(&data_bit_tag_coords);

    // Round to nearest integer values and return
    let mut data_bit_sonar_img_vals_rounded = Vec::new();
    for i in 0..data_bits {
        let x = data_bit_sonar_img_vals[(3*i) as usize];
        let y = data_bit_sonar_img_vals[(3*i+1) as usize];
        let x_rounded = Float::with_val(64, x);
        let y_rounded = Float::with_val(64, y);
        data_bit_sonar_img_vals_rounded.push((x_rounded.to_u32_saturating_round(Round::Nearest).unwrap() as u64, 
                                              y_rounded.to_u32_saturating_round(Round::Nearest).unwrap() as u64));
    }

    // Return the data bit locations in the sonar image
    data_bit_sonar_img_vals_rounded
}

/// Rust equivalent of :func:`actag.tag_decoding.check_quad_for_tag`.
///
/// :param binary_img: The binarized sonar image to search for tags in.
/// :type binary_img: &Vec<Vec<i32>>
/// :param corner_points: The corners of the quadrilateral.
/// :type corner_points: mut Vec<(i64, i64)>
/// :param data_bit_cords: The locations of the data bits for the potential tag in the sonar image.
/// :type data_bit_cords: &Vec<(u64, u64)>
/// :param tags_in_family: The data bits of all of the tags in the AcTag family, including rotations and reversals.
/// :type tags_in_family: &Vec<Vec<i32>>
/// :param bit_corrections_allowed: The number of bit corrections to allow when checking for a tag.
/// :type bit_corrections_allowed: u64
/// :return: A vector of any tags that were found in this quad. Each tag is a vector, with the first element being the tag_id, followed by the row value of the first point, followed by the column value of the first point, and then followed by the second, third and fourth points in the same way.
/// :rtype: Vec<Vec<u64>>
/// 
pub fn check_quad_for_tag(binary_img: &Vec<Vec<i32>>, mut corner_points: Vec<(i64, i64)>, data_bit_cords: &Vec<(u64, u64)>,
                  tags_in_family: &Vec<Vec<i32>>, bit_corrections_allowed: u64) -> Vec<Vec<u64>> {

    // Get height and width of binary image
    let img_height: u64 = binary_img.len() as u64;
    let img_width: u64 = binary_img[0].len() as u64;

    // Extract the data bits from the binary image 
    let mut decoded_data_bits = Vec::new();
    for &(r, c) in data_bit_cords {
        if r >= img_height || c >= img_width {
            // Data bit out of bounds, so tag partially obscured
            // Therefore, we can't decode this tag
            return Vec::new();
        }
        decoded_data_bits.push(binary_img[r as usize][c as usize]);
    }
    
    // Compare decoded data bits to the tags in the family
    let mut decoded_tags = Vec::new();
    let num_in_fam = tags_in_family.len() / 8;
    let num_in_fam_rev = tags_in_family.len() / 2;
    for i in 0..(tags_in_family.len()) {
        let mut hamming_dist: u64 = 0;
        // Calulate the hamming distance between the decoded data bits and the tag in the family
        for j in 0..(tags_in_family[i].len()) {
            hamming_dist += (tags_in_family[i][j] ^ decoded_data_bits[j]) as u64;
        }

        // If the hamming distance less than or equal to the maximum allowed, it has been successfully decoded
        if hamming_dist <= bit_corrections_allowed {             
            // A decoded tag contains the following information -
            // [tag_id, pt1row, pt1col, pt2row, pt2col, pt3row, pt3col, pt4row, pt4col]
            let mut decoded_tag = Vec::new();

            // Flip the corner points if the tag is upside down
            if i >= num_in_fam_rev {
                // Roll the points based on how rotated the tag is
                for _j in 0..(8 - ((i / num_in_fam) as i64)) {
                    let temp = corner_points.pop().unwrap();
                    corner_points.insert(0, temp);
                }

                let temp = corner_points[3].clone();
                corner_points[3] = corner_points[1];
                corner_points[1] = temp;
            }
            else { 
                // Roll the points based on how rotated the tag is
                for _j in 0..((i / num_in_fam) as i64) {
                    let temp = corner_points.pop().unwrap();
                    corner_points.insert(0, temp);
                }
            }

            // Create the decoded tag
            decoded_tag.push((i % num_in_fam) as u64);
            for j in 0..(corner_points.len()) {
                decoded_tag.push(corner_points[j].0 as u64);
                decoded_tag.push(corner_points[j].1 as u64);
            }
            
            // Push the tag to the list of decoded tags
            decoded_tags.push(decoded_tag);
        }
    }

    // Return the result
    decoded_tags
}

/// Rust equivalent of :func:`actag.tag_decoding.check_quad_for_tag`. Note that this function does 
/// not return the range and azimuth values of the tag corners, as the Python version does.
///
/// :param binary_img: The binarized sonar image to search for tags in.
/// :type binary_img: Vec<Vec<i32>>
/// :param corner_points: The corners of the quadrilateral.
/// :type corner_points: Vec<(i64, i64)>
/// :param data_bit_cords: The locations of the data bits for the potential tag in the sonar image.
/// :type data_bit_cords: Vec<(u64, u64)>
/// :param tags_in_family: The data bits of all of the tags in the AcTag family, including rotations and reversals.
/// :type tags_in_family: Vec<Vec<i32>>
/// :param bit_corrections_allowed: The number of bit corrections to allow when checking for a tag.
/// :type bit_corrections_allowed: u64
/// :return: A vector of any tags that were found in this quad. Each tag is a vector, with the form ``[tag_id, pt1_row, pt1_col, pt2_row, pt2_col, pt3_row, pt3_col, pt4_row, pt4_col]``.
/// :rtype: Vec<Vec<u64>>
/// 
#[pyfunction]
pub fn check_quad_for_tag_python_wrap(binary_img: Vec<Vec<i32>>, corner_points: Vec<(i64, i64)>, data_bit_cords: Vec<(u64, u64)>,
                  tags_in_family: Vec<Vec<i32>>, bit_corrections_allowed: u64) -> Vec<Vec<u64>> {
    check_quad_for_tag(&binary_img, corner_points, &data_bit_cords, &tags_in_family, bit_corrections_allowed)
}

/// '''
/// Takes a filtered image and list of quads, and returns all
/// of the successfully decoded tags.
///
/// Arguments: binary_img - the binary image to decode the potential tag from
///            quads - each of the quads (with their four corner points) which will be 
///                    potentially decoded as tags
///            tags_in_family - all of the tag in the family (as their data bits), including
///                             rotations and reversals
///            bit_corrections_allowed - the maximum number of data bit errors to correct
///                                 when decoding tags
///            horizontal_aperture - the horizontal aperture of the sonar in radians
///            min_range - the minimum range of the sonar
///            max_range - the maximum range of the sonar
///            data_bits - the number of data bits in the tag
///
/// Returns: Vec<Vec<u64>> - A vector that contains the decoded tags. Each tag is a vector, with
///                          the first element being the tag_id, followed by the row value of the 
///                          first point, followed by the column value of the first point, and then
///                          followed by the second, third and fourth points in the same way.
/// '''
pub fn tag_detection(binary_img: &Vec<Vec<i32>>, quads: Vec<Vec<(i64, i64)>>, 
                     tags_in_family: &Vec<Vec<i32>>, bit_corrections_allowed: u64,
                     data_bits: u64) -> Vec<Vec<u64>> {

    // For each quad, try to decode a tag
    let mut decoded_tags = Vec::new();
    for (_i, quad) in quads.into_iter().enumerate() {
        let quad_c = quad.clone();

        // Get data bit locations
        let cds = get_data_bit_locations(quad, data_bits);
        
        // Check if the quad contains a tag
        let mut tags_detected = check_quad_for_tag(binary_img, quad_c, &cds, tags_in_family, bit_corrections_allowed);
        
        if tags_detected.len() > 0 {
            decoded_tags.append(& mut tags_detected);
        }
    }
    decoded_tags
}

/// Takes the newly detected tags and appends the range and azimuth information for each of the points.
///
/// :param detected_tags: A vector of the detected tags. Each tag is a vector, with the form ``[tag_id, pt1_row, pt1_col, pt2_row, pt2_col, pt3_row, pt3_col, pt4_row, pt4_col]``.
/// :type detected_tags: Vec<Vec<u64>>
/// :param img_shape: The shape of the image in ``(rows, cols)`` format.
/// :type img_shape: (i64, i64)
/// :param min_range: The minimum range of the sonar.
/// :type min_range: f64
/// :param max_range: The maximum range of the sonar.
/// :type max_range: f64
/// :param horizontal_aperture: The horizontal aperture of the sonar in radians.
/// :type horizontal_aperture: f64
///
/// :return: A vector containing all of the decoded tags found in the image. Each tag is a vector, with the form ``[tag_id, pt1_row, pt1_col ... pt4_row, pt4_col, pt1_range, pt1_azi ... pt4_range, pt4_azi]``.
/// :rtype: Vec<Vec<f64>>
/// 
#[pyfunction]
pub fn convert_tag_detections_to_range_azi_locations(detected_tags: Vec<Vec<u64>>, img_shape: (i64, i64), 
                                                     min_range: f64, max_range: f64, mut horizontal_aperture: f64) -> Vec<Vec<f64>> {
    // Convert horizontal_aperture to degrees
    horizontal_aperture = horizontal_aperture.to_degrees();
    
    // Extract number of rows and columns
    let range_bins = img_shape.0;
    let azi_bins = img_shape.1;

    // Initialize arrays
    let mut list_tags_converted: Vec<Vec<f64>> = Vec::new();

    // For each tag in decoded_tags
    for i in 0..detected_tags.len() {
        // Make the tag converted array, starting from the provided tag array
        let mut tag_converted = Vec::new();
        for j in 0..detected_tags[i].len() {
            tag_converted.push(detected_tags[i][j] as f64);
        }

        // For each corner, find range & azimuth
        for j in 0..4 {
            // Range
            let x_val = detected_tags[i][(2*j)+1];
            let step: f64 = (max_range - min_range) / (range_bins as f64 - 1.0);
            let range: f64 = (max_range) - ((x_val as f64) * step);
            tag_converted.push(range);

            // Azimuth
            let y_val = detected_tags[i][(2*j)+2];
            let step = horizontal_aperture / (azi_bins as f64 - 1.0);
            let azimuth: f64 = (horizontal_aperture / 2.0) - ((y_val as f64) * step);
            tag_converted.push(azimuth.to_radians());
        }

        // Add the result to the list_tags_converted vector
        list_tags_converted.push(tag_converted);
    }
    list_tags_converted
}

/// Rust equivalent of :func:`actag.tag_decoding.decode_tags`.
///
/// :param binary_img: The binary sonar image.
/// :type binary_img: Vec<Vec<i32>>
/// :param quads: A list of quadrilaterals found in the image.
/// :type quads: Vec<Vec<(i64, i64)>>
/// :param min_range: The minimum range of the sonar.
/// :type min_range: f64
/// :param max_range: The maximum range of the sonar.
/// :type max_range: f64
/// :param horizontal_aperture: The horizontal aperture of the sonar in radians.
/// :type horizontal_aperture: f64
/// :param tag_family: The name of the AcTag family.
/// :type tag_family: String
/// :param tags_in_family: A list containing the data bit layouts for each tag in the family, including rotations and reversals.
/// :type tags_in_family: Vec<Vec<i32>>
/// :param bit_corrections_allowed: The number of bit corrections to perform when decoding the tag.
/// :type bit_corrections_allowed: u64
///
/// :return: A vector containing all of the decoded tags found in the image. Each tag is a vector, with the form ``[tag_id, pt1_row, pt1_col ... pt4_row, pt4_col, pt1_range, pt1_azi ... pt4_range, pt4_azi]``.
/// :rtype: Vec<Vec<i32>>
/// 
#[pyfunction]
pub fn decode_tags(binary_img: Vec<Vec<i32>>, quads: Vec<Vec<(i64, i64)>>, min_range: f64, 
                   max_range: f64, horizontal_aperture: f64, tag_family: String, tags_in_family: Vec<Vec<i32>>, 
                   bit_corrections_allowed: u64) -> Vec<Vec<f64>> {   

    // Get the number of data bits and hamming distance
    let tag_fam_parts: Vec<&str>;
    let tag_fam: String;
    if tag_family.contains('_') {
        tag_fam_parts = tag_family.split('_').collect();
        tag_fam = tag_fam_parts[0].to_string();
    }
    else {
        tag_fam = tag_family;
    }
    let temp: Vec<&str> = tag_fam.split('h').collect();
    let min_hamming_dist: u64 = temp[1].parse().expect("Unable to parse hamming distance");
    let num_data_bits: u64 = (&temp[0][temp[0].find(char::is_numeric).expect("Failed to find numeric character to extract num data bits")..temp[0].len()]).parse().expect("Unable to parse number of data bits");

    // Restrict the bit_corrections_allowed based on the hamming distance
    let max_bit_corrections_allowed: u64;
    if min_hamming_dist % 2 == 0 {
        max_bit_corrections_allowed = (min_hamming_dist / 2) - 1;
    } else {
        max_bit_corrections_allowed = ((min_hamming_dist as f64) / 2.0).floor() as u64;
    }
    if max_bit_corrections_allowed < bit_corrections_allowed {
        panic!("Bit corrections allowed has been set to {}, which is higher than the maximum bit corrections allowed for this TagSonar family, which is {}. Lower the bit corrections allowed, or use a TagSonar family with a higher hamming distance.", bit_corrections_allowed, max_bit_corrections_allowed);
    } 

    // Run the tag detection algorithm
    let tags_detected = tag_detection(&binary_img, quads, &tags_in_family, bit_corrections_allowed, num_data_bits);
    convert_tag_detections_to_range_azi_locations(tags_detected, (binary_img.len() as i64, binary_img[0].len() as i64), min_range, max_range, horizontal_aperture)
}