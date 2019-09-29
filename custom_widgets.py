# -*- coding: UTF-8 -*-
'''
Author: Jaime Rivera
File: custom_widgets.py
Date: 2019.08.03
Revision: 2019.08.03
Copyright: Copyright Jaime Rivera 2019 | www.jaimervq.com
           The program(s) herein may be used, modified and/or distributed in accordance with the terms and conditions
           stipulated in the Creative Commons license under which the program(s) have been registered. (CC BY-SA 4.0)

Brief:

'''

__author__ = 'Jaime Rivera <jaime.rvq@gmail.com>'
__copyright__ = 'Copyright 2019, Jaime Rivera'
__credits__ = []
__license__ = 'Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)'
__maintainer__ = 'Jaime Rivera'
__email__ = 'jaime.rvq@gmail.com'
__status__ = 'Testing'

from PySide2 import QtWidgets, QtCore, QtGui
import random
import json

import node_classes


# -------------------------------- CUSTOM GRAPHICS VIEW -------------------------------- #

class CustomGW(QtWidgets.QGraphicsView):

    def __init__(self):
        QtWidgets.QGraphicsView.__init__(self)
        self.setRenderHints(QtGui.QPainter.Antialiasing)
        self.setAcceptDrops(True)

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.NoAnchor)

        self.middle_pressed = False

    def mousePressEvent(self, event):
        self.middle_pressed = False

        if event.button() == QtCore.Qt.MidButton:
            self._dragPos = event.pos()
            self.middle_pressed = True
            self.translate(50, 50)

        QtWidgets.QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        new_pos = event.pos()

        if self.middle_pressed:
            disp = new_pos - self._dragPos
            self._dragPos = new_pos
            self.translate(disp.x(), disp.y())

        QtWidgets.QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MidButton:
            self.middle_pressed = False

        QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)

    def wheelEvent(self, event):
        zoom_increase = 1.2
        zoom_decrease = 0.8

        old_pos = self.mapToScene(event.pos())

        if event.delta() > 0:
            self.scale(zoom_increase, zoom_increase)
        else:
            self.scale(zoom_decrease, zoom_decrease)

        new_pos = self.mapToScene(event.pos())
        disp = new_pos - old_pos
        self.translate(disp.x(), disp.y())


# -------------------------------- CUSTOM SCENE CLASS -------------------------------- #

class CustomScene(QtWidgets.QGraphicsScene):
    def __init__(self):
        QtWidgets.QGraphicsScene.__init__(self)

        # NODES
        self.all_nodes = []
        self.selected_node = None

        # PATH TESTS
        self.testing_origin = None
        self.testing_path = QtWidgets.QGraphicsPathItem()
        self.testing_path.setPen(QtGui.QPen(QtCore.Qt.magenta, 2))
        self.testing_path.setZValue(-1)

        # CONNECTORS (Tests)
        self.testing_origin_connector = None
        self.testing_target_connector = None

    def add_node(self, node_class, x, y):
        for c in node_classes.ALL_NODES_LIST:
            if node_class == c.node_class_nice_name or node_class == c.node_class:
                new_node = c()
                self.addItem(new_node)
                new_node.setPos(x, y)
                new_node.set_selected(False)
                self.all_nodes.append(new_node)

                return new_node

    def delete_node(self):
        for stream in self.selected_node.streams:
            stream.clear_connections()

        self.removeItem(self.selected_node)
        self.all_nodes.remove(self.selected_node)
        del self.selected_node

        self.color_streams(recolor=False, only_starts=False)

    def establish_selected_node(self, node):
        if node:
            self.selected_node = node
            node.set_selected(True)
        else:
            self.selected_node = None

        for n in self.all_nodes:
            if n != self.selected_node:
                n.set_selected(False)

    def to_stream(self, node_class, node_id, stream_index):
        for node in self.all_nodes:
            if node.node_class == node_class and node.id == node_id:
                for stream in node.streams:
                    if stream.index == stream_index:
                        return stream

        return None

    def draw_valid_line(self, p1, p2):
        new_path = QtGui.QPainterPath(p1)

        c_p1 = QtCore.QPoint(((p2.x() + p1.x()) / 2) + 10, p1.y())
        c_p2 = QtCore.QPoint(((p2.x() + p1.x()) / 2) - 10, p2.y())
        new_path.cubicTo(c_p1, c_p2, p2)

        new_valid_line = QtWidgets.QGraphicsPathItem(new_path)
        new_valid_line.setPen(QtGui.QPen(QtGui.QColor(QtCore.Qt.green), 2))
        self.addItem(new_valid_line)
        new_valid_line.setZValue(-1)

        return new_valid_line

    def color_streams(self, recolor=True, only_starts=True):
        checkable_nodes = [n for n in self.all_nodes if n.node_class == 'Start']
        if not only_starts:
            checkable_nodes = self.all_nodes

        for node in checkable_nodes:
            for stream in node.streams:
                new_pen = QtGui.QPen(QtGui.QColor(QtCore.Qt.green), 2)
                if recolor:
                    new_pen = QtGui.QPen(
                        QtGui.QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 6)
                self.recolor_stream(stream, new_pen)

    def recolor_stream(self, stream, pen):
        next_stream = stream.output_stream
        if next_stream:
            line = stream.output_line
            line.setPen(pen)
            self.recolor_stream(next_stream, pen)

    def save_to_file(self):
        dialog = QtWidgets.QFileDialog()
        result = dialog.getSaveFileName(caption='Specify target file', filter='*.json')
        if not result[0] or not result[1]:
            return

        target_file = result[0]
        the_dict = {}

        for node in self.all_nodes:
            the_dict[str(node)] = {'class': node.node_class,
                                   'id': node.id,
                                   'x_pos': node.x(),
                                   'y_pos': node.y(),
                                   'widget_value': node.get_widget_value(),
                                   'stream_count': node.stream_count,
                                   'streams': {}}
            for stream in node.streams:
                if stream.output_stream:
                    the_dict[str(node)]['streams'][stream.index] = [stream.output_stream.parent_class,
                                                                    stream.output_stream.parent_id,
                                                                    stream.output_stream.index]

        with open(target_file, 'w') as w:
            json.dump(the_dict, w, indent=2)

    def load_from_file(self):
        if self.all_nodes:
            warning_window = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Error",
                                                   "This functionality is only available with an empty graph."
                                                   "\nPlease clear the graph and try again.")
            warning_window.exec_()
            return

        dialog = QtWidgets.QFileDialog()
        result = dialog.getOpenFileName(caption='Specify source file', filter='*.json')
        if not result[0] or not result[1]:
            return

        source_file = result[0]

        with open(source_file, 'r') as r:
            net_dict = json.load(r)

        # Nodes creation
        for n in net_dict:
            new_node = self.add_node(net_dict[n]['class'], net_dict[n]['x_pos'], net_dict[n]['y_pos'])
            new_node.relabel_id(net_dict[n]['id'])
            new_node.set_widget_value(net_dict[n]['widget_value'])
            for i in range(net_dict[n]['stream_count'] - 1):
                new_node.add_stream()

        max_id = max([n.id for n in self.all_nodes])
        node_classes.GeneralNode.id_counter = max_id

        # Nodes connection
        for n in net_dict:
            if not net_dict[n]['streams']:
                continue

            for index in net_dict[n]['streams']:
                origin_stream = self.to_stream(net_dict[n]['class'], net_dict[n]['id'], int(index))
                target_stream = self.to_stream(net_dict[n]['streams'][index][0], net_dict[n]['streams'][index][1],
                                               net_dict[n]['streams'][index][2])

                out_c = origin_stream.output_connector
                in_c = target_stream.input_connector

                new_l = self.draw_valid_line(out_c.center_point, in_c.center_point)
                out_c.register_connection(in_c, new_l)
                in_c.register_connection(out_c, new_l)

        # Framing
        last_node = self.all_nodes[-1]
        self.parent().centerOn(last_node.x() + 50, last_node.y() + 50)

    def mousePressEvent(self, event):
        testing_connector = self.itemAt(event.scenePos(), QtGui.QTransform())
        if isinstance(testing_connector, node_classes.Connector):
            if testing_connector.can_recieve_connection:
                self.testing_path.setPen(QtGui.QPen(QtCore.Qt.magenta, 2, QtCore.Qt.DashLine))
                self.testing_origin_connector = testing_connector
                self.testing_origin = testing_connector.center_point
                self.addItem(self.testing_path)
            else:
                self.testing_origin_connector = testing_connector.connected_to
                self.testing_target_connector = testing_connector

                self.testing_path = testing_connector.line
                self.testing_path.setPen(QtGui.QPen(QtCore.Qt.magenta, 2, QtCore.Qt.DashLine))
                self.testing_path.setPen(QtGui.QPen(QtCore.Qt.magenta, 2, QtCore.Qt.DashLine))
                if testing_connector.type == 'input':
                    self.testing_origin = self.testing_path.path().pointAtPercent(0)
                else:
                    self.testing_origin = self.testing_path.path().pointAtPercent(1)

                self.testing_origin_connector.toggle_connection(restore=True)
                self.testing_target_connector.toggle_connection(restore=True)
        else:
            self.testing_origin = None
            if testing_connector is None:
                self.establish_selected_node(None)

        QtWidgets.QGraphicsScene.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.testing_origin:
            new_path = QtGui.QPainterPath(self.testing_origin)

            p1 = self.testing_path.path().pointAtPercent(0)
            p2 = event.scenePos()
            c_p1 = QtCore.QPoint(((p2.x() + p1.x()) / 2) + 10, p1.y())
            c_p2 = QtCore.QPoint(((p2.x() + p1.x()) / 2) - 10, p2.y())
            new_path.cubicTo(c_p1, c_p2, p2)

            if new_path.length() > 7000:
                self.testing_path.hide()
            else:
                self.testing_path.show()

            self.testing_path.setPath(new_path)

        QtWidgets.QGraphicsScene.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.testing_path.setPath(QtGui.QPainterPath())
        self.removeItem(self.testing_path)
        self.update()

        if self.testing_origin:
            if isinstance(self.itemAt(event.scenePos(), QtGui.QTransform()), node_classes.Connector):
                self.testing_target_connector = self.itemAt(event.scenePos(), QtGui.QTransform())
                self.check_connectables()

        self.testing_origin = None
        QtWidgets.QGraphicsScene.mouseReleaseEvent(self, event)

    def check_connectables(self):

        origin_connector, target_connector = self.testing_origin_connector, self.testing_target_connector

        checks = [origin_connector.type != target_connector.type,
                  origin_connector.parent_node != target_connector.parent_node,
                  origin_connector.can_recieve_connection,
                  target_connector.can_recieve_connection]

        # CONNECTION CHECKS
        if False in checks:
            return

        # RIGHT-TO-LEFT CONNECTION
        if not ((origin_connector.type == 'output' and origin_connector.x < target_connector.x) or
                (origin_connector.type == 'input' and origin_connector.x > target_connector.x)):
            return

        p1 = origin_connector.center_point
        p2 = target_connector.center_point
        if p1.x() < p2.x():
            new_path = QtGui.QPainterPath(p1)
            c_p1 = QtCore.QPoint(((p2.x() + p1.x()) / 2) + 10, p1.y())
            c_p2 = QtCore.QPoint(((p2.x() + p1.x()) / 2) - 10, p2.y())
            new_path.cubicTo(c_p1, c_p2, p2)
        else:
            new_path = QtGui.QPainterPath(p2)
            c_p1 = QtCore.QPoint(((p2.x() + p1.x()) / 2) + 10, p1.y())
            c_p2 = QtCore.QPoint(((p2.x() + p1.x()) / 2) - 10, p2.y())
            new_path.cubicTo(c_p2, c_p1, p1)

        valid_line = QtWidgets.QGraphicsPathItem(new_path)
        valid_line.setPen(QtGui.QPen(QtCore.Qt.green, 2))
        valid_line.setZValue(-1)
        self.addItem(valid_line)

        target_connector.register_connection(origin_connector, valid_line)
        origin_connector.register_connection(target_connector, valid_line)

        self.color_streams(recolor=False, only_starts=False)

    def keyPressEvent(self, event):
        if self.selected_node:
            if event.key() == QtCore.Qt.Key_Delete:
                self.delete_node()
            elif event.key() == QtCore.Qt.Key_Plus and self.selected_node:
                self.selected_node.add_stream()
            elif event.key() == QtCore.Qt.Key_Minus and self.selected_node:
                self.selected_node.remove_stream()
            elif event.key() == QtCore.Qt.Key_F and self.selected_node:
                self.parent().resetMatrix()
                self.parent().centerOn(self.selected_node.x() + 50, self.selected_node.y() + 50)

        QtWidgets.QGraphicsScene.keyPressEvent(self, event)

    def dragMoveEvent(self, event):
        event.accept()

    def dragLeaveEvent(self, event):
        self.dropEvent(event)

    def dropEvent(self, event):
        source_widget = event.source()
        if isinstance(source_widget, QtWidgets.QTreeWidget):
            node_type = str(source_widget.selectedItems()[0].text(0)).strip()
            self.add_node(node_type, event.scenePos().x(), event.scenePos().y())
