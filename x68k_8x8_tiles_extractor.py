# Simple & dirty X68000 8x8 tiles PNG pictures extractor.
# By Franck "hitchhikr" Charlet.

from pathlib import Path
import sys
import os
import png
import numpy
import wx

png_pic_name = ""
png_bitmap = 0
png_image = 0
png_bitmap_zoom_1 = 0
png_bitmap_zoom_2 = 0
png_bitmap_zoom_4 = 0
cur_png_bitmap = 0
global_pict_array = 0
dest_pict_array = 0
dest_png_array = 0
dest_txt_array = 0
src_static_bitmap = 0
dest_static_bitmap = 0
dest_bitmap = 0
tiles_number = 0
pos_in_pic = 0
max_tiles_view = 0
max_page = 0
picture_width = 0
picture_height = 0
# 1, 2 or 4
tiles_zoom = 2
tiles_size = 8
tiles_palettes = 16
tiles_changed = False

def convert_tiles(png_name, pic_name, pal_name, sprites, off_pic, off_pal):
    global global_pict_array

    with open(pic_name, "rb") as f:
        pict = bytearray()
        f.seek(off_pic, 0)
        print("Reading picture file...")
        pict = f.read(int(sprites) * 32)
    with open(pal_name, "rb") as f:
        pal = bytearray()
        f.seek(off_pal, 0)
        print("Reading palette file...")
        pal += f.read(512)
    red = bytearray(256)
    green = bytearray(256)
    blue = bytearray(256)
    print("Converting palette...")
    for i in range(256):
        color = ((pal[(i * 2)] << 8) + pal[(i * 2) + 1])
        blue[i] = int(float((color & 0x3e) >> 1) * 255.0 / 31.0)
        red[i] = int(float((color & 0x7c0) >> 6) * 255.0 / 31.0)
        green[i] = int(float((color & 0xf800) >> 11) * 255.0 / 31.0)
    global_pict_array = bytearray(int(sprites) * 8 * (8 * 16 * 3))
    global_pict_array = numpy.array(global_pict_array).reshape(8 * int(sprites),  (8 * 16 * 3))
    print("Converting tiles to RGBA...")
    for palette in range(16):
        off = 0
        for j in range(int(sprites)):
            for k in range(8):
                for i in range(2):
                    pixels = ((pict[(k * 4) + (i * 2) + off] << 8) + pict[(k * 4) + (i * 2) + 1 + off])
                    pixel1 = (pixels & 0xf000) >> 12
                    pixel2 = (pixels & 0x0f00) >> 8
                    pixel3 = (pixels & 0x00f0) >> 4
                    pixel4 = (pixels & 0x000f)
                    global_pict_array[k + (j * 8)][(i * 12) + (palette * 24)] = red[pixel1 + (palette * 16)]
                    global_pict_array[k + (j * 8)][(i * 12) + 1 + (palette * 24)] = green[pixel1 + (palette * 16)]
                    global_pict_array[k + (j * 8)][(i * 12) + 2 + (palette * 24)] = blue[pixel1 + (palette * 16)]
                    global_pict_array[k + (j * 8)][(i * 12) + 3 + (palette * 24)] = red[pixel2 + (palette * 16)]
                    global_pict_array[k + (j * 8)][(i * 12) + 4 + (palette * 24)] = green[pixel2 + (palette * 16)]
                    global_pict_array[k + (j * 8)][(i * 12) + 5 + (palette * 24)] = blue[pixel2 + (palette * 16)]
                    global_pict_array[k + (j * 8)][(i * 12) + 6 + (palette * 24)] = red[pixel3 + (palette * 16)]
                    global_pict_array[k + (j * 8)][(i * 12) + 7 + (palette * 24)] = green[pixel3 + (palette * 16)]
                    global_pict_array[k + (j * 8)][(i * 12) + 8 + (palette * 24)] = blue[pixel3 + (palette * 16)]
                    global_pict_array[k + (j * 8)][(i * 12) + 9 + (palette * 24)] = red[pixel4 + (palette * 16)]
                    global_pict_array[k + (j * 8)][(i * 12) + 10 + (palette * 24)] = green[pixel4 + (palette * 16)]
                    global_pict_array[k + (j * 8)][(i * 12) + 11 + (palette * 24)] = blue[pixel4 + (palette * 16)]
            off += 0x20
    print("Done.")

def set_bitmap(array):
    width = int(array.shape[1] / 3)
    height = array.shape[0]
    image = wx.Image(width, height)
    image.SetData(array.tobytes())
    return image

def draw_tiles(bm, array):
    bm.CopyFromBuffer(array.tobytes(), wx.BitmapBufferFormat_RGB)

def create_context(self):
    global dest_pict_array
    global dest_bitmap
    global dest_static_bitmap
    global dest_txt_array
    global dest_png_array
    global picture_width
    global picture_height
    global png_bitmap_zoom_1
    global png_bitmap_zoom_2
    global png_bitmap_zoom_4
    global cur_png_bitmap
    global src_static_bitmap
    global tiles_zoom
    global tiles_size
    global tiles_number
    global pos_in_pic
    global max_page
    global max_tiles_view

    if(tiles_zoom == 1):
        cur_png_bitmap = png_bitmap_zoom_1
    if(tiles_zoom == 2):
        cur_png_bitmap = png_bitmap_zoom_2
    if(tiles_zoom == 4):
        cur_png_bitmap = png_bitmap_zoom_4

    self.window.DestroyChildren()

    # create destination bitmap
    dest_pict_array = numpy.zeros((picture_height * tiles_zoom, tiles_size * tiles_zoom, 3), 'uint8')
    dest_pict_array[:,:,] = (0, 0, 0)

    dest_bitmap = wx.Bitmap()
    dest_bitmap.CreateWithDIPSize((tiles_size, picture_height), tiles_zoom)
    dest_static_bitmap = wx.StaticBitmap()
    
    self.SetAutoLayout(False)
    self.window.SetScrollbars(0, int(tiles_size * tiles_zoom), 0, tiles_number)
    self.window.SetScrollRate(0, int(tiles_size * tiles_zoom))
    winsize = wx.Size()
    winsize = self.GetSize()
    winsize.Width = ((tiles_size * tiles_palettes) * tiles_zoom) + ((tiles_size * tiles_zoom) * 2) + (wx.SystemSettings.GetMetric(wx.SYS_HSCROLL_Y) * 2)
    pos_in_pic = 0

    self.window.WindowToClientSize(winsize)
    self.WindowToClientSize(winsize)
    self.window.SetSize(winsize)
    self.SetSize(winsize)
    self.ClearBackground()
    self.window.ClearBackground()
    
    # selected tiles
    dest_static_bitmap.Create(self.window, 0,
                                           pos = ((picture_width * tiles_zoom) + (tiles_size * tiles_zoom), 0),
                                           size = (tiles_size, picture_height))
    dest_static_bitmap.Bind(wx.EVT_LEFT_DOWN, self.on_left_down_dest_tiles)

    # whole tiles
    src_static_bitmap = wx.StaticBitmap(self.window, 0, wx.Bitmap(cur_png_bitmap), (0, 0), (picture_width * tiles_zoom, picture_height * tiles_zoom))
    src_static_bitmap.Bind(wx.EVT_LEFT_DOWN, self.on_left_down_src_tiles)
    self.window.Centre(wx.BOTH)
    self.Centre(wx.BOTH)
    
    for y in range(tiles_number):
        dither = 0
        for j in range(tiles_size):
            for i in range(tiles_size):
                # no index
                dither_pattern = 0
                if(dest_txt_array[y] == 127):
                    red = 0
                    green = 0
                    blue = 0
                    dither_pattern = 127
                else:
                    red = cur_png_bitmap.GetRed(    (dest_txt_array[y] * tiles_size * tiles_zoom) + (i * tiles_zoom), (y * tiles_size * tiles_zoom) + (j * tiles_zoom))
                    green = cur_png_bitmap.GetGreen((dest_txt_array[y] * tiles_size * tiles_zoom) + (i * tiles_zoom), (y * tiles_size * tiles_zoom) + (j * tiles_zoom))
                    blue = cur_png_bitmap.GetBlue(  (dest_txt_array[y] * tiles_size * tiles_zoom) + (i * tiles_zoom), (y * tiles_size * tiles_zoom) + (j * tiles_zoom))
                for k in range(tiles_zoom):
                    for l in range(tiles_zoom):
                        dest_pict_array[(y * tiles_size * tiles_zoom) + (j * tiles_zoom) + l, (i * tiles_zoom) + k, 0] = red ^ dither
                        dest_pict_array[(y * tiles_size * tiles_zoom) + (j * tiles_zoom) + l, (i * tiles_zoom) + k, 1] = green ^ dither
                        dest_pict_array[(y * tiles_size * tiles_zoom) + (j * tiles_zoom) + l, (i * tiles_zoom) + k, 2] = blue ^ dither
                dither ^= dither_pattern
                dest_png_array[(y * tiles_size) + j][(i * 3) + 0] = red
                dest_png_array[(y * tiles_size) + j][(i * 3) + 1] = green
                dest_png_array[(y * tiles_size) + j][(i * 3) + 2] = blue
            dither ^= dither_pattern
    draw_tiles(dest_bitmap, dest_pict_array)
    dest_static_bitmap.SetBitmap(dest_bitmap)
    
def save_indexes_file():
    global png_pic_name
    global dest_txt_array
    global tiles_changed

    name = png_pic_name
    name = name + ".idx"
    with open(name, "wb") as f:
        print("Saving tiles indexes file...")
        dest_txt_array = bytes(dest_txt_array)
        header = bytearray(4)
        header[0] = 0x54
        header[1] = 0x49
        header[2] = 0x4c
        header[3] = 0x53
        f.write(header)
        f.write(dest_txt_array)
        dest_txt_array = list(dest_txt_array)
        print("Done.")
        tiles_changed = False

class MyFrame(wx.Frame):
    def __init__(self):

        global png_pic_name
        global png_bitmap
        global png_image
        global png_bitmap_zoom_1
        global png_bitmap_zoom_2
        global png_bitmap_zoom_4
        global global_pict_array
        global max_tiles_view
        global max_page
        global picture_width
        global picture_height
        global dest_png_array
        global dest_txt_array
        global tiles_zoom
        global tiles_palettes
        global tiles_number
        global tiles_size
        global tiles_changed

        tiles_changed = False

        # set the window
        super().__init__(parent = None, title = "Select tiles to be exported or removed to/from the final picture", 
                                       size = wx.Size( ((tiles_size * tiles_palettes) * tiles_zoom) + ((tiles_size * tiles_zoom) * 2) + (wx.SystemSettings.GetMetric(wx.SYS_HSCROLL_Y) * 2),
                                       800))
        super().Centre(wx.BOTH)

        # get the content of the png file
        png_image = set_bitmap(global_pict_array)
        png_bitmap = png_image.ConvertToBitmap()
        picture_width = png_bitmap.GetWidth()
        picture_height = png_bitmap.GetHeight()

        png_bitmap_zoom_1 = png_image.Scale(picture_width * 1, picture_height * 1, wx.IMAGE_QUALITY_NORMAL)
        png_bitmap_zoom_2 = png_image.Scale(picture_width * 2, picture_height * 2, wx.IMAGE_QUALITY_NORMAL)
        png_bitmap_zoom_4 = png_image.Scale(picture_width * 4, picture_height * 4, wx.IMAGE_QUALITY_NORMAL)
        
        # set the scrolled window
        self.window = wx.ScrolledWindow(self, size = wx.Size( ((tiles_size * tiles_palettes) * tiles_zoom) + ((tiles_size * tiles_zoom) * 2) + (wx.SystemSettings.GetMetric(wx.SYS_HSCROLL_Y) * 2),
                                              800), style = wx.FULL_REPAINT_ON_RESIZE)
        self.window.SetBackgroundColour((0, 0, 0))
        
        dest_png_array = bytearray(tiles_number * tiles_size * (tiles_size * 3))
        dest_png_array = numpy.array(dest_png_array).reshape(tiles_size * tiles_number, (tiles_size * 3))
        dest_png_array[:] = 0
        dest_txt_array = bytearray(tiles_number)
        dest_txt_array = numpy.array(dest_txt_array).reshape(tiles_number)
        dest_txt_array[:] = 127

        # load the indexes file (if any) and draw them
        name = png_pic_name
        name = name + ".idx"
        if(os.path.isfile(name) == True):
            with open(name, "rb") as f:
                size = os.path.getsize(name)
                if(size):
                    header = bytearray(4)
                    header = f.read(4)
                    if(header[0] == 0x54 and header[1] == 0x49 and header[2] == 0x4c and header[3] == 0x53):
                        print("Found tiles indexes file, loading...")
                        size = size - 4
                        dest_txt_array = f.read(int(size))
                        dest_txt_array = list(dest_txt_array)
                        print("Done.")

        create_context(self)

        menu_bar = wx.MenuBar()
        project_menu = wx.Menu()
        project_menu.Append(wx.MenuItem(project_menu, 200, "Save all tiles as PNG\tCtrl+S", kind = wx.ITEM_NORMAL))
        project_menu.Append(wx.MenuItem(project_menu, 201, "Save selected tiles as PNG\tCtrl+T", kind = wx.ITEM_NORMAL))
        project_menu.Append(wx.MenuItem(project_menu, 202, "Save selected tiles indexes\tCtrl+I", kind = wx.ITEM_NORMAL))
        project_menu.AppendSeparator()
        project_menu.Append(wx.MenuItem(project_menu, wx.ID_CLEAR, "Reset all selected tiles\tCtrl+R", kind = wx.ITEM_NORMAL))
        project_menu.AppendSeparator()
        project_menu.Append(wx.MenuItem(project_menu, 204, "Zoom X1\tCtrl+1", kind = wx.ITEM_CHECK))
        project_menu.Append(wx.MenuItem(project_menu, 205, "Zoom X2\tCtrl+2", kind = wx.ITEM_CHECK))
        project_menu.Append(wx.MenuItem(project_menu, 206, "Zoom X4\tCtrl+4", kind = wx.ITEM_CHECK))
        if(tiles_zoom == 1):
            project_menu.FindItemById(204).Check(True)
        if(tiles_zoom == 2):
            project_menu.FindItemById(205).Check(True)
        if(tiles_zoom == 4):
            project_menu.FindItemById(206).Check(True)

        project_menu.AppendSeparator()
        project_menu.Append(wx.MenuItem(project_menu, wx.ID_EXIT, "Exit\tCtrl+Q", kind = wx.ITEM_NORMAL))
        menu_bar.Append(project_menu, "&Project")
        about_menu = wx.Menu()
        about_menu.Append(wx.MenuItem(project_menu, wx.ID_ABOUT, "About\tCtrl+A", kind = wx.ITEM_NORMAL))
        menu_bar.Append(about_menu, "&Help")
        self.SetMenuBar(menu_bar)
        self.Bind(wx.EVT_MENU, self.on_menu_close)

        super().Bind(wx.EVT_SIZE, self.on_resize)

        self.window.Bind(wx.EVT_SCROLLWIN_TOP, self.on_scrollwin_top)
        self.window.Bind(wx.EVT_SCROLLWIN_BOTTOM, self.on_scrollwin_bottom)
        self.window.Bind(wx.EVT_SCROLLWIN_LINEUP, self.on_scrollwin_lineup)
        self.window.Bind(wx.EVT_SCROLLWIN_LINEDOWN, self.on_scrollwin_linedown)
        self.window.Bind(wx.EVT_SCROLLWIN_PAGEUP, self.on_scrollwin_pageup)
        self.window.Bind(wx.EVT_SCROLLWIN_PAGEDOWN, self.on_scrollwin_pagedown)
        self.window.Bind(wx.EVT_SCROLLWIN_THUMBTRACK, self.on_scrollwin_thumbtrack)
        self.window.Bind(wx.EVT_SCROLLWIN_THUMBRELEASE, self.on_scrollwin_thumbrelease)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Show()

    def on_close(self, event):
        global tiles_changed

        if(tiles_changed == True):
            msg = wx.GenericMessageDialog(self, "Selected tiles have been modified\nDo you want to save the indexes file ?" , "Your choice", wx.YES_NO | wx.CANCEL)
            ret = msg.ShowModal()
            if(ret == wx.ID_NO):
                event.Skip()
            if(ret == wx.ID_YES):
                save_indexes_file()
                event.Skip()
            # cancel is implied and blocks the event
        else:
            event.Skip()

    def on_menu_close(self, event):
        global png_pic_name
        global dest_bitmap
        global dest_static_bitmap
        global dest_pict_array
        global dest_png_array
        global dest_txt_array
        global tiles_number
        global tiles_changed
        global tiles_zoom

        id = event.GetId()

        # save all tiles
        if(id == 200):
            print("Saving whole tiles as PNG picture...")
            png.from_array(global_pict_array, 'RGB').save(png_pic_name)
            print("Done.")

        # save selected tiles
        if(id == 201):
            print("Saving selected tiles as PNG picture...")
            png.from_array(dest_png_array, 'RGB').save(png_pic_name)
            print("Done.")

        # save indexes file
        if(id == 202):
            save_indexes_file()
        
        # reset all selected tiles
        if(id == wx.ID_CLEAR):
            for y in range(tiles_number):
                dither = 0
                for j in range(tiles_size):
                    for i in range(tiles_size):
                        dither_pattern = 127
                        for k in range(tiles_zoom):
                            for l in range(tiles_zoom):
                                dest_pict_array[(y * tiles_size * tiles_zoom) + (j * tiles_zoom) + l, (i * tiles_zoom) + k, 0] = 0 ^ dither
                                dest_pict_array[(y * tiles_size * tiles_zoom) + (j * tiles_zoom) + l, (i * tiles_zoom) + k, 1] = 0 ^ dither
                                dest_pict_array[(y * tiles_size * tiles_zoom) + (j * tiles_zoom) + l, (i * tiles_zoom) + k, 2] = 0 ^ dither
                        dest_png_array[(y * tiles_size) + j][(i * 3) + 0] = 0
                        dest_png_array[(y * tiles_size) + j][(i * 3) + 1] = 0
                        dest_png_array[(y * tiles_size) + j][(i * 3) + 2] = 0
                        dither ^= dither_pattern
                    dither ^= dither_pattern
                if(dest_txt_array[y] != 127):
                    tiles_changed = True
                dest_txt_array[y] = 127
            draw_tiles(dest_bitmap, dest_pict_array)
            dest_static_bitmap.SetBitmap(dest_bitmap)

        # zoom x1
        if(id == 204):
            self.GetMenuBar().FindItemById(id).Check(True)
            self.GetMenuBar().FindItemById(205).Check(False)
            self.GetMenuBar().FindItemById(206).Check(False)
            tiles_zoom = 1
            create_context(self)

        # zoom x2
        if(id == 205):
            self.GetMenuBar().FindItemById(204).Check(False)
            self.GetMenuBar().FindItemById(id).Check(True)
            self.GetMenuBar().FindItemById(206).Check(False)
            tiles_zoom = 2
            create_context(self)

        # zoom x4
        if(id == 206):
            self.GetMenuBar().FindItemById(204).Check(False)
            self.GetMenuBar().FindItemById(205).Check(False)
            self.GetMenuBar().FindItemById(id).Check(True)
            tiles_zoom = 4
            create_context(self)
        
        # exit
        if(id == wx.ID_EXIT):
            self.Close()

        # about
        if(id == wx.ID_ABOUT):
            msg = wx.GenericMessageDialog(self, "Simple & dirty X68000 tiles/sprites extractor\nWritten by Franck 'hitchhikr' Charlet." , "About", wx.OK)
            ret = msg.ShowModal()

    # select a tile
    def on_left_down_src_tiles(self, event):
        global cur_png_bitmap
        global dest_bitmap
        global dest_static_bitmap
        global dest_pict_array
        global dest_png_array
        global dest_txt_array
        global tiles_changed
        global tiles_size
        global tiles_zoom

        x = int((event.Position.x + 1) / int(tiles_size * tiles_zoom))
        y = int((event.Position.y + 1) / int(tiles_size * tiles_zoom))

        if(x > (tiles_palettes - 1)):
            x = (tiles_palettes - 1)

        for j in range(tiles_size):
            for i in range(tiles_size):
                red = cur_png_bitmap.GetRed(    (x * tiles_size * tiles_zoom) + (i * tiles_zoom), (y * tiles_size * tiles_zoom) + (j * tiles_zoom))
                green = cur_png_bitmap.GetGreen((x * tiles_size * tiles_zoom) + (i * tiles_zoom), (y * tiles_size * tiles_zoom) + (j * tiles_zoom))
                blue = cur_png_bitmap.GetBlue(  (x * tiles_size * tiles_zoom) + (i * tiles_zoom), (y * tiles_size * tiles_zoom) + (j * tiles_zoom))
                for k in range(tiles_zoom):
                    for l in range(tiles_zoom):
                        dest_pict_array[(y * tiles_size * tiles_zoom) + (j * tiles_zoom) + l, (i * tiles_zoom) + k, 0] = red
                        dest_pict_array[(y * tiles_size * tiles_zoom) + (j * tiles_zoom) + l, (i * tiles_zoom) + k, 1] = green
                        dest_pict_array[(y * tiles_size * tiles_zoom) + (j * tiles_zoom) + l, (i * tiles_zoom) + k, 2] = blue
                dest_png_array[(y * tiles_size) + j][(i * 3) + 0] = red
                dest_png_array[(y * tiles_size) + j][(i * 3) + 1] = green
                dest_png_array[(y * tiles_size) + j][(i * 3) + 2] = blue

        # mark it as changed
        if(dest_txt_array[y] != x):
            tiles_changed = True

        dest_txt_array[y] = x

        draw_tiles(dest_bitmap, dest_pict_array)
        dest_static_bitmap.SetBitmap(dest_bitmap)

    # unselect a tile
    def on_left_down_dest_tiles(self, event):
        global dest_bitmap
        global dest_static_bitmap
        global dest_pict_array
        global dest_png_array
        global dest_txt_array
        global tiles_changed
        global tiles_size
        global tiles_zoom

        y = int((event.Position.y) / int(tiles_size * tiles_zoom))

        dither = 0
        for j in range(tiles_size):
            for i in range(tiles_size):
                dither_pattern = 127
                for k in range(tiles_zoom):
                    for l in range(tiles_zoom):
                        dest_pict_array[(y * tiles_size * tiles_zoom) + (j * tiles_zoom) + l, (i * tiles_zoom) + k, 0] = 0 ^ dither
                        dest_pict_array[(y * tiles_size * tiles_zoom) + (j * tiles_zoom) + l, (i * tiles_zoom) + k, 1] = 0 ^ dither
                        dest_pict_array[(y * tiles_size * tiles_zoom) + (j * tiles_zoom) + l, (i * tiles_zoom) + k, 2] = 0 ^ dither
                dest_png_array[(y * tiles_size) + j][(i * 3) + 0] = 0
                dest_png_array[(y * tiles_size) + j][(i * 3) + 1] = 0
                dest_png_array[(y * tiles_size) + j][(i * 3) + 2] = 0
                dither ^= dither_pattern
            dither ^= dither_pattern

        # mark it as changed
        if(dest_txt_array[y] != 127):
            tiles_changed = True

        dest_txt_array[y] = 127

        draw_tiles(dest_bitmap, dest_pict_array)
        dest_static_bitmap.SetBitmap(dest_bitmap)

    def on_resize(self, event):
        global pos_in_pic
        global max_page
        global max_tiles_view
        global picture_height
        global tiles_number
        global tiles_size
        global tiles_zoom

        self.window.SetSize(0, 0, self.GetClientSize().GetWidth(), self.GetClientSize().GetHeight())
        max_page = int(self.GetClientSize().GetHeight() / (tiles_size * tiles_zoom))
        max_tiles_view = tiles_number - max_page
        if(pos_in_pic > max_tiles_view):
            pos_in_pic = max_tiles_view
        self.window.Scroll(0, pos_in_pic)

    def on_scrollwin_top(self, event):
        global pos_in_pic

        pos_in_pic = 0
        self.window.Scroll(0, pos_in_pic)

    def on_scrollwin_bottom(self, event):
        global pos_in_pic
        global max_tiles_view

        pos_in_pic = max_tiles_view
        self.window.Scroll(0, pos_in_pic)

    def on_scrollwin_lineup(self, event):
        global pos_in_pic

        pos_in_pic = pos_in_pic - 1
        if(pos_in_pic < 0):
            pos_in_pic = 0
        self.window.Scroll(0, pos_in_pic)

    def on_scrollwin_linedown(self, event):
        global pos_in_pic
        global max_tiles_view

        pos_in_pic = pos_in_pic + 1
        if(pos_in_pic > max_tiles_view):
            pos_in_pic = max_tiles_view
        self.window.Scroll(0, pos_in_pic)

    def on_scrollwin_pageup(self, event):
        global pos_in_pic
        global max_page

        pos_in_pic = pos_in_pic - max_page
        if(pos_in_pic < 0):
            pos_in_pic = 0
        self.window.Scroll(0, pos_in_pic)

    def on_scrollwin_pagedown(self, event):
        global pos_in_pic
        global max_tiles_view
        global max_page

        pos_in_pic = pos_in_pic + max_page
        if(pos_in_pic > max_tiles_view):
            pos_in_pic = max_tiles_view
        self.window.Scroll(0, pos_in_pic)

    def on_scrollwin_thumbtrack(self, event):
        global pos_in_pic

        pos_in_pic = event.Position
        self.window.Scroll(0, pos_in_pic)

    def on_scrollwin_thumbrelease(self, event):
        global pos_in_pic

        pos_in_pic = event.Position
        self.window.Scroll(0, pos_in_pic)

class UsageFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent = None),
        msg = wx.GenericMessageDialog(self, "x68k_8x8_tiles_extractor <png picture file> <tiles file> <palette file> <number of tiles> [offset in pic file] [offset in pal file]" , "Usage", wx.OK)
        ret = msg.ShowModal()

def main():
    global png_pic_name
    global tiles_number

    print('x68k_8x8_tiles_extractor by Franck "hitchhikr" Charlet.')
    if len(sys.argv) < 5:
        if(sys.executable.endswith("pythonw.exe")):
            app = wx.App()
            UsageFrame()
        else:
            print("Usage: x68k_8x8_tiles_extractor <png picture file> <tiles file> <palette file> <number of tiles> [offset in pic file] [offset in pal file]")
        return
    if len(sys.argv) < 6:
        offset_pic = 0
    else:
        offset_pic = int(sys.argv[5])
    if len(sys.argv) < 7:
        offset_pal = 0
    else:
        offset_pal = int(sys.argv[6])
    png_pic_name = sys.argv[1]
    tiles_number = int(sys.argv[4])
    convert_tiles(png_pic_name, sys.argv[2], sys.argv[3], sys.argv[4], offset_pic, offset_pal)

    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
