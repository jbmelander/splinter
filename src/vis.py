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

PLOT_OPTIONS = ['stability', 'si_autocorr', 'si_autocorr_hires', 'waveforms']
class VisualizationTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        
        self.first_row = QHBoxLayout()
        self.second_row = QHBoxLayout()
        self.third_row = QHBoxLayout()
        self.fourth_row = QHBoxLayout()

        self.load_h5_push = QPushButton("Load h5", self)
        self.load_h5_push.clicked.connect(self.load_h5)
        self.first_row.addWidget(self.load_h5_push)

        self.h5_path_label = QLabel("No h5 file selected", self)
        self.first_row.addWidget(self.h5_path_label)

        self.cluster_combo = QComboBox()
        self.second_row.addWidget(self.cluster_combo)
        self.cluster_combo.currentTextChanged.connect(self.update_plot)
        
        
        self.figures = [] 
        self.axes = []
        self.canvi = [] # WTF is the plural of canvas
        self.combos = []
        self.columns = []

        for i in range(2):
            for j in range(2):
                plot_column = QVBoxLayout()
                self.figures.append(Figure())
                self.axes.append(self.figures[-1].add_subplot(111))
                self.canvi.append(FigureCanvas(self.figures[-1]))
                self.combos.append(QComboBox())
                self.combos[-1].addItems(PLOT_OPTIONS)
                self.combos[-1].currentTextChanged.connect(self.update_plot)

                plot_column.addWidget(self.combos[-1])
                plot_column.addWidget(self.canvi[-1])

                self.columns.append(plot_column)



        
        self.third_row.addLayout(self.columns[0])
        self.third_row.addLayout(self.columns[1])

        self.fourth_row.addLayout(self.columns[2])
        self.fourth_row.addLayout(self.columns[3])

        # self.second_row.addWidget(self.plot_combo)


        layout.addLayout(self.first_row)
        layout.addLayout(self.second_row)
        layout.addLayout(self.third_row)
        layout.addLayout(self.fourth_row)
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
        
        for i in range(2):
            for j in range(2):
                current_plot = self.combos[i*2+j].currentText()
                self.axes[i*2+j].clear()

                if current_plot == "stability":
                    self.axes[i*2+j].plot(self.h5_file[current_cluster]["stability"][:])
                    self.axes[i*2+j].set_title("Stability")
                elif current_plot == "si_autocorr":
                    self.axes[i*2+j].plot(self.h5_file[current_cluster]["si_autocorr"][:])
                    self.axes[i*2+j].set_title("autocorr")
                elif current_plot == "si_autocorr_hires":
                    self.axes[i*2+j].plot(self.h5_file[current_cluster]["si_autocorr_hires"][:])
                    self.axes[i*2+j].set_title("hi_res")
                elif current_plot == "waveforms":


                    all_waveforms = self.h5_file[current_cluster]["waveforms"][::10]
                    print(all_waveforms.shape)
                    mean_waveform = np.mean(all_waveforms, axis=0)
                    print(mean_waveform.shape)
                    for _waveform in all_waveforms:
                        self.axes[i*2+j].plot(_waveform, 'k', alpha=0.01)
                    self.axes[i*2+j].plot(self.h5_file[current_cluster]["mean_waveform"][:], 'r')
                    self.axes[i*2+j].set_title("waveforms")

                self.canvi[i*2+j].draw()



        # if current_plot == "stability":
        #     self.axes[0,0].clear()

        #     self.axes[0,0].plot(self.h5_file[current_cluster]["stability"][:])
        #     self.axes[0,0].set_title("Stability")

        #     self.canvas.draw()

        # elif current_plot == "autocorr":
        #     self.axes[0,0].clear()

        #     self.axes[0,0].plot(self.h5_file[current_cluster]["autocorr"][:])
        #     self.axes[0,0].set_title("Stability")

        #     self.canvas.draw()
        #     pass









