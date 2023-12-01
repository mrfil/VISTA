import numpy as np
import nibabel as nib
import argparse
import scipy.ndimage as ndimage


def mask_splitter_4d(infile, outdir):
    img = nib.load(infile)
    header = img.header
    img_data = img.get_fdata()
    img_data = img_data.astype(int, casting="unsafe")
    object_labels = np.unique(img_data)
    print(object_labels)
    # for each time slice
    for i in range(0, np.shape(img_data)[3]):
        img_slice = img_data[:,:,:,i]
        # for each object in the labelled set, mask and only use one object at a time
        for j in range(1, len(object_labels)):
            mask = img_slice == object_labels[j]
            isolated_object = np.zeros_like(img_slice)
            isolated_object[mask] = object_labels[j]
            iso_img = nib.Nifti1Image(isolated_object, None, dtype="int64")
            nib.save(iso_img, f'{outdir}slice{i}_obj{j}.nii.gz')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="convert a nifti file to isometric",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("infile", help="nii.gz file")
    parser.add_argument("outdir", help="directory for output nifti files")
    args = parser.parse_args()
    print(args.infile, args.outdir)
    mask_splitter_4d(args.infile, args.outdir)
