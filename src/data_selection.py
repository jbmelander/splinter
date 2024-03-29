from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTableWidget, QTableView, QTableWidgetItem
import numpy as np
import os
import h5py as h5
import spikeinterface.full as si
import glob
import metrics

class IOTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        
        self.first_row = QHBoxLayout()
        self.second_row = QHBoxLayout()
        self.third_row = QHBoxLayout()

        ### First row 
        self.directory_path_push = QPushButton("Select directory", self)
        self.directory_path_push.clicked.connect(self.load_path)
        self.first_row.addWidget(self.directory_path_push)

        self.directory_path_label = QLabel("No directory selected", self)
        self.first_row.addWidget(self.directory_path_label)


        # Second row
        self.cluster_table = QTableWidget()
        self.cluster_table.setColumnCount(2)
        self.cluster_table.setHorizontalHeaderLabels(["Cluster", "Number of spikes"])
        self.cluster_table.setColumnWidth(0, 200)
        self.cluster_table.setColumnWidth(1, 200)
        self.cluster_table.setRowCount(0)
        self.cluster_table.horizontalHeader().setStretchLastSection(False)
        self.cluster_table.verticalHeader().setVisible(False)

        self.second_row.addWidget(self.cluster_table)
        
        # Third row
        self.compute_push = QPushButton("Compute", self)
        self.third_row.addWidget(self.compute_push)
        self.compute_push.clicked.connect(self.compute_metrics)



        layout.addLayout(self.first_row)
        layout.addLayout(self.second_row)
        layout.addLayout(self.third_row)

        self.setLayout(layout)

    def load_path(self):
        # Opens a file dialog and returns the path to the selected directory
        self.directory_path = QFileDialog.getExistingDirectory(self, "Select directory")

        # If the user selected a directory, update the label
        if self.directory_path:
            self.directory_path_label.setText(self.directory_path)
        else:
            self.directory_path_label.setText("No directory selected")

        self.parse_directory()

    def parse_directory(self):
        
        waveforms_file = glob.glob(os.path.join(self.directory_path, "sparsity.json"))
        print(waveforms_file)
        self.waveforms_dir = os.path.dirname(waveforms_file[0])

        self.load_SI_data()

    def load_SI_data(self):
        self.waveforms = si.load_waveforms(self.waveforms_dir, with_recording=False)
        self.sorting = self.waveforms.sorting

        self.cluster_ids = self.sorting.get_unit_ids()
        self.cluster_table.setRowCount(len(self.cluster_ids))
        
        print(self.cluster_ids)

        for i, cluster_id in enumerate(self.cluster_ids):
            self.cluster_table.setItem(i, 0, QTableWidgetItem(str(cluster_id)))
            self.cluster_table.setItem(i, 1, QTableWidgetItem(str(self.sorting.get_unit_spike_train(cluster_id).shape[0])))

    def compute_metrics(self):
        # Choose the name of the metrics file, automatically ending with .h5
        self.metrics_file = QFileDialog.getSaveFileName(self, "Choose the name of the metrics file", filter="*.h5")[0]
        if not self.metrics_file.endswith(".h5"):
            self.metrics_file += ".h5"

        with h5.File(self.metrics_file, "w") as h5_file:

            for cluster_id in self.cluster_ids:
                # Create a group for each cluster
                h5_file.create_group(str(cluster_id))

            stabilities = metrics.compute_stability(self.sorting) 

            acs = {}
            for cluster_id in self.cluster_ids:
                cluster_group = h5_file[str(cluster_id)]
                cluster_group.create_dataset("stability", data=stabilities[cluster_id])

                spike_train = self.sorting.get_unit_spike_train(cluster_id)
                window_size = 0.1
                
                window_size = int(window_size * self.sorting.get_sampling_frequency())

                bin_size = 0.001
                bin_size = int(bin_size * self.sorting.get_sampling_frequency())

                ac = si.compute_autocorrelogram_from_spiketrain(spike_train, window_size, bin_size)
                cluster_group.create_dataset("si_autocorr", data=ac)

                window_size = 0.02
                
                window_size = int(window_size * self.sorting.get_sampling_frequency())

                bin_size = 0.0001
                bin_size = int(bin_size * self.sorting.get_sampling_frequency())

                ac = si.compute_autocorrelogram_from_spiketrain(spike_train, window_size, bin_size)
                cluster_group.create_dataset("si_autocorr_hires", data=ac)

                waveforms = self.waveforms.get_waveforms(cluster_id)

                mean_waveform = np.mean(waveforms, axis=0)
                print(mean_waveform)
                print(mean_waveform.shape)

                max_point = np.where(np.abs(mean_waveform) == np.max(np.abs(mean_waveform)))

                print(max_point)
                max_t, max_ch = max_point[0], max_point[1]

                print(max_t, max_ch)
                cluster_group.create_dataset("mean_waveform", data=mean_waveform[:, max_ch])
                cluster_group.create_dataset("waveforms", data=waveforms[:, :, max_ch])


            
            print("Metrics computed and saved to ", self.metrics_file)








