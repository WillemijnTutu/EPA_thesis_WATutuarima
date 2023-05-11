import wx
import matplotlib as plt
import cv2

import osmnx as ox
import networkx as nx


class MyFrame(wx.Frame):

    def __init__(self):

        self.height=800
        self.width=1200
        super().__init__(parent=None, title='Route simulation', size=(self.width, self.height))


        self.filepath = "graph/rotterdam_drive_bbox_cameras_traffic_lights_bridges_roundabouts.graphml"
        self.graph = ox.load_graphml(self.filepath)

        # Stap 1, laten zien van initiele map file
        self.imagepath = "vis_image/vis_image.png"


        self.panel = wx.Panel(self)
        self.my_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The space to put the text
        # self.text_ctrl = wx.TextCtrl(panel)
        self.show_original_image()

        self.my_sizer.Add(self.imageCtrl, 0, wx.ALL | wx.LEFT | wx.EXPAND, 3)

        self.checkbox_sizer = wx.BoxSizer(wx.VERTICAL)

        self.cb1 = wx.CheckBox(self.panel, label='Obstacle avoidance')
        self.cb2 = wx.CheckBox(self.panel, label='Traffic avoidance ')
        self.cb3 = wx.CheckBox(self.panel, label='Risky')
        self.cb4 = wx.CheckBox(self.panel, label='Familiariy')
        self.cb5 = wx.CheckBox(self.panel, label='DPT')

        self.checkbox_sizer.Add(self.cb1, 0, wx.ALL)
        self.checkbox_sizer.Add(self.cb2, 0, wx.ALL)
        self.checkbox_sizer.Add(self.cb3, 0, wx.ALL)
        self.checkbox_sizer.Add(self.cb4, 0, wx.ALL)
        self.checkbox_sizer.Add(self.cb5, 0, wx.ALL)

        self.my_btn = wx.Button(self.panel, label='Run simulation')
        self.my_btn2 = wx.Button(self.panel, label='Reset')

        self.my_btn.Bind(wx.EVT_BUTTON, self.run_simulation)
        self.checkbox_sizer.Add(self.my_btn, 0, wx.ALL)

        self.my_btn2.Bind(wx.EVT_BUTTON, self.reset_simulation)
        self.checkbox_sizer.Add(self.my_btn2, 0, wx.ALL)

        self.my_sizer.Add(self.checkbox_sizer, 0, wx.ALL | wx.RIGHT)

        self.panel.SetSizer(self.my_sizer)
        self.Centre()
        self.Show(True)

        self.Show()

    def show_original_image(self):

        self.generate_image_file()

        self.img = wx.Image(self.imagepath, wx.BITMAP_TYPE_ANY)

        self.PhotoMaxSize = 800
        W = self.img.GetWidth()
        H = self.img.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * H / W
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * W / H
        self.img = self.img.Scale(NewW, NewH)

        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY,
                                         wx.Bitmap(self.img), style=wx.ALIGN_LEFT)


    def reset_simulation(self, event):
        self.show_original_image()
        self.panel.Refresh()

    def run_simulation(self, event):
        source = 44430463
        sink = 44465861
        route = ox.distance.shortest_path(self.graph, source, sink,
                                         weight='time_to_cross', cpus=1)

        fig, ax = plt.pyplot.subplots()
        ax.set_title('Graph - Shapes', fontsize=10)

        node_size = []
        node_color = []
        for node in self.graph.nodes:
            node_size.append(0)
            node_color.append('blue')

        ox.plot.plot_graph_route(
            self.graph, route, route_color='b', route_linewidth=4, route_alpha=0.5,
            orig_dest_size=100, ax=None,
            bgcolor="white", node_color=node_color, node_size=node_size, edge_linewidth=1, edge_color='lightgray',
            show=False, save=True, filepath=self.imagepath
        )

        self.img = wx.Image(self.imagepath, wx.BITMAP_TYPE_ANY)

        W = self.img.GetWidth()
        H = self.img.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * H / W
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * W / H
        self.img = self.img.Scale(NewW, NewH)

        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY,
                                         wx.Bitmap(self.img), style=wx.ALIGN_LEFT)

        self.panel.Refresh()

    def generate_image_file(self):

        # fig = plt.figure(figsize=(12, 12))
        fig, ax = plt.pyplot.subplots()
        ax.set_title('Graph - Shapes', fontsize=10)

        node_size = []
        node_color = []
        for node in self.graph.nodes:
            node_size.append(0)
            node_color.append('blue')

        ox.plot.plot_graph(
            self.graph, bgcolor="white", node_color=node_color, node_size=node_size, edge_linewidth=1,
            edge_color='lightgray', show=False, save=True, filepath=self.imagepath
        )


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()