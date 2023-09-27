import os
import numpy as np
import pytest
from spektro.loader import load

# Define a fixture for a sample '.npy' file
@pytest.fixture
def sample_npy_file(tmpdir):
    data = np.random.rand(4, 4, 3)
    file_path = tmpdir.join("sample.npy")
    np.save(str(file_path), data)
    return str(file_path)

# Test the load function for '.npy' files
def test_load_npy_file(sample_npy_file):
    # Load the sample .npy file using the load function
    data = load(sample_npy_file)

    # Check if the loaded data is a NumPy array
    assert isinstance(data, np.ndarray)

    # Check if the shape of the loaded data matches the expected shape
    expected_shape = (4, 4, 3)
    assert data.shape == expected_shape

    # Check if the loaded data is close to the original data (tolerance can be adjusted)
    assert np.allclose(data, np.load(sample_npy_file))

# Define the path to the 'indianpinearray.npy' file in the 'data/' directory
indianpine_file_path = os.path.join("data", "indianpinearray.npy")

# Test the load function for 'indianpinearray.npy'
def test_load_indianpine_array():
    # Load the 'indianpinearray.npy' file using the load function
    data = load(indianpine_file_path)

    # Check if the loaded data is a NumPy array
    assert isinstance(data, np.ndarray)

    # Check if the shape of the loaded data matches the expected shape (replace with your actual expected shape)
    expected_shape = (145, 145, 200)
    assert data.shape == expected_shape