import argparse
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
from skimage.measure import marching_cubes
from scipy.ndimage import zoom



def convert_nii_to_obj(file, out_name):
    """
    File -> niifti file to be converted
    out_name -> file name AND path of outfile

    """
    img = nib.load(file)
    data = img.get_fdata()[:,:,:]

    # xflip to fix radiological view
    new_data = np.flip(data, 0)
    # new_data = data
    verts, faces, normals, values = marching_cubes(new_data, method='lewiner', step_size=1, allow_degenerate=False)
    faces = faces+1

    '''
    Commented out segment will demonstrate the coordinate conversion
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(verts[:, 0], verts[:,1], faces, verts[:, 2],
                  linewidth=0.2, antialiased=True)
    plt.show()'''

    file = open(out_name, 'w')
    for item in verts:
        file.write("v {0} {1} {2}\n".format(item[0],item[1],item[2]))

    for item in normals:
        file.write("vn {0} {1} {2}\n".format(item[0],item[1],item[2]))

    for item in faces:
        file.write("f {0}//{0} {1}//{1} {2}//{2}\n".format(item[0],item[1],item[2]))

    file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Turn data into object files",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("infile", help="File to be converted to an object")
    parser.add_argument("outfile", help="converted file name")

    args = parser.parse_args()
    convert_nii_to_obj(args.infile, args.outfile)
