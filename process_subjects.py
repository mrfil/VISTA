import subprocess
import argparse
from convert_to_iso import convert_file
from niigz_to_obj import convert_nii_to_obj


def call_fsl(cmd, pipe):
    proc = subprocess.Popen(cmd.split(), stdout=pipe, stderr=pipe, shell=False)
    return proc.communicate()


def process(mri_file):
    output_folder = '/VISTA/Outputs/'
    file_mri_struct = mri_file
    pipe = subprocess.PIPE
    print("MRI Filename loaded: " + str(file_mri_struct))

    # Generate partial volume estimates
    print("Extracting GM/WM/CSF. This may take some time.")
    call_fsl(f"fsl_anat -i {file_mri_struct} -o {output_folder}brain_seg",pipe)
    print("GM/WM/CSF segmentation finished")

    # Convert PVE
    print("Converting PVEs")
    brain_seg = f'{output_folder}brain_seg.anat/'
    for i in range(0, 3):
        # Align PVE TO MRI
        call_fsl(f"flirt -in {brain_seg}T1_fast_pve_{i}.nii.gz -ref {file_mri_struct} -applyxfm -usesqform -out {output_folder}T1_fast_pve_{i}_MRI.nii.gz", pipe)
        convert_file(f"{output_folder}T1_fast_pve_{i}_MRI.nii.gz", f"{output_folder}T1_fast_pve_{i}_iso.nii.gz")
        convert_nii_to_obj(f"{output_folder}T1_fast_pve_{i}_iso.nii.gz", f"{output_folder}obj/T1_fast_pve_{i}_iso.obj")

    print("Conversion finished")


if __name__ == "__main__":
    print('entered file')
    parser = argparse.ArgumentParser(description="Pre-Process the MRI files",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("mri", help="T1 Weighted MRI as nii.gz", type=str)
    args = parser.parse_args()
    print('parsed')
    process(args.mri)
    print('File finished')
