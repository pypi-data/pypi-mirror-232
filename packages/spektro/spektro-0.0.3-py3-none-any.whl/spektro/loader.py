import numpy as np
import h5py

def load(file_path, channel_order=(), verbose=False):
    """
    Load hyperspectral data from an npy file.

    Parameters:
        file_path (str): The path to the hyperspectral data npy file.
        verbose (bool): Whether to print additional information.

    Returns:
        data (numpy.ndarray): The loaded hyperspectral data as a NumPy array.
    """
    try:
        if file_path.endswith('.npy'):
            data = np.load(file_path)
        elif file_path.endswith('.h5'):
            # source: https://stackoverflow.com/a/41586571
            with h5py.File(file_path, "r") as f:
                # Print all root level object names (aka keys) 
                # these can be group or dataset names 
                print("Keys: %s" % f.keys()) if verbose else None
                # get first object name/key; may or may NOT be a group
                a_group_key = list(f.keys())[0]

                # get the object type for a_group_key: usually group or dataset
                print(type(f[a_group_key])) if verbose else None

                # If a_group_key is a group name, 
                # this gets the object names in the group and returns as a list
                data = list(f[a_group_key])

                # If a_group_key is a dataset name, 
                # this gets the dataset values and returns as a list
                data = list(f[a_group_key])
                # preferred methods to get dataset values:
                # ds_obj = f[a_group_key]      # returns as a h5py dataset object
                data = f[a_group_key][()]  # returns as a numpy array
        
        if channel_order:
            # Change the order of the channels using the channel_order parameter
            data = np.moveaxis(data, [0,1,2], channel_order)

        return data
    except Exception as e:
        raise Exception(f"Error loading data from {file_path}: {str(e)}")

if __name__ == "__main__":
    # file_path = 'data/indianpinearray.npy'
    file_path = 'data/2021-11-03_006.h5'
    img = load(file_path, channel_order=(2,0,1), verbose=True)
    print(f"Spektro has read this as: Width: {img.shape[0]}, Height: {img.shape[1]}, Bands: {img.shape[2]}")
