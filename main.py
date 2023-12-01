import sys
from sys import stdin, stdout, stderr
import re
import pathlib
import os
import subprocess
import nibabel as nib
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json
from threading import *
from os.path import exists
import numpy as np


def call_cmd(cmd, pipe):
    proc = subprocess.Popen(cmd.split(), stdout=pipe, stderr=pipe, shell=False)
    return proc.communicate()


def call_docker(path_to_volume, commands):
    try:
        print('calling container')
        subprocess.run(["docker", "run", "--name=mne_bpy", "-it", "--rm", "-d", "-v",
                       path_to_volume+":/VISTA_vol", "mne_bpy"], check=True)
        for cmd in commands:
            subprocess.call(cmd, stdin=stdin, stdout=stdout, stderr=stderr, shell=True)
        subprocess.run(["docker", "stop", "mne_bpy"], check=True)
    except Exception as e:
        print(e)
        subprocess.run(["docker", "stop", "mne_bpy"], check=True)


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'VISTA'
        self.left = 0
        self.top = 0
        self.width = 300
        self.height = 300

        self.pipe = subprocess.PIPE
        self.ct_file = None
        self.ct_path = None
        self.mri_file = None
        self.mri_path = None
        self.edf_file = None
        self.edf_path = None
        self._data = None
        self.vol_path = '/VISTA_vol/VISTA/'
        self.output = f'{self.vol_path}Outputs/'
        self.obj = f'{self.output}obj/'
        self.nifti_out_dir = f'{self.output}Nifti/'

        self.real_path = f'{pathlib.Path(__file__).parents[1]}'
        self.initUI()
        self.name_boxes = []

    def thread(self, funct):
        t1 = Thread(target=funct)
        t1.start()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        print(f'real path: {self.real_path}')
        print(f'vol path: {self.vol_path}')

        # Button box contains all the buttons
        button_box = QVBoxLayout(self)
        button_box.setAlignment(Qt.AlignTop)


        # Button to load MRI file
        mri_choice = QPushButton("Select the MRI file", self)
        mri_choice.clicked.connect(self.getMRIText)
        button_box.addWidget(mri_choice, alignment=Qt.AlignLeft)

        mask_choice = QPushButton("Select the Label Mask file", self)
        mask_choice.clicked.connect(self.getMRIText)
        button_box.addWidget(mask_choice, alignment=Qt.AlignLeft)

        mri_idx = self.layout().indexOf(mri_choice)

        self.mri_label = QLabel("MRI file: ", self)
        button_box.insertWidget(mri_idx + 1, self.mri_label)

        self.mask_label = QLabel("Label Mask file: ", self)
        button_box.insertWidget(mri_idx + 3, self.mask_label)

        # Begin the preprocessing, segmentation steps prior to electrodes needing labels
        process_button = QPushButton("Process MRI")
        process_button.clicked.connect(lambda: self.thread(self.process_sub))
        button_box.addWidget(process_button, alignment=Qt.AlignLeft)

        process_mask_button = QPushButton("Process Mask")
        process_mask_button.clicked.connect(lambda: self.thread(self.process_mask))
        button_box.addWidget(process_mask_button, alignment=Qt.AlignLeft)
        
        self.process_label = QLabel("", self)
        button_box.insertWidget(self.layout().indexOf(process_button)+1, self.process_label)

        process_edf_button = QPushButton("Generate FBX")
        # add connect function and threading
        process_edf_button.clicked.connect(lambda: self.thread(self.finalize_patient()))
        button_box.addWidget(process_edf_button, alignment=Qt.AlignLeft)

        self.show()

    def finalize_patient(self):
        self.generate_fbx()

    def generate_fbx(self):
        print('test')
        cmd = [f'docker exec mne_bpy bash -c \" python3.10 -u {self.vol_path}fbx_generator.py '
               f'{self.obj} '
               f'{self.output}VR_object \"']

        call_docker(self.real_path, cmd)

    def process_mask(self):
        command = []
        cmd = f'docker exec mne_bpy bash -c \" python3.9 -u {self.vol_path}convert_to_iso.py ' \
              f'{self.mri_file} ' \
              f'{self.vol_path}structures_iso.nii.gz\"'
        command.append(cmd)

        cmd = f'docker exec mne_bpy bash -c \" python3.9 -u {self.vol_path}mask_splitter.py ' \
              f'{self.vol_path}structures_iso.nii.gz ' \
              f'{self.nifti_out_dir}\"'
        command.append(cmd)

        for file in os.listdir(f'{self.real_path}VISTA/Outputs/Nifti/'):
            print(file)
            f = os.path.join(f'{self.nifti_out_dir}', file)
            fname = f'{os.path.splitext(file)[0]}'
            print(f)
            cmd = f'docker exec mne_bpy bash -c \" python3.9 -u {self.vol_path}niigz_to_obj.py ' \
                  f'{f} ' \
                  f'{self.obj_out_dir}{fname}.obj\"'
            command.append(cmd)

    def process_sub(self):
        if self.mri_file is None:
            self.process_label.setText("Error: MRI file not found")
        else:
            self.process_label.setText("Processing. This will take some time. Check the terminal for progress reports.")
            commands = [
                f'docker exec mne_bpy bash -c \"python3.9 -u '
                f'{self.vol_path}process_subjects.py '
                f'{self.vol_path}Inputs/{self.mri_file}\"',
            ]
            call_docker(self.real_path, commands)

            self.process_label.setText("Done Processing!")

    def getMRIText(self):
        userInput, _ = QFileDialog.getOpenFileName(self, "Select your MRI file", "",
                                                   "All Files (*.*);;NIFTI Files (*.nii.gz)",
                                                   options=QFileDialog.Options())
        self.mri_path = userInput
        if _:  # and userInput != '':
            if str(userInput).strip():
                self.MRIniftiCheck(str(userInput))
            else:
                self.mri_label.setText("Error, no file selected")

    def MRIniftiCheck(self, userInput):
        pieces = userInput.split("/")
        file = pieces[len(pieces) - 1]
        print(file)
        if re.search(".nii.gz", file):
            self.mri_file = file
            print("MRI file: ", self.mri_file)
            '''mri = {"MRI_file": self.mri_file}
            with open('config1.json', 'w') as f:
                json.dump(mri, f)
                print("Save success!")

            print("MRI file: ", self.mri_file)'''
        else:
            file = "Not a NIFTI file, choose again"

        self.mri_label.setText("MRI file: " + file)

    def update_data(self):
        output = f'./Outputs/'
        self._data = np.load(f'{output}datafile.npy')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
