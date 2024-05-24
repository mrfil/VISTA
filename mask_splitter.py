import numpy as np
import nibabel as nib
import argparse
import scipy.ndimage as ndimage


def mask_splitter(infile, outdir):
    img = nib.load(infile)
    header = img.header
    img_data = img.get_fdata()
    img_data = img_data.astype(int, casting="unsafe")
    object_labels = np.unique(img_data)
    object_labels = object_labels[object_labels != 0]
    print(object_labels)
    # for each object in the labelled set, mask and only use one object at a time
    for label in object_labels:
        mask = (img_data == label).astype(np.uint8)
        iso_img = nib.Nifti1Image(mask, None, dtype="int64")
        nib.save(iso_img, f'{outdir}_obj{label}.nii.gz')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="convert a nifti file to isometric",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("infile", help="nii.gz file")
    parser.add_argument("outdir", help="directory for output nifti files")
    args = parser.parse_args()
    print(args.infile, args.outdir)
    mask_splitter(args.infile, args.outdir)
