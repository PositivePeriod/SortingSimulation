import csv
import os
import sys
import time
import copy
import random

from sort import Sort

import pyqtgraph
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
import numpy
import matplotlib.pyplot as plt


form_class = uic.loadUiType('pyqt_gui.ui')[0]


class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Button binding; Shuffle, Start, Stop
        self.shuffle.clicked.connect(self.shuffle_function)
        self.start.clicked.connect(self.start_function)
        self.stop.clicked.connect(self.stop_function)
        self.makeuser.clicked.connect(lambda: self.userinput_function('make'))
        self.searchuser.clicked.connect(lambda: self.userinput_function('search'))

        # Slider binding
        self.slider_speed.valueChanged.connect(self.speed_function)
        self.slider_size.valueChanged.connect(self.size_function)

        # Checkbox binding
        self.two_heatmap.stateChanged.connect(lambda: self.option_function('heatmap'))
        self.three_heatmap.stateChanged.connect(lambda: self.option_function('heatmap'))
        self.point_btn.clicked.connect(lambda: self.option_function('btn'))
        self.line_btn.clicked.connect(lambda: self.option_function('btn'))
        self.bar_btn.clicked.connect(lambda: self.option_function('btn'))

        # Sort Radiobutton binding
        self.algorithm = ('bogo', 'bubble', 'gnome', 'heap', 'insertion', 'merge', 'quick', 'selection', 'shell')
        for name in self.algorithm:
            getattr(self, name).clicked.connect(self.sort_function)

        self.counter = 0
        self.time_data = [0, 0]  # start, finish
        self.data = [i+1 for i in range(10)]
        self.history = []
        self.heatmap = True
        self.sorting = Sort()
        self.rate = 50

        # Timer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.rate)  # default

        # Drawing; canvas
        self.key = 'line'
        self.line_drawing = pyqtgraph.PlotCurveItem()
        self.point_drawing = pyqtgraph.ScatterPlotItem()
        self.bar_drawing = pyqtgraph.BarGraphItem()
        self.highlight_drawing = [pyqtgraph.BarGraphItem() for _ in range(3)]  # r g b
        self.point_drawing.setData(pen=None, symbol='o', symbolPen=None, symbolBrush='w')
        self.bar_drawing.setOpts(width=1, brush='w', pen='w')
        self.highlight_drawing[0].setOpts(width=1, brush='r', pen='r')
        self.highlight_drawing[1].setOpts(width=1, brush='g', pen='g')
        self.highlight_drawing[2].setOpts(width=1, brush='b', pen='b')

        # Initial state
        self.array_size = 10  # default
        self.bogo.setChecked(True)
        self.sorting.set_algorithm(self.algorithm[0])
        self.shuffle_function()

    def sort_function(self):
        for name in self.algorithm:
            if getattr(self, name).isChecked():
                print(f'main.py; sorting_function; {name}')
                self.sorting.set_algorithm(name)
                return
        print('main.py; sort_function; Error: no checked for radiobutton')

    def shuffle_function(self):
        random.shuffle(self.data)
        self.update_text(array_edit=False, turn_init=True, time_init=True)
        self.draw_scene(self_data=True)

    def start_function(self):
        print('main.py; start_function')
        # init
        self.counter = 0
        self.time_data = [time.time(), 0]
        self.canvas_widget.setXRange(0, self.array_size)
        self.canvas_widget.setYRange(0, self.array_size)
        if self.heatmap:
            self.history = []

        # binding inactive
        self.slider_size.setEnabled(False)
        self.sort_group.setEnabled(False)
        self.option_group.setEnabled(False)
        self.start.setEnabled(False)
        self.shuffle.setEnabled(False)
        self.makeuser.setEnabled(False)
        self.searchuser.setEnabled(False)

        self.update_text(array_edit=False, turn_init=True, time_init=True)
        print('start_function', self.data)
        self.drawing_function()

    def stop_function(self):
        print('main.py; stop_function')
        # stop getting data
        self.timer.stop()
        self.sorting.clear()

        # binding active
        self.slider_size.setEnabled(True)
        self.sort_group.setEnabled(True)
        self.option_group.setEnabled(True)
        self.start.setEnabled(True)
        self.shuffle.setEnabled(True)
        self.makeuser.setEnabled(True)
        self.searchuser.setEnabled(True)

    def speed_function(self):
        self.rate = self.slider_speed.value()
        self.speed.setText(f'Speed : {self.rate}ms')
        self.timer.setInterval(self.rate)

    def size_function(self):
        # update by slider_size value
        self.update_text(array_edit=True, turn_init=True, time_init=True)

        # visual
        self.data = [i+1 for i in range(self.array_size)]
        random.shuffle(self.data)
        self.canvas_widget.setXRange(0, self.array_size)
        self.canvas_widget.setYRange(0, self.array_size)
        self.draw_scene(self_data=True)

    def userinput_function(self, command):
        if command == 'make':
            path = './data'
            if not os.path.isdir(path):
                os.mkdir(path)
            counter = 1
            while os.path.isfile(path+f'/user_input_format{counter}.csv'):
                counter += 1
            with open(path+f'/user_input_format{counter}.csv', 'w', encoding='utf-8', newline='') as f:
                wr = csv.writer(f)
                wr.writerow(['Order', "Data"])
                size = 10
                for i in range(size):
                    wr.writerow([i+1, size-i])  # TODO
        elif command == 'search':
            path, extension = QFileDialog.getOpenFileName(self, caption='Open File', directory='./data', filter='CSV Files(*.csv)')
            if path is None:
                return 0
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    rdr = csv.reader(f)
                    data = []
                    for line in rdr:
                        data.append(line[1])
                    data.pop(0)
                    if not len(data) > 0:
                        raise Exception
                    else:
                        data = [int(x) for x in data]
            except Exception as e:  # TODO - specific
                print(e)
                # TODO - add user alert
                return 0

            # update by slider_size value
            self.data = data
            self.array_size = len(self.data)
            self.slider_size.setValue(min(self.array_size, self.slider_size.maximum()))
            self.array.setText(f'Size : {self.array_size}')
            self.update_text(array_edit=False, turn_init=True, time_init=True)

            # visual
            self.canvas_widget.setXRange(0, self.array_size)
            self.canvas_widget.setYRange(0, self.array_size)
            self.draw_scene(self_data=True)

    def update_text(self, array_edit, turn_init, time_init, time_only=False):
        if time_only:
            self.time_data[1] = time.time()
            self.time.setText(f'Time : {self.time_data[1] - self.time_data[0]}s')
            return
        if array_edit:
            self.array_size = self.slider_size.value()
            self.array.setText(f'Size : {self.array_size}')
        if turn_init:
            self.turn.setText(f'Comparison : 0')
        else:
            self.counter += 1
            self.turn.setText(f'Comparison : {self.counter}')
        if time_init:
            self.time.setText(f'Time : 0s')
        else:
            self.time_data[1] = time.time()
            self.time.setText(f'Time : {round(self.time_data[1] - self.time_data[0], 5)}s')

    def draw_graph(self, data):
        if self.key == 'line':
            key = {'y': numpy.array(data)}
            self.line_drawing.setData(**key)
            self.canvas_widget.clear()
            self.canvas_widget.addItem(self.line_drawing)
        elif self.key == 'point':
            key = {'size': self.point_size(data), 'x': numpy.arange(len(data)), 'y': numpy.array(data)}
            self.point_drawing.setData(**key)
            self.canvas_widget.clear()
            self.canvas_widget.addItem(self.point_drawing)
        elif self.key == 'bar':
            key = {'x': numpy.arange(len(data))+0.5, 'height': numpy.array(data)}
            self.bar_drawing.setOpts(**key)
            self.canvas_widget.clear()
            self.canvas_widget.addItem(self.bar_drawing)

    def draw_scene(self, self_data=False):
        if self_data:
            self.draw_graph(self.data)
            return
        ans = self.sorting.get_data()
        if ans == (None, None, None):
            self.update_text(False, False, False, time_only=True)
            return
        elif ans == 'finish':
            self.stop_function()
            if self.heatmap and len(self.history) > 0:
                self.heatmap_function()
        else:
            self.update_text(array_edit=False, turn_init=False, time_init=False)
            self.sorting_command(ans)

    def sorting_command(self, commands):
        change, highlight, data = commands
        if data is not None:
            if data != 'stay':
                self.data = data
            self.draw_graph(self.data)
        elif change is not None:  # elif!
            for i, j in change:
                self.data[i], self.data[j] = self.data[j], self.data[i]
            self.draw_graph(self.data)
        if self.key == 'bar' and highlight is not None:
            color = [[], [], []]  # r g b
            for x_, color_ in highlight:
                color['rgb'.index(color_)].append(x_)
            # print(color)
            for i in [1, 2, 0]:  # r g b draw order
                key = {'x': numpy.array(color[i])+0.5, 'height': numpy.array([self.data[x] for x in color[i]])}
                self.highlight_drawing[i].setOpts(**key)
                self.canvas_widget.addItem(self.highlight_drawing[i])
            # print('processing...')
        if self.heatmap and ((data is not None and data != 'stay') or change is not None):
            self.history.append(tuple(self.data))

    def drawing_function(self):
        self.sorting.sort(self.data)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.rate)  # just initial
        self.timer.timeout.connect(self.draw_scene)
        self.timer.start()

    def option_function(self, command):
        if command == 'heatmap':
            if self.two_heatmap.isChecked() or self.three_heatmap.isChecked():
                self.heatmap = True
            else:
                self.heatmap = False
        elif command == 'btn':
            if self.line_btn.isChecked():
                self.key = 'line'
                self.draw_scene(self_data=True)
            elif self.point_btn.isChecked():
                self.key = 'point'
                self.draw_scene(self_data=True)
            elif self.bar_btn.isChecked():
                self.key = 'bar'
                self.draw_scene(self_data=True)

    def point_size(self, data):
        p = len(data)
        if p > 600:
            return 3
        elif p > 400:
            return 5
        elif p > 200:
            return 7
        elif p > 100:
            return 9
        elif p > 50:
            return 11
        else:
            return 14

    def heatmap_function(self):
        name = f"{self.sorting.algorithm} sort - {time.strftime('%c', time.localtime(time.time()))}"
        if self.two_heatmap.isChecked():
            fig_, ax = plt.subplots(1, 1)
            ax.set_xlabel('Array')  # x label
            ax.set_ylabel('Time')  # y label
            fig_.canvas.set_window_title(f'2D Heatmap - {name}')
            ax.pcolor(copy.deepcopy(self.history), cmap='ocean')
            fig_.tight_layout()
        if self.three_heatmap.isChecked():
            self.history = numpy.array(self.history)
            x = numpy.arange(0, len(self.history[0]), 1)  # points in the x axis
            y = numpy.arange(0, len(self.history), 1)  # points in the y axis
            x_, y_ = numpy.meshgrid(x, y)  # create the "base grid"

            fig = plt.figure()
            fig.canvas.set_window_title(f'3D Heatmap - {name}')
            ax = fig.gca(projection='3d')  # 3d axes instance
            surf = ax.plot_surface(x_, y_, self.history,  # data values (2D Arryas)
                                   rstride=1,  # row step size
                                   cstride=1,  # column step size
                                   cmap='rainbow',  # colour map
                                   linewidth=1,  # wireframe line width
                                   antialiased=True)

            ax.set_xlabel('Array')  # x label
            ax.set_ylabel('Time')  # y label
            ax.set_zlabel('Element')  # z label
            fig.colorbar(surf, shrink=1, aspect=8)  # colour bar

            ax.view_init(elev=45, azim=-135)  # elevation & angle
            ax.dist = 8  # distance from the plot
        plt.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = WindowClass()
    main_window.show()
    app.exec_()
