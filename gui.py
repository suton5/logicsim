"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser



class MyGLCanvas(wxcanvas.GLCanvas):
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

    def render(self, text, reset = 0):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        """
        #from display_signals in Monitors
        margin = self.monitors.get_margin()
        for device_id, output_id in self.monitors.monitors_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            name_length = len(monitor_name)
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]
            print(monitor_name + (margin - name_length) * " ", end=": ")
            
            GL.glClear(GL.GL_COLOR_BUFFER_BIT)
            #self.render_text(text, 10, 10)
            GL.glColor3f(0.0, 0.0, 1.0)
            GL.glBegin(GL.GL_LINE_STRIP)

            for index, signal in enumerate(signal_list):
                x = (index - 1) * 20 + 10
                x_next = (index - 1) * 20 + 30
                
                if signal == self.devices.HIGH:
                    y = 100
                if signal == self.devices.LOW:
                    y = 75
                    
                #if signal == self.devices.RISING:
                #if signal == self.devices.FALLING:
                #if signal == self.devices.BLANK:

                GL.glVertex2f(x, y)
                GL.glVertex2f(x_next, y)
            GL.glEnd()

            # We have been drawing to the back buffer, flush the graphics pipeline
            # and swap the back buffer to the front
            GL.glFlush()
            self.SwapBuffers()


        """
        
        #if reset == 0:
        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(10):
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            if i % 2 == 0:
                y = 75
            else:
                y = 100
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
        GL.glEnd()
 
        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()
       

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

class MyDialog_monitor(wx.Dialog):
    def __init__(self, parent, title):
        super(MyDialog_monitor, self).__init__(parent, title = title, size = (250,150))
        
        """
            self.switches=[]
            def array_adder(self):
            for switch in array:
            self.switches.append(wx.CheckBox(panel, label = 'Switch 1',pos = (10,10))
        """
        
        panel = wx.Panel(self)
        self.signal_1 = wx.CheckBox(panel, label = 'Signal 1',pos = (10,10))
        self.signal_2 = wx.CheckBox(panel, label = 'Signal 2',pos = (10,40))
        self.signal_3 = wx.CheckBox(panel, label = 'Signal 3',pos = (10,70))
        
        self.signal_1.Bind(wx.EVT_CHECKBOX,self.monitor_command)
        self.signal_2.Bind(wx.EVT_CHECKBOX,self.monitor_command)
        self.signal_3.Bind(wx.EVT_CHECKBOX,self.monitor_command)
        
        self.btn = wx.Button(panel, wx.ID_OK, label = "ok", size = (50,20), pos = (10,100))

    # Need to return the correct items, i.e. [device_id, port_id]
    def onChecked_monitor(self,event):
        signal_monitor = event.GetEventObject()
        #print(signal.GetLabel(), 'is clicked', signal.GetValue())
        return signal_monitor.GetLabel(), signal_monitor.GetValue()
    
    
    def monitor_command(self, event):
        """Set the specified monitor."""
        monitor = self.onChecked_monitor(event)
        if monitor is not None:
            [device, port] = monitor
            monitor_error = self.monitors.make_monitor(device, port,
                                                       self.cycles_completed)
            if monitor_error == self.monitors.NO_ERROR:
                print("Successfully made monitor.")
            else:
                print("Error! Could not make monitor.")



class MyDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(MyDialog, self).__init__(parent, title = title, size = (250,150))
        
        """
        self.switches=[]
        def array_adder(self):
            for switch in array:
            self.switches.append(wx.CheckBox(panel, label = 'Switch 1',pos = (10,10))
        """
        
              
        panel = wx.Panel(self)
        self.switch_1 = wx.CheckBox(panel, label = 'Switch 1',pos = (10,10))
        self.switch_2 = wx.CheckBox(panel, label = 'Switch 2',pos = (10,40))
        self.switch_3 = wx.CheckBox(panel, label = 'Switch 3',pos = (10,70))
        
        self.switch_1.Bind(wx.EVT_CHECKBOX,self.switch_command)
        self.switch_2.Bind(wx.EVT_CHECKBOX,self.switch_command)
        self.switch_3.Bind(wx.EVT_CHECKBOX,self.switch_command)
        
        self.btn = wx.Button(panel, wx.ID_OK, label = "ok", size = (50,20), pos = (10,100))

    def onChecked(self,event):
        signal = event.GetEventObject()
        #print(signal.GetLabel(), 'is clicked', signal.GetValue())
        return signal.GetLabel(), signal.GetValue()
    
    
    def switch_command(self, event):
        """Set the specified switch to the specified signal level."""
        switch_id = self.onChecked(event)[0]
        if switch_id is not None:
            #print(switch_id)
            switch_state = self.onChecked(event)[1]
            if switch_state == True:
                switch_state = 1
            else:
                switch_state = 0
            print(switch_id, switch_state)
            """
                if switch_state is not None:
                if self.devices.set_switch(switch_id, switch_state):
                print("Successfully set switch.")
                else:
                print("Error! Invalid switch.")
                """


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
        fileMenu = wx.Menu()
        #fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(102, "&About")
        fileMenu.Append(wx.ID_NEW, "&New", "Create new session")
        fileMenu.Append(wx.ID_OPEN, "&Open")
        fileMenu.Append(wx.ID_SAVE, "&Save")       
        fileMenu.Append(wx.ID_PRINT, "&Print")
        #fileMenu.Append(wx.ID_EXIT, "&Exit")
        fileMenu.Append(103, "&Exit")
      
        # Create the menu bar
        menuBar = wx.MenuBar()
        # Adding the "file menu" to the menu bar
        menuBar.Append(fileMenu, "&File")
        # Adding the menu bar to the frame content
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Configure the widgets
        self.text_run = wx.StaticText(self, wx.ID_ANY, "Cycles to run")
        self.text_cont = wx.StaticText(self, wx.ID_ANY, "Cycles to continue")
        self.spin_run = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.spin_cont = wx.SpinCtrl(self, wx.ID_ANY, "2")
        self.run = wx.Button(self, wx.ID_ANY, "Run")
        self.cont = wx.Button(self, wx.ID_ANY, "Continue")
        self.text_box = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER)
        self.ResetButton = wx.Button(self, wx.ID_ANY, "Reset")
        self.set_switch = wx.Button(self, wx.ID_ANY, "Set Switches")
        self.select_monitor = wx.Button(self, wx.ID_ANY, "Monitor")
        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin_run.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.spin_cont.Bind(wx.EVT_SPINCTRL, self.on_spin_cont)
        self.run.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.cont.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)
        self.ResetButton.Bind(wx.EVT_BUTTON, self.on_reset_button)
        self.set_switch.Bind(wx.EVT_BUTTON, self.check_box)
        self.select_monitor.Bind(wx.EVT_BUTTON, self.check_box_monitor)
        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        side_sizer.Add(self.text_run, 1, wx.TOP, 10)
        side_sizer.Add(self.spin_run, 1, wx.ALL, 5)
        side_sizer.Add(self.run, 1, wx.ALL, 5)
        side_sizer.Add(self.text_cont, 1, wx.TOP, 10)
        side_sizer.Add(self.spin_cont, 1, wx.ALL, 5)
        side_sizer.Add(self.cont, 1, wx.ALL, 5)
        side_sizer.Add(self.ResetButton, 1, wx.ALL, 5)
        side_sizer.Add(self.text_box, 1, wx.ALL, 5)
        side_sizer.Add(self.set_switch, 1, wx.ALL, 5)
        side_sizer.Add(self.select_monitor, 1, wx.ALL, 5)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

        # A modal show will lock out the other windows until it has been dealth with
        # Very useful in some programming tasks to ensure that things happen in an order
        # that the programmer expects, but can be very frustrating to the user if it is
        # used to excess
        self.exitconfirmation = wx.MessageDialog(self, "Exit - Are you Sure? \n", "Confirmation", wx.YES_NO)
    
    def check_box_monitor(self, event):
        MyDialog_monitor(self, "Tick to select signals to monitor").ShowModal()
        #self.Centre()
        #self.Show(True)
        print('check_box_monitor is called')
    
    def check_box(self, event):
        MyDialog(self, "Tick to set the switches to 1").ShowModal()
        #self.Centre()
        #self.Show(True)
        print('check_box is called')

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            exitconf=self.exitconfirmation.ShowModal()
            if exitconf == wx.ID_YES:
                self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)
    
    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin_run.GetValue()
        text = "".join(["New run spin control value: ", str(spin_value)])
        self.canvas.render(text)
        return spin_value
    
    def on_spin_cont(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value_cont = self.spin_cont.GetValue()
        text = "".join(["New continue spin control value: ", str(spin_value_cont)])
        self.canvas.render(text)
        return spin_value_cont

    
    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        self.canvas.render(text)
        self.run_command()
    
    def on_continue_button(self, event):
        """Handle the event when the user clicks the Continue button."""
        text = "Continue button pressed."
        self.canvas.render(text)
        self.continue_command()
    
    def on_reset_button(self, event):
        """Handle the event when the user clicks the reset button."""
        text = "Reset button pressed."
        #self.canvas.render(text, reset = 1)
        self.canvas.render(text)

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.text_box.GetValue()
        text = "".join(["New text box value: ", text_box_value])
        self.canvas.render(text)

    def run_command(self):
        """Run the simulation from scratch."""
        self.cycles_completed = 0
        
        cycles = self.on_spin(wx.SpinCtrl)
        
        #check that this function has been called on pressing run button
        text = "".join(["run_command function has been called, number of cycles is: ", str(cycles)])
        self.canvas.render(text)
        
        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            print("".join(["Running for ", str(cycles), " cycles"]))
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles

    def continue_command(self):
        """Continue a previously run simulation."""
        cycles_cont = self.on_spin_cont(wx.SpinCtrl)
        
        #check that this function has been called on pressing continue button
        text = "".join(["continue_command function has been called, number of cycles is: ", str(cycles_cont)])
        self.canvas.render(text)
        if cycles_cont is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                print("Error! Nothing to continue. Run first.")
            elif self.run_network(cycles):
                self.cycles_completed += cycles
                print(" ".join(["Continuing for", str(cycles), "cycles.",
                                "Total:", str(self.cycles_completed)]))


