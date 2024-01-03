import matplotlib.pyplot as plt
import numpy as np
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTableWidget, QTableView, QTableWidgetItem, QComboBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
import h5py as h5
import spikeinterface.full as si
import glob
import metrics

class VisualizationTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        
        self.first_row = QHBoxLayout()
        self.second_row = QHBoxLayout()
        self.third_row = QHBoxLayout()

        self.load_h5_push = QPushButton("Load h5", self)
        self.load_h5_push.clicked.connect(self.load_h5)
        self.first_row.addWidget(self.load_h5_push)

        self.h5_path_label = QLabel("No h5 file selected", self)
        self.first_row.addWidget(self.h5_path_label)

        self.cluster_combo = QComboBox()
        self.second_row.addWidget(self.cluster_combo)
        self.cluster_combo.currentTextChanged.connect(self.update_plot)

        self.plot_combo = QComboBox()
        self.plot_combo.addItems(["stability", "autocorr"])
        self.plot_combo.currentTextChanged.connect(self.update_plot)
        
        self.figure, self.axes = plt.subplots(2, 2)
        self.canvas = FigureCanvas(self.figure)
        


        self.third_row.addWidget(self.canvas)

        self.second_row.addWidget(self.plot_combo)



        layout.addLayout(self.first_row)
        layout.addLayout(self.second_row)
        layout.addLayout(self.third_row)
        self.setLayout(layout)

    def load_h5(self):
        # Popup to select h5 file
        self.h5_path = QFileDialog.getOpenFileName(self, "Select h5 file", "", "h5 files (*.h5)")[0]

        # If the user selected a file, update the label
        if self.h5_path:
            self.h5_path_label.setText(self.h5_path)
        else:
            self.h5_path_label.setText("No h5 file selected")
        
        
        self.h5_file = h5.File(self.h5_path, "r")
        self.cluster_ids = list(self.h5_file.keys())

        self.cluster_ids = [int(cluster_id) for cluster_id in self.cluster_ids]
        self.cluster_ids = np.sort(self.cluster_ids)
        
        self.cluster_ids = [str(cluster_id) for cluster_id in self.cluster_ids]
        self.cluster_combo.clear()
        self.cluster_combo.addItems(self.cluster_ids)

    def update_plot(self):
        current_cluster = self.cluster_combo.currentText()
        current_plot = self.plot_combo.currentText()

        # if current_plot == "stability":
        self.axes[0,0].clear()

        self.axes[0,0].plot(self.h5_file[current_cluster]["stability"][:])
        self.axes[0,0].set_title("Stability")

        self.canvas.draw()

        # elif current_plot == "autocorr":
        self.axes[0,1].clear()

        self.axes[0,1].plot(self.h5_file[current_cluster]["autocorr"][1:])
        self.axes[0,1].set_title("autocorr")

        self.canvas.draw()










