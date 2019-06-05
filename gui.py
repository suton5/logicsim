"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""

import app_base as ab

import wx
import wx.lib.scrolledpanel
import wx.glcanvas as wxcanvas
import numpy as np
import math
from OpenGL import GL, GLU, GLUT
import subprocess
import sys

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

global_cycles_completed = 0


class MyGLCanvas2D(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])

        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        # Copied from User Interface
        self.devices = devices
        self.monitors = monitors
        self.cycles_completed = 0
    
    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text, autoscroll = False):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True
        
        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        for device_id, output_id in self.monitors.monitors_dictionary:
            i = list(
                self.monitors.monitors_dictionary.keys()).index(
                (device_id, output_id))
            signal_list = self.monitors.monitors_dictionary[(
                device_id, output_id)]
            signal_name = self.devices.get_signal_name(device_id, output_id)

            GL.glBegin(GL.GL_LINE_STRIP)
            for j in range(len(signal_list)):
                signal = signal_list[j]
                x = (j * 20) + 60
                x_next = (j * 20) + 80
                if signal == self.devices.HIGH:
                    y = 100 + 100 * i
                    GL.glColor3f(1, 0, 0)
                if signal == self.devices.LOW:
                    y = 75 + 100 * i
                    GL.glColor3f(0.0, 1.0, 0.0)  # red for low signal trace
                if signal != self.devices.BLANK:
                    GL.glVertex2f(x, y)
                    GL.glVertex2f(x_next, y)
                if autoscroll:
                    self.latest_position(x)
            GL.glEnd()

            self.labels_position(i, signal_name)

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()
            
    def latest_position(self, x_pos):
        self.pan_x = min(self.GetClientSize()[0] - x_pos - 150, 0)
        self.init = False
        self.Refresh()

    def labels_position(self, i, signal_name):
        self.render_text('HIGH', 20, 90 + 100 * i, 1)
        self.render_text('LOW', 20, 70 + 100 * i, 2)
        self.render_text(signal_name, 10, 50 + 100 * i)
        self.Refresh()


    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join([_(u"Canvas redrawn on paint event, size is "),
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def default_position(self):
        self.pan_x = 0
        self.pan_y = 0
        self.zoom = 1
        self.init = False
        self.Refresh()

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join([_(u"Mouse button pressed at: "), str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join([_(u"Mouse button released at: "), str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join([_(u"Mouse left canvas at: "), str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join([_(u"Mouse dragged to: "), str(event.GetX()),
                            ", ", str(event.GetY()), _(u". Pan is now: "),
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join([_(u"Negative mouse wheel rotation. Zoom is now: "),
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join([_(u"Positive mouse wheel rotation. Zoom is now: "),
                            str(self.zoom)])
        if text:
            self.render(text)
            
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos, colour=0):
        """Handle text drawing operations."""
        if colour == 0:
            GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        elif colour == 1:
            GL.glColor3f(1.0, 0.0, 0.0)
        elif colour == 2:
            GL.glColor3f(0.0, 1.0, 0.0)
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))




class MyGLCanvas3D(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos, z_pos): Handles text drawing
                                                  operations.
    """

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Constants for OpenGL materials and lights
        self.mat_diffuse = [0.0, 0.0, 0.0, 1.0]
        self.mat_no_specular = [0.0, 0.0, 0.0, 0.0]
        self.mat_no_shininess = [0.0]
        self.mat_specular = [0.5, 0.5, 0.5, 1.0]
        self.mat_shininess = [50.0]
        self.top_right = [1.0, 1.0, 1.0, 0.0]
        self.straight_on = [0.0, 0.0, 1.0, 0.0]
        self.no_ambient = [0.0, 0.0, 0.0, 1.0]
        self.dim_diffuse = [0.5, 0.5, 0.5, 1.0]
        self.bright_diffuse = [1.0, 1.0, 1.0, 1.0]
        self.med_diffuse = [0.75, 0.75, 0.75, 1.0]
        self.full_specular = [0.5, 0.5, 0.5, 1.0]
        self.no_specular = [0.0, 0.0, 0.0, 1.0]

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise the scene rotation matrix
        self.scene_rotate = np.identity(4, 'f')

        # Initialise variables for zooming
        self.zoom = 1

        # Offset between viewpoint and origin of the scene
        self.depth_offset = 1000

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        # Copied from User Interface
        self.devices = devices
        self.monitors = monitors
        self.cycles_completed = 0

        self.colours = [(1.0, 0.0, 0.0),
                        (0.0, 1.0, 0.0),
                        (0.0, 0.0, 1.0),
                        (0.5, 0.5, 0.0),
                        (1.0, 0.0, 1.0),
                        (0.0, 1.0, 1.0),
                        (0.0, 0.5, 0.0),
                        (0.3, 0.3, 0.3)]

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)

        GL.glViewport(0, 0, size.width, size.height)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(45, size.width / size.height, 10, 10000)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()  # lights positioned relative to the viewer
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, self.med_diffuse)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, self.top_right)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_DIFFUSE, self.dim_diffuse)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_POSITION, self.straight_on)

        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, self.mat_specular)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SHININESS, self.mat_shininess)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE,
                        self.mat_diffuse)
        GL.glColorMaterial(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE)

        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glCullFace(GL.GL_BACK)
        GL.glEnable(GL.GL_COLOR_MATERIAL)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_LIGHT1)
        GL.glEnable(GL.GL_NORMALIZE)

        # Viewing transformation - set the viewpoint back from the scene
        GL.glTranslatef(0.0, 0.0, -self.depth_offset)

        # Modelling transformation - pan, zoom and rotate
        GL.glTranslatef(self.pan_x, self.pan_y, 0.0)
        GL.glMultMatrixf(self.scene_rotate)
        GL.glScalef(self.zoom, self.zoom, self.zoom)

    def render(self):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        for device_id, output_id in self.monitors.monitors_dictionary:
            i = list(
                self.monitors.monitors_dictionary.keys()).index(
                (device_id, output_id))
            GL.glColor3f(self.colours[i%8][0], self.colours[i%8][1], self.colours[i%8][2])
            x = (i - len(self.monitors.monitors_dictionary)/2)*20
            signal_list = self.monitors.monitors_dictionary[(
                device_id, output_id)]

            signal_name = self.devices.get_signal_name(device_id, output_id)

            self.render_text(signal_name, x, 0, 10*len(signal_list)+10)

            length = len(signal_list)
            for j in range(length):
                signal = signal_list[j]
                z = (j-length/2)*20
                if signal == self.devices.HIGH:
                    y = 11
                if signal == self.devices.LOW:
                    y = 1
                if signal != self.devices.BLANK:
                    self.draw_cuboid(x, z, 5, 10, y)

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def draw_cuboid(self, x_pos, z_pos, half_width, half_depth, height):
        """Draw a cuboid.

        Draw a cuboid at the specified position, with the specified
        dimensions.
        """
        GL.glBegin(GL.GL_QUADS)
        GL.glNormal3f(0, -1, 0)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glNormal3f(0, 1, 0)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glNormal3f(-1, 0, 0)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glNormal3f(1, 0, 0)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glNormal3f(0, 0, -1)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glNormal3f(0, 0, 1)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glEnd()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join([_(u"Canvas redrawn on paint event, size is "),
                        str(size.width), ", ", str(size.height)])
        self.render()

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        self.SetCurrent(self.context)

        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()

        if event.Dragging():
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()
            x = event.GetX() - self.last_mouse_x
            y = event.GetY() - self.last_mouse_y
            if event.LeftIsDown():
                GL.glRotatef(math.sqrt((x * x) + (y * y)), y, x, 0)
            if event.MiddleIsDown():
                GL.glRotatef((x + y), 0, 0, 1)
            if event.RightIsDown():
                self.pan_x += x
                self.pan_y -= y
            GL.glMultMatrixf(self.scene_rotate)
            GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX, self.scene_rotate)
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False

        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False

        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False

        self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos, z_pos):
        """Handle text drawing operations."""
        GL.glDisable(GL.GL_LIGHTING)
        GL.glRasterPos3f(x_pos, y_pos, z_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_10

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos3f(x_pos, y_pos, z_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

        GL.glEnable(GL.GL_LIGHTING)

    def default_position(self):
        self.pan_x = 0
        self.pan_y = 0
        self.zoom = 1
        self.init = False
        self.Refresh()




hold_monitor = {}
class MyDialog_monitor(wx.Frame):
    def __init__(self, parent, id, title, names, devices, monitors):
        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.temp = {}
        self.monitors_array = self.monitors_array_adder()
        window_height = min(len(self.monitors_array) *
                            35 + 100, 600)
        # Create a frame
        wx.Frame.__init__(
            self,
            parent,
            id,
            title,
            size=(
                200,
                window_height),
            style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        panel = wx.lib.scrolledpanel.ScrolledPanel(
            self, -1, size=(200, window_height), pos=(80, 0), style=wx.SIMPLE_BORDER)
        panel.SetupScrolling()
        self.MakeModal()
        self.Bind(wx.EVT_CLOSE, self.on_close_window)
        bSizer = wx.BoxSizer(wx.VERTICAL)

        self.monitors_array = self.monitors_array_adder()
        for i in range(len(self.monitors_array)):
            self.i = wx.CheckBox(panel, label=self.monitors_array[i])
            self.i.Bind(wx.EVT_CHECKBOX, self.onChecked_monitor)
            # Add label to our global hold
            if self.monitors.get_signal_names()[0].count(
                    self.i.GetLabel()) == 1:
                default = True
            else:
                default = False
            # set monitor checkbox value as that of global hold monitor
            self.i.SetValue(hold_monitor.get(self.monitors_array[i], default))
            # set global hold monitor values as that of monitor checkbox (for
            # initialisation of hold_monitor dictionary)
            hold_monitor[self.monitors_array[i]] = self.i.GetValue()
            # set temp attribute as current checkbox values, checkbox will only manipulate this temp
            # hitting ok button will confirm changes and set global values to
            # changes
            self.temp[self.i.GetLabel()] = self.i.GetValue()
            bSizer.Add(self.i, 0, wx.ALL, 5)
        self.btn = wx.Button(panel, wx.ID_OK, label="OK")
        self.btn.Bind(wx.EVT_BUTTON, self.ok_button)
        bSizer.Add(self.btn, 0, wx.ALL, 5)
        panel.SetSizer(bSizer)

    def monitors_array_adder(self):
        device_id = self.devices.find_devices()
        dlatch_id = self.devices.find_devices(self.devices.D_TYPE)
        monitors_array = []
        for i in device_id:
            if dlatch_id.count(i) == 1:
                output_q = (self.names.get_name_string(i), "Q")
                output_qbar = (self.names.get_name_string(i), "QBAR")
                dlatch_output_q = ".".join(output_q)
                dlatch_output_qbar = ".".join(output_qbar)
                monitors_array.append(dlatch_output_q)
                monitors_array.append(dlatch_output_qbar)
            else:
                monitors_array.append(self.names.get_name_string(i))
        return monitors_array

    def zap_command(self, monitor_zap, monitor_name):
        if monitor_zap is not None:
            [device, port] = monitor_zap
            if self.monitors.remove_monitor(device, port):
                print(_(u"Successfully zapped monitor"), monitor_name)
            else:
                print(_(u"Error! Could not zap monitor"), monitor_name)

    def ok_button(self, event):
        """Set the monitors."""
        global global_cycles_completed
        global hold_monitor
        for monitor_name in self.monitors_array:
            if hold_monitor[monitor_name] != self.temp[monitor_name]:
                monitor = self.devices.get_signal_ids(monitor_name)
                if self.temp[monitor_name]:
                    if monitor is not None:
                        [device_id, port_id] = monitor
                        monitor_error = self.monitors.make_monitor(
                            device_id, port_id, global_cycles_completed)
                        if monitor_error == self.monitors.NO_ERROR:
                            print(_(u"Successfully made monitor "), monitor_name)
                        else:
                            print(
                                _(u"Error! Could not make monitor"), monitor_name)
                else:
                    self.zap_command(monitor, monitor_name)
        hold_monitor = self.temp
        self.MakeModal(False)
        self.Close()

    def onChecked_monitor(self, event):
        """Return the device and port IDs of the current signal name.

        Return None if either is invalid.
        """
        monitored_output = event.GetEventObject()
        self.temp[monitored_output.GetLabel()] = monitored_output.GetValue()
        return

    def MakeModal(self, modal=True):
        if modal and not hasattr(self, '_disabler'):
            self._disabler = wx.WindowDisabler(self)
        if not modal and hasattr(self, '_disabler'):
            del self._disabler

    def on_close_window(self, event):
        self.MakeModal(False)
        self.Destroy()


hold = {}


class MyDialog(wx.Frame):

    def __init__(self, parent, id, title, names, devices):
        self.names = names
        self.devices = devices
        self.temp = {}
        self.switches = self.switches_array_adder()[0]
        self.values = self.switches_array_adder()[1]
        window_height = min(len(self.switches) * 35 + 100, 600)
        # Create a frame
        wx.Frame.__init__(
            self,
            parent,
            id,
            title,
            size=(
                200,
                window_height),
            style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        panel = wx.lib.scrolledpanel.ScrolledPanel(
            self, -1, size=(200, window_height), pos=(80, 0), style=wx.SIMPLE_BORDER)
        panel.SetupScrolling()
        self.MakeModal()
        self.Bind(wx.EVT_CLOSE, self.on_close_window)
        bSizer = wx.BoxSizer(wx.VERTICAL)

        for i in range(len(self.switches)):
            self.i = wx.CheckBox(panel, label=self.switches[i])
            self.i.Bind(wx.EVT_CHECKBOX, self.onChecked)
            # Add label to our global hold
            self.i.SetValue(hold.get(self.switches[i], self.values[i]))
            hold[self.switches[i]] = self.i.GetValue()
            self.temp[self.switches[i]] = hold[self.switches[i]]
            bSizer.Add(self.i, 0, wx.ALL, 5)
        self.btn = wx.Button(panel, wx.ID_OK, label="OK")
        self.btn.Bind(wx.EVT_BUTTON, self.ok_button)
        bSizer.Add(self.btn, 0, wx.ALL, 5)

        panel.SetSizer(bSizer)

    def switches_array_adder(self):
        device_id = self.devices.find_devices(self.devices.SWITCH)
        objects = []
        values = []
        switches_array = []
        for i in device_id:
            objects.append(self.devices.get_device(i))
            switches_array.append(self.names.get_name_string(i))
        for i in objects:
            values.append(i.switch_state)
        return switches_array, values

    def onChecked(self, event):
        signal = event.GetEventObject()
        self.temp[signal.GetLabel()] = signal.GetValue()
        return

    def ok_button(self, event):
        global hold
        hold = self.temp
        for switch in self.switches:
            self.devices.set_switch(
                self.names.lookup(
                    [switch])[0], hold[switch])
            if hold[switch]:
                print(switch, _(u" is on"))
            else:
                print(switch, _(u" is off"))
        self.MakeModal(False)
        self.Close()

    def MakeModal(self, modal=True):
        if modal and not hasattr(self, '_disabler'):
            self._disabler = wx.WindowDisabler(self)
        if not modal and hasattr(self, '_disabler'):
            del self._disabler

    def on_close_window(self, event):
        self.MakeModal(False)
        self.Destroy()

class ErrorFrame(wx.Dialog):
    def __init__(self, parent = None):
        wx.Frame.__init__(self, parent, -1, _(u"Parsing Definition Files"))
        
        self.errormsg = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE|wx.TE_READONLY)
        self.errormsg.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u"Consolas"))
        self.close = wx.Button(self, label=_(u"Close"))

        # Set sizer for the panel content
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.errormsg, 5, wx.EXPAND, 5)
        self.sizer.Add(self.close, 1, wx.EXPAND, 5)

        # Set event handlers
        self.close.Bind(wx.EVT_BUTTON, self.OnButton)

        self.SetSizeHints(300, 300)
        self.SetSizer(self.sizer)

        sys.stdout = self.errormsg

    def OnButton(self, e):
        self.Close(True)


lang_sel = 0
class Gui(wx.Frame):
    """
    Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        """Initialise variables."""
        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network
        # Setting up the file menu
        self.fileMenu = wx.Menu()
        self.fileMenu.Append(102, _(u"&About"))
        self.fileMenu.Append(wx.ID_OPEN, _(u"&Open"))
        self.fileMenu.Append(103, _(u"&Quit"))

        # Create the menu bar
        self.menuBar = wx.MenuBar()
        # Adding the "file menu" to the menu bar
        self.menuBar.Append(self.fileMenu, _(u"&File"))
        # Adding the menu bar to the frame content
        self.SetMenuBar(self.menuBar)

        # Canvas for drawing signals
        self.canvas_2d = MyGLCanvas2D(self, devices, monitors)
        self.canvas_3d = MyGLCanvas3D(self, devices, monitors)
        self.canvas_2d.Show()
        self.canvas_3d.Hide()

        # Configure the widgets
        self.lblLogWindow = wx.StaticText(self, -1, label = _(u"Console"))
        self.logWindow = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE|wx.TE_READONLY, size = (100, 500))

        self.lblList = ['2D', '3D']     
        self.render = wx.RadioBox(self, label = _(u"Render"), choices = self.lblList, majorDimension = 1, style = wx.RA_SPECIFY_ROWS)
        self.render.SetSelection(0)
        self.state = self.render.GetSelection()
        self.languagelist = ["English", "Chinese"]
        self.language = wx.RadioBox(self, label = _(u"Language"), choices = self.languagelist, majorDimension = 1, style = wx.RA_SPECIFY_ROWS)      
        global lang_sel
        self.language.SetSelection(lang_sel)
        self.current_lang = self.language.GetSelection()
        self.text_run = wx.StaticText(self, wx.ID_ANY, _(u"Cycles to run"))
        self.text_cont = wx.StaticText(self, wx.ID_ANY, _(u"Cycles to continue"))
        self.spin_run = wx.SpinCtrl(self, wx.ID_ANY, "10", max=2147483647)
        self.spin_cont = wx.SpinCtrl(self, wx.ID_ANY, "2", max=2147483647)
        self.run = wx.Button(self, wx.ID_ANY, _(u"Run"))
        self.cont = wx.Button(self, wx.ID_ANY, _(u"Continue"))
        self.ResetButton = wx.Button(self, wx.ID_ANY, _(u"Clear"))
        self.set_switch = wx.Button(self, wx.ID_ANY, _(u"Set Switches"))
        self.select_monitor = wx.Button(self, wx.ID_ANY, _(u"Monitor"))
        self.default_position = wx.Button(self, wx.ID_ANY, _(u"Default Position"))

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.render.Bind(wx.EVT_RADIOBOX, self.on_radiobox)
        self.language.Bind(wx.EVT_RADIOBOX, self.on_sel_language)
        self.spin_run.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.spin_cont.Bind(wx.EVT_SPINCTRL, self.on_spin_cont)
        self.run.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.cont.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.ResetButton.Bind(wx.EVT_BUTTON, self.on_reset_button)
        self.set_switch.Bind(wx.EVT_BUTTON, self.check_box)
        self.select_monitor.Bind(wx.EVT_BUTTON, self.check_box_monitor)
        self.default_position.Bind(wx.EVT_BUTTON, self.on_default_pos)
        
        # Configure sizers for layout
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_sizer.Add(self.canvas_2d, 5, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        side_sizer.Add(self.language, 0, wx.TOP, 5)
        side_sizer.Add(self.render, 0, wx.TOP, 5)
        side_sizer.Add(self.text_run, 1, wx.TOP, 10)
        side_sizer.Add(self.spin_run, 1, wx.ALL, 5)
        side_sizer.Add(self.run, 1, wx.EXPAND, 5)
        side_sizer.Add(self.text_cont, 1, wx.TOP, 10)
        side_sizer.Add(self.spin_cont, 1, wx.ALL, 5)
        side_sizer.Add(self.cont, 1, wx.EXPAND, 5)
        side_sizer.Add(self.set_switch, 1, wx.EXPAND, 5)
        side_sizer.Add(self.select_monitor, 1, wx.EXPAND, 5)
        side_sizer.Add(self.ResetButton, 1, wx.EXPAND, 5)
        side_sizer.Add(self.default_position, 1, wx.EXPAND, 5)
        side_sizer.Add(self.lblLogWindow, 1, wx.TOP, 5)
        side_sizer.Add(self.logWindow, 1, wx.EXPAND, 5)

        self.SetSizeHints(600, 600)
        self.SetSizer(self.main_sizer)

        # A modal show will lock out the other windows until it has been dealth with
        # Very useful in some programming tasks to ensure that things happen in an order
        # that the programmer expects, but can be very frustrating to the user if it is
        # used to excess
        self.exitconfirmation = wx.MessageDialog(
            self,
            _(u"Are you sure you want to quit the simulation? \n"),
            _(u"Confirmation"),
            wx.YES_NO)
        self.openFileDialog = wx.FileDialog(
            self,
            _(u"Select Logic Definition File"),
            "",
            "",
            _(u"Logic definition files (*.txt)|*.txt"),
            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        sys.stdout = self.logWindow

    def on_sel_language(self, event):
        self.current_lang = self.language.GetSelection()
        
        if self.current_lang == 0:
            app = ab.BaseApp(redirect=False)
            app.updateLanguage(u"en")
            print(_(u"English is selected"))
            global lang_sel
            lang_sel = 0
        else:
            app = ab.BaseApp(redirect=False)
            app.updateLanguage(u"zh_CN")
            print(_(u"Chinese is selected"))
            lang_sel = 1
        
        self.text_run.SetLabel(_(u"Cycles to run"))
        self.text_cont.SetLabel(_(u"Cycles to continue"))
        self.run.SetLabel(_(u"Run"))
        self.cont.SetLabel(_(u"Continue"))
        self.ResetButton.SetLabel(_(u"Clear"))
        self.set_switch.SetLabel(_(u"Set Switches"))
        self.select_monitor.SetLabel(_(u"Monitor"))
        self.default_position.SetLabel(_(u"Default Position"))
        self.language.SetLabel(_(u"Language"))
        self.render.SetLabel(_(u"Render"))
        self.lblLogWindow.SetLabel(_(u"Console"))
        self.fileMenu.SetLabel(102, _(u"About"))
        self.fileMenu.SetLabel(103, _(u"Quit"))
        self.menuBar.SetMenuLabel(0, _(u"File"))
        self.fileMenu.SetLabel(wx.ID_OPEN, _(u"&Open"))

            
    def on_radiobox(self, event):
        self.state = self.render.GetSelection()
        print(self.lblList[self.state], _(u" was selected"))
        if self.state == 0:
            #Change from 3D to 2D
            self.main_sizer.Replace(self.canvas_3d, self.canvas_2d)
            self.canvas_3d.Hide()
            self.canvas_2d.Show()
        else:
            #Change from 2D to 3D
            self.main_sizer.Replace(self.canvas_2d, self.canvas_3d)
            self.canvas_2d.Hide()
            self.canvas_3d.Show()
        self.main_sizer.Layout()
    
    def on_default_pos(self, event):
        self.canvas_2d.default_position()
        self.canvas_3d.default_position()
    
    def check_box_monitor(self, event):
        MyDialog_monitor(self, -1, _(u"Select signals to monitor"),
                         self.names, self.devices, self.monitors).Show()

    def check_box(self, event):
        MyDialog(self, -1, _(u"Set switches to 1"),
                 self.names, self.devices).Show()

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == 103:
            exitconf = self.exitconfirmation.ShowModal()
            if exitconf == wx.ID_YES:
                self.Close(True)
        if Id == 102:
            wx.MessageBox(
                _(u"Display the signal traces at different monitored outputs.  \nRed trace represents '1', blue trace represents '0'.\nOutputs to be monitored can be selected by clicking 'Monitor'.\nSwitches levels can be selected by clicking 'Set Switches'"),
                _(u"About Logsim"),
                wx.ICON_INFORMATION | wx.OK)

        if Id == wx.ID_OPEN:
            with wx.FileDialog(self) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
                path = fileDialog.GetPath()
                self.Close(True)

                app = wx.App()
                error = ErrorFrame()

                names = Names()
                devices = Devices(names)
                network = Network(names, devices)
                monitors = Monitors(names, devices, network)
                self.names = names
                self.devices = devices
                self.network = network
                self.monitors = monitors
                self.scanner = Scanner(path, self.names)
                self.parser = Parser(
                    self.names,
                    self.devices,
                    self.network,
                    self.monitors,
                    self.scanner)
                global global_cycles_completed
                global hold
                global hold_monitor
                global_cycles_completed = 0
                hold = {}
                hold_monitor = {}
                try:
                    self.parser.parse_network()
                    gui = Gui(
                                "LogicSim",
                                path,
                                self.names,
                                self.devices,
                                self.network,
                                self.monitors)
                    gui.Show(True)
                except:
                    pass

                error.ShowModal()
                app.MainLoop()

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin_run.GetValue()
        text = "".join([_(u"New run spin control value: "), str(spin_value)])
        if self.state == 0:
            self.canvas_2d.render(text)
        else:
            self.canvas_3d.render()
        return spin_value

    def on_spin_cont(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value_cont = self.spin_cont.GetValue()
        text = "".join(
            [_(u"New continue spin control value: "), str(spin_value_cont)])
        if self.state == 0:
            self.canvas_2d.render(text)
        else:
            self.canvas_3d.render()
        return spin_value_cont

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = _(u"Run button pressed.")
        if self.state == 0:
            self.canvas_2d.render(text)
        else:
            self.canvas_3d.render()
        self.run_command()

    def on_continue_button(self, event):
        """Handle the event when the user clicks the Continue button."""
        text = _(u"Continue button pressed.")
        if self.state == 0:
            self.canvas_2d.render(text)
        else:
            self.canvas_3d.render()
        self.continue_command()

    def on_reset_button(self, event):
        """Handle the event when the user clicks the reset button."""
        text = _(u"Reset button pressed.")
        if self.state == 0:
            self.canvas_2d.render(text)
        else:
            self.canvas_3d.render()

        dialog_box = MyDialog_monitor(
            self, -1, _(u"Select signals to monitor"), self.names, self.devices, self.monitors)
        dialog_box.Destroy()

        global hold_monitor
        differential = hold_monitor

        hold_monitor = dict.fromkeys(hold_monitor, False)

        dialog_box = MyDialog_monitor(
            self, -1, _(u"Select signals to monitor"), self.names, self.devices, self.monitors)

        hold_monitor = differential
        dialog_box.ok_button(wx.EVT_BUTTON)

        dialog_box.Destroy()
        hold_monitor = dict.fromkeys(hold_monitor, False)
        if self.state == 0:
            self.canvas_2d.Refresh()
        else:
            self.canvas_3d.Refresh()
        global global_cycles_completed
        global_cycles_completed = 0

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.text_box.GetValue()
        text = "".join([_(u"New text box value: "), text_box_value])
        if self.state == 0:
            self.canvas_2d.render(text)
        else:
            self.canvas_3d.render()

    def run_command(self):
        """Run the simulation from scratch."""
        global global_cycles_completed
        global_cycles_completed = 0

        cycles = self.on_spin(wx.SpinCtrl)

        # check that this function has been called on pressing run button
        text = "".join(
            [_(u"run_command function has been called, number of cycles is: "), str(cycles)])
        if self.state == 0:
            self.canvas_2d.render(text, True)
        else:
            self.canvas_3d.render()

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            print("".join([_(u"Running for "), str(cycles), _(u" cycles")]))
            self.devices.cold_startup()
            if self.run_network(cycles):
                global_cycles_completed += cycles

    def continue_command(self):
        """Continue a previously run simulation."""
        cycles_cont = self.on_spin_cont(wx.SpinCtrl)
        global global_cycles_completed
        # check that this function has been called on pressing continue button
        text = "".join(
            [_(u"continue_command function has been called, number of cycles is: "), str(cycles_cont)])
        if self.state == 0:
            self.canvas_2d.render(text, True)
        else:
            self.canvas_3d.render()
        if cycles_cont is not None:  # if the number of cycles provided is valid
            if global_cycles_completed == 0:
                print(_(u"Error! Nothing to continue. Run first."))
            elif self.run_network(cycles_cont):
                global_cycles_completed += cycles_cont
                print(" ".join([_(u"Continuing for"), str(cycles_cont), _(u"cycles."), _(u"Total:"), str(
                    global_cycles_completed)]))

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print(_(u"Error! Network oscillating."))
                return False
        self.monitors.display_signals()
        text = "The signal trace is printed"
        if self.state == 0:
            self.canvas_2d.render(text, True)
        else:
            self.canvas_3d.render()
        return True


