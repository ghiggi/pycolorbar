# -----------------------------------------------------------------------------.
# MIT License

# Copyright (c) 2024 pycolorbar developers
#
# This file is part of pycolorbar.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# -----------------------------------------------------------------------------.
"""Test the Color Encoding and Decoding."""

import numpy as np
import pytest

from pycolorbar.colors.colors_io import (
    CIELABEncoderDecoder,
    CIELUVEncoderDecoder,
    CIEXYZEncoderDecoder,
    CMYKEncoderDecoder,
    HCLEncoderDecoder,
    HSVEncoderDecoder,
    LCHEncoderDecoder,
    RGBAEncoderDecoder,
    RGBEncoderDecoder,
    check_valid_external_data_range,
    check_valid_internal_data_range,
    decode_colors,
    encode_colors,
    is_within_external_data_range,
    is_within_internal_data_range,
)


def create_test_colors_array(color_space):
    """Utility function to create test colors arrays for various color spaces."""
    if color_space == "RGB":
        return np.array([[0, 128, 255], [255, 0, 128]])
    if color_space == "RGBA":
        return np.array([[0, 128, 255, 50], [255, 0, 128, 100]])
    if color_space == "HSV":
        return np.array([[0, 100, 100], [240, 50, 50]])
    if color_space == "LCH":
        return np.array([[50, 100, 0], [75, 50, 180]])
    if color_space == "HCL":
        return np.array([[0, 50, 100], [180, 25, 75]])
    if color_space == "CIELUV":
        return np.array([[100, -80, 70], [10, 20, -40]])
    if color_space == "CIELAB":
        return np.array([[50, -25, 25], [75, 50, -50]])
    if color_space == "CIEXYZ":
        return np.array([[20, 40, 60], [80, 70, 50]])
    if color_space == "CMYK":
        return np.array([[0, 100, 100, 0], [100, 0, 0, 50]])
    raise ValueError(f"Color space '{color_space}' not recognized.")


@pytest.mark.parametrize(
    ("encoder_decoder_class", "color_space"),
    [
        (RGBEncoderDecoder, "RGB"),
        (RGBAEncoderDecoder, "RGBA"),
        (HSVEncoderDecoder, "HSV"),
        (LCHEncoderDecoder, "LCH"),
        (HCLEncoderDecoder, "HCL"),
        (CIELUVEncoderDecoder, "CIELUV"),
        (CIELABEncoderDecoder, "CIELAB"),
        (CIEXYZEncoderDecoder, "CIEXYZ"),
        (CMYKEncoderDecoder, "CMYK"),
    ],
)
def test_encode_decode(encoder_decoder_class, color_space):
    """Test encoding and decoding of color values for various color spaces."""
    encoder_decoder = encoder_decoder_class()
    test_colors = create_test_colors_array(color_space)
    encoded_colors = encoder_decoder.encode(test_colors)
    decoded_colors = encoder_decoder.decode(encoded_colors)
    assert np.allclose(
        test_colors, decoded_colors, atol=1e-2
    ), f"Decoded colors should match the original colors for {color_space} within a tolerance."


@pytest.mark.parametrize(
    ("encoder_decoder_class", "color_space"),
    [
        (RGBEncoderDecoder, "RGB"),
        (RGBAEncoderDecoder, "RGBA"),
        (HSVEncoderDecoder, "HSV"),
        (LCHEncoderDecoder, "LCH"),
        (HCLEncoderDecoder, "HCL"),
        (CIELUVEncoderDecoder, "CIELUV"),
        (CIELABEncoderDecoder, "CIELAB"),
        (CIEXYZEncoderDecoder, "CIEXYZ"),
        (CMYKEncoderDecoder, "CMYK"),
    ],
)
def test_color_range_check(encoder_decoder_class, color_space):
    """Test that color range checking works as expected for various color spaces."""
    encoder_decoder = encoder_decoder_class()

    # Generate test colors that are intentionally outside the valid ranges for each color space
    if color_space == "RGBA":
        test_colors = np.array([[256, -1, 256, 50], [256, -1, -1, 110]])
    if color_space == "RGB":
        test_colors = np.array([[256, -1, 256], [256, -1, -1]])
    elif color_space == "HSV":
        test_colors = np.array([[361, -1, 101], [-1, 101, -1]])
    elif color_space == "LCH" or color_space == "HCL":
        test_colors = np.array([[101, 201, 361], [-1, -1, -1]])
    elif color_space == "CIELUV":
        test_colors = np.array([[101, 101, 101], [-101, 101, -101]])
    elif color_space == "CIELAB":
        test_colors = np.array([[101, 128, 128], [-129, -129, -129]])
    elif color_space == "CIEXYZ":
        test_colors = np.array([[101, 101, 101], [-1, -1, -1]])
    elif color_space == "CMYK":
        test_colors = np.array([[101, 101, 101, 101], [-1, -1, -1, -1]])

    # Test internal data range check
    with pytest.raises(ValueError):
        encoder_decoder.check_valid_internal_data_range(test_colors)

    # Test external data range check without strict checking
    with pytest.raises(ValueError):
        encoder_decoder.check_valid_external_data_range(test_colors, strict=False)

    # Test external data range check with strict checking
    with pytest.raises(ValueError):
        encoder_decoder.check_valid_external_data_range(test_colors, strict=True)


@pytest.mark.parametrize(
    ("hue_degree", "expected_radian"),
    [
        (0, 0),
        (180, np.pi),
        (360, 2 * np.pi),
    ],
)
def test_hsv_hue_conversion(hue_degree, expected_radian):
    """Test the conversion of hue values from degrees to radians in HSV color space."""
    hsv_encoder_decoder = HSVEncoderDecoder()
    hue_array = np.array([[hue_degree, 50, 50]])
    decoded_hue = hsv_encoder_decoder.decode(hue_array)[:, 0]
    assert np.isclose(decoded_hue, expected_radian), "Hue conversion from degrees to radians is incorrect."


def test_rgba_edge_cases():
    """Test RGBA color values at the edge of the allowable range."""
    rgba_encoder_decoder = RGBAEncoderDecoder()
    # Test with valid edge values
    valid_edge_colors = np.array([[0, 0, 0, 0], [255, 255, 255, 100]])
    # No exception should be raised for valid edge values
    rgba_encoder_decoder.check_valid_external_data_range(valid_edge_colors)

    # Test with invalid edge values
    invalid_edge_colors = np.array([[-1, -1, -1, -1], [256, 256, 256, 101]])
    with pytest.raises(ValueError):
        rgba_encoder_decoder.check_valid_external_data_range(invalid_edge_colors)


@pytest.mark.parametrize(
    "invalid_colors",
    [
        (None),  # Incorrect data type
        ("Not an array"),  # Incorrect data type
        (np.array([[300, -100, 0]])),  # Invalid RGB values
        (np.array([1, 2, 3])),  # Incorrect dimensions
    ],
)
def test_invalid_color_format(invalid_colors):
    """Test handling of various invalid colors (i.e. for RGB)."""
    rgb_encoder_decoder = RGBEncoderDecoder()
    with pytest.raises(ValueError):
        rgb_encoder_decoder.check_valid_external_data_range(invalid_colors)


def test_encoding_decoding_accuracy():
    """Test the encoding and decoding accuracy (i.e for RGB)."""
    rgb_encoder_decoder = RGBEncoderDecoder()
    # Create a gradient of colors in external representation and convert to internal
    external_colors = np.linspace(0, 255, num=9).reshape(-1, 3)
    internal_colors = rgb_encoder_decoder.decode(external_colors)
    # Convert back to external representation
    re_encoded_colors = rgb_encoder_decoder.encode(internal_colors)
    # Check if re-encoded colors match the original
    np.testing.assert_almost_equal(
        external_colors,
        re_encoded_colors,
        decimal=5,
        err_msg="RGB re-encoding does not match original colors accurately.",
    )


@pytest.mark.parametrize(
    ("input_radians", "expected_degrees"),
    [
        (0, 0),
        (np.pi, 180),
        (2 * np.pi, 360),
    ],
)
def test_hsv_hue_encoding(input_radians, expected_degrees):
    """Test the custom encoding function for HSV hue channel."""
    hsv_encoder_decoder = HSVEncoderDecoder()
    encoded_hue = hsv_encoder_decoder._hue_encode(input_radians, 0, 2 * np.pi, 0, 360)
    assert np.isclose(
        encoded_hue, expected_degrees
    ), "Hue encoding from radians to degrees is incorrect for HSV color space."


@pytest.mark.parametrize(
    ("input_radians", "expected_degrees"),
    [
        (0, 0),
        (np.pi, 180),
        (2 * np.pi, 360),
    ],
)
def test_lch_hue_encoding(input_radians, expected_degrees):
    """Test the custom encoding function for LCH hue channel."""
    lch_encoder_decoder = LCHEncoderDecoder()
    encoded_hue = lch_encoder_decoder._hue_encode(input_radians, 0, 2 * np.pi, 0, 360)
    assert np.isclose(
        encoded_hue, expected_degrees
    ), "Hue encoding from radians to degrees is incorrect for LCH color space."


def test_check_valid_internal_data_range():
    """Test internal data range validation."""
    color_space = "RGB"

    # Test with valid colors (should not raise an exception)
    valid_colors = np.array([[0.5, 0.5, 0.5], [1, 0, 0]])
    check_valid_internal_data_range(valid_colors, color_space)
    assert is_within_internal_data_range(valid_colors, color_space)

    # Test with all invalid colors (should raise a ValueError)
    invalid_colors = np.array([[1.1, -0.1, 0.5], [2, -1, 1.5]])
    with pytest.raises(ValueError):
        check_valid_internal_data_range(invalid_colors, color_space)
    assert not is_within_internal_data_range(invalid_colors, color_space)


def test_check_valid_external_data_range():
    """Test external data range validation."""
    color_space = "RGB"

    # Test with valid colors (should not raise an exception) (strict=False)
    valid_colors = np.array([[128, 128, 128], [255, 0, 0]])
    check_valid_external_data_range(valid_colors, color_space)
    assert is_within_external_data_range(valid_colors, color_space)

    # Test with valid color but with all values also in the internal ranges (raise an error in strict mode)
    valid_colors = np.array([[0.5, 0.5, 0.5], [0, 0, 0]])
    check_valid_external_data_range(valid_colors, color_space)
    assert is_within_external_data_range(valid_colors, color_space)
    assert not is_within_external_data_range(valid_colors, color_space, strict=True)
    with pytest.raises(ValueError):
        check_valid_external_data_range(valid_colors, color_space, strict=True)

    # Test with invalid colors (should raise a ValueError)
    invalid_colors = np.array([[256, -1, 128], [300, -10, 0]])
    with pytest.raises(ValueError):
        check_valid_external_data_range(invalid_colors, color_space)
    with pytest.raises(ValueError):
        check_valid_external_data_range(invalid_colors, color_space, strict=True)
    assert not is_within_external_data_range(invalid_colors, color_space)
    assert not is_within_external_data_range(invalid_colors, color_space, strict=True)


@pytest.mark.parametrize(
    ("color_space", "colors"),
    [
        ("name", np.array(["red", "green", "blue"])),
        ("hex", np.array(["#FF0000", "#00FF00", "#0000FF"])),
    ],
)
def test_not_decode_encode_name_hex_colors(color_space, colors):
    """Test that for 'name' and 'hex' color spaces, decode and encode return the input colors."""
    # Test decoding
    decoded_colors = decode_colors(colors, color_space)
    assert np.array_equal(
        decoded_colors, colors
    ), f"Decoding should return the original colors for color_space='{color_space}'"

    # Test encoding
    encoded_colors = encode_colors(colors, color_space)
    assert np.array_equal(
        encoded_colors, colors
    ), f"Encoding should return the original colors for color_space='{color_space}'"


@pytest.mark.parametrize(
    ("color_space", "decoded_colors", "encoded_colors"),
    [
        ("RGB", np.array([[0.5, 0.5, 0.5], [0, 0, 0]]), np.array([[127.5, 127.5, 127.5], [0.0, 0.0, 0.0]])),
    ],
)
def test_decode_encode_name_other_colors(color_space, decoded_colors, encoded_colors):
    """Test that encode and decode other colors."""
    # Test decoding
    assert np.array_equal(
        decode_colors(encoded_colors, color_space), decoded_colors
    ), f"Decoding should return the original colors for color_space='{color_space}'"
    # Test encoding
    assert np.array_equal(
        encode_colors(decoded_colors, color_space), encoded_colors
    ), f"Encoding should return the original colors for color_space='{color_space}'"
