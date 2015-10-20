MY_ARCHIVE = ""




global GENERATE_COMPILED_VERSION
GENERATE_COMPILED_VERSION = False

#<-------------------------------------------------------------------------->#
#----------------------------------------------------------------------------
# Name:         PyEmbeddedAssetManager.py
# Purpose:      Make asset repositories easier to maintain and refactor
#----------------------------------------------------------------------------

__version__ = "1.5"
__author__  = "Keith Brafford"
__date__    = "20 Oct 2015"

import wx
from wx.lib.embeddedimage import PyEmbeddedImage
import zipfile
import cStringIO
import base64
import os

global ArtManager
ArtManager = None

def GetArtManager():
    global ArtManager
    if ArtManager == None:
        ArtManager = _ArtManager()
    return ArtManager

class _ArtManager(object):
    def __init__(self, archive = MY_ARCHIVE, root=""):
        data = base64.decodestring(archive)
        self.zipfile = None
        self.assetusagelist = set([])
        if archive:
            self.zipfile = zipfile.ZipFile(cStringIO.StringIO(data),"r")
            self.assetusagelist = set(self.GetAssetList())
        self.root = root
        self.imagecache, self.bitmapcache, self.iconcache = {},{},{}
    def SetRoot(self, root):
        self.root = root
    def GetImage(self, filename):
        filename = os.path.join(self.root,filename)
        self.assetusagelist.discard(filename)
        if self.imagecache.has_key(filename):
            return self.imagecache[filename]
        bitmapfile = self.zipfile.open()
        image = wx.ImageFromStream(cStringIO.StringIO(bitmapfile.read()))
        self.imagecache[filename] = image
        return image
    def GetBitmap(self, filename):
        filename = os.path.join(self.root,filename)
        self.assetusagelist.discard(filename)
        if self.bitmapcache.has_key(filename):
            return self.bitmapcache[filename]
        bitmapfile = self.zipfile.open(filename)
        image = wx.ImageFromStream(cStringIO.StringIO(bitmapfile.read()))
        bitmap = image.ConvertToBitmap()
        self.bitmapcache[filename] = bitmap
        return bitmap
    def GetIcon(self, filename):
        filename = os.path.join(self.root,filename)
        self.assetusagelist.discard(filename)
        if self.iconcache.has_key(filename):
            return self.iconcache[filename]
        bitmapfile = self.zipfile.open(filename)
        pei =  PyEmbeddedImage(bitmapfile.read(), isBase64 = False)
        icon = pei.GetIcon()
        self.iconcache[filename] = icon
        return icon
    def GetAssetList(self):
        if self.zipfile:
            return self.zipfile.namelist()
        else:
            return []
    def GetNamedContents(self, name):
        filename = os.path.join(self.root,name)
        self.assetusagelist.discard(filename)
        fp = self.zipfile.open(filename)
        return fp.read()
    def GetLicense(self):
        return self.GetNamedContents("License.txt")
    def GetUnusedAssetList(self):
        return self.assetusagelist

if __name__ == "__main__":
    import tempfile
    import textwrap
    import shutil
    import sys
    import py_compile

    class InMemoryZip(object):
        """InMemoryZip class, courtesy of this stack overflow article:
   http://stackoverflow.com/questions/2463770/python-in-memory-zip-library"""
        def __init__(self):
            # Create the in-memory file-like object
            self.in_memory_zip = cStringIO.StringIO()

        def append(self, filename_in_zip, file_contents):
            '''Appends a file with name filename_in_zip and contents of
               file_contents to the in-memory zip.'''
            # Get a handle to the in-memory zip in append mode
            zf = zipfile.ZipFile(self.in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)
            # Write the file to the in-memory zip
            zf.writestr(filename_in_zip, file_contents)
            # Mark the files as having been created on Windows so that
            # Unix permissions are not inferred as 0000
            for zfile in zf.filelist:
                zfile.create_system = 0
            return self
        def read(self):
            '''Returns a string with the contents of the in-memory zip.'''
            self.in_memory_zip.seek(0)
            return self.in_memory_zip.read()

    def ExtractArchive(zf):
        """Extracts zip archive to temp folder"""
        tempdir = tempfile.mkdtemp()
        if zf:
            zf.extractall(tempdir)
        return tempdir

    def DeleteTempFiles(tempdir):
        try:
            shutil.rmtree(tempdir)
            return True
        except:
            return False

    def BundleArchive(tempdir):
        global GENERATE_COMPILED_VERSION
        zipfiledata = ""
        imz = InMemoryZip()
        rootlen = len(tempdir)
        if tempdir != None:
            for root, dirs, files in os.walk(tempdir):
                basedir = root[rootlen:]
                for filename in files:
                    if not filename.startswith("."):
                        with open(os.path.join(root,filename),"rb") as f:
                            contents = f.read()
                        zipfilename = os.path.join(basedir, filename)
                        imz.append(zipfilename,contents)
            zipfiledata = imz.read()
        b64data = base64.encodestring(zipfiledata)
        b64lines = textwrap.wrap(b64data, 80)
        b64lines = ['    "%s"\n' % line for line in b64lines]
        if len(b64lines) > 0:
            new_archive = ["MY_ARCHIVE = (\n"]
            new_archive.extend(b64lines)
            new_archive.append("            )\n\n\n\n\n")
        else:
            new_archive = ['MY_ARCHIVE = ""\n\n\n\n\n']
        new_archive.append("GENERATE_COMPILED_VERSION = %s\n\n\n\n" % str(GENERATE_COMPILED_VERSION))
        return new_archive

    def ProcessModule(new_archive, filename, template):
        global GENERATE_COMPILED_VERSION
        with open(template, "rb") as f:
            while True:
                line = f.readline()
                if line.startswith("#<---"):
                    keeper = [line]
                    keeper.extend(f.readlines())
                    break
        if not filename.endswith(".py"): filename += ".py"
        f = open(filename, "wb")
        f.writelines(new_archive)
        f.writelines(keeper)
        f.close()
        if GENERATE_COMPILED_VERSION:
            print "Doing compiled version"
            py_compile.compile(filename)

    class MyDialog(wx.Dialog):
        def __init__(self, parent, id = -1, artman = None):
            if artman == None:
                wx.MessageBox("No Asset Manager specified", "Error", wx.OK)
                self.EndModal(-1)
                return
            title = "Asset Manager - %s" % sys.argv[0]
            wx.Dialog.__init__(self, parent,id, title, pos = (5,5), style = wx.DEFAULT_DIALOG_STYLE)
            self.artman = artman
            self.button_delete = wx.Button(self, -1, "Delete Temp Files (No Reencode)")
            self.button_explore = wx.Button(self, -1, "Extract and Explore")
            self.button_encode = wx.Button(self, -1, "Encode And Repack")
            self.button_export = wx.Button(self, -1, "Export New Module")
#            self.checkbox_provider = wx.CheckBox(self, -1, "Include ArtProvider?")
            self.static_line = wx.StaticLine(self, -1, style = wx.LI_VERTICAL)
            self.static_line2 = wx.StaticLine(self, -1, style = wx.LI_VERTICAL)

            self.checkbox_compile = wx.CheckBox(self, -1, "Generate .pyc(o)", style = wx.ALIGN_RIGHT)

            self.buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
            self.buttonsizer.AddStretchSpacer()
            self.buttonsizer.Add(self.button_explore, 0, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT, 5)
            self.buttonsizer.AddSpacer(20)
            self.buttonsizer.Add(self.static_line, 0, wx.EXPAND | wx.ALL, 5)
            self.buttonsizer.AddSpacer(20)
#            self.buttonsizer.Add(self.checkbox_provider, 0, wx.ALIGN_CENTRE_VERTICAL |wx.LEFT | wx.RIGHT, 5)

            self.middlesizer = wx.BoxSizer(wx.VERTICAL)
            self.middletopsizer = wx.BoxSizer(wx.HORIZONTAL)
            self.middletopsizer.Add(self.button_encode, 0, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT,  10)
            self.middletopsizer.Add(self.button_export, 0, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT, 10)
            self.middlebottomsizer = wx.BoxSizer(wx.HORIZONTAL)
            self.middlebottomsizer.AddStretchSpacer()
            self.middlebottomsizer.Add(self.checkbox_compile, 0, wx.RIGHT, 25)
            self.middlebottomsizer.AddStretchSpacer()
            self.middlesizer.Add(self.middletopsizer,0)
            self.middlesizer.Add(self.middlebottomsizer,0, wx.BOTTOM | wx.TOP | wx.EXPAND, 5)

            self.buttonsizer.Add(self.middlesizer, 0)

            self.buttonsizer.AddSpacer(20)
            self.buttonsizer.Add(self.static_line2, 0, wx.EXPAND | wx.ALL, 5)
            self.buttonsizer.AddSpacer(20)

            self.buttonsizer.Add(self.button_delete,0, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
            self.buttonsizer.AddStretchSpacer()

#            self.app = ArtProviderPanel(self)

            self.mainsizer = wx.BoxSizer(wx.VERTICAL)
            self.mainsizer.Add(self.buttonsizer,0, wx.EXPAND | wx.TOP, 2)


#            self.mainsizer.Add(self.app, 0, wx.EXPAND)

            self.button_explore.Bind(wx.EVT_BUTTON, self.OnExplore)
            self.button_encode.Bind(wx.EVT_BUTTON, self.OnEncode)
            self.button_export.Bind(wx.EVT_BUTTON, self.OnExport)
            self.button_delete.Bind(wx.EVT_BUTTON, self.OnDelete)
#            self.checkbox_provider.Bind(wx.EVT_CHECKBOX, self.OnCheckBox)

#            self.checkbox_provider.Enable(False)
            self.button_encode.Enable(False)
            self.button_delete.Enable(False)
            self.button_export.Enable(False)
            self.checkbox_compile.Enable(False)

            self.Bind(wx.EVT_CLOSE, self.OnClose)

#            self.app.Hide()
            self.SetSizer(self.mainsizer)
            self.width, h = self.mainsizer.CalcMin()
            w,h = self.mainsizer.CalcMin()
            self.SetSize((self.width, h+30))
            self.checkbox_compile.SetValue(GENERATE_COMPILED_VERSION)

#        def OnCheckBox(self, event):
#            if self.checkbox_provider.GetValue():
#                self.app.Show(True)
#            else:
#                self.app.Show(False)
#            w,h = self.mainsizer.CalcMin()
#            self.SetSize((self.width, h+30))
#            self.Update()

        def OnClose(self, event):
            self.Destroy()
            import sys
            wx.CallLater(100, sys.exit,0)

        def OnDelete(self, event):
            self.button_delete.Enable(False)
            self.button_encode.Enable(False)
            wx.CallAfter(self.PerformDelete)

        def PerformDelete(self):
            while DeleteTempFiles(self.tempdir) == False:
                wx.MessageBox("Can not delete the temp files.  You may need to close the app","Error", wx.OK)
            self.Close()

        def OnExport(self, event):
            global GENERATE_COMPILED_VERSION
            import os
            dlg = wx.FileDialog(self, "Export New Module", os.getcwd(), "", "*.py", wx.FD_SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                GENERATE_COMPILED_VERSION = self.checkbox_compile.GetValue()
                new_archive = BundleArchive(self.tempdir)
                filename = dlg.GetPath()
                ourfile = sys.argv[0]
                self.button_delete.Enable(False)
                self.button_encode.Enable(False)
                self.checkbox_compile.Enable(False)
                ProcessModule(new_archive, filename, ourfile)
                self.PerformDelete()

        def OnEncode(self, event):
            global GENERATE_COMPILED_VERSION
            self.button_delete.Enable(False)
            self.button_encode.Enable(False)
            GENERATE_COMPILED_VERSION = self.checkbox_compile.GetValue()
            self.checkbox_compile.Enable(False)
            wx.BeginBusyCursor()
            wx.CallAfter(self.PerformEncode)

        def PerformEncode(self):
            new_archive = BundleArchive(self.tempdir)
            ProcessModule(new_archive, __file__, __file__)
            if DeleteTempFiles(self.tempdir) == False:
                wx.MessageBox("Can not delete the temp files.  You may need to close the app","Error", wx.OK)
            self.Close()

        def OnExplore(self, event):
            self.button_explore.Enable(False)
            if os.path.split(sys.argv[0])[1] not in ("PyEmbeddedImageManager.py", "PyEmbeddedImageManager.pyw"):
                self.button_encode.Enable(True)
            self.button_delete.Enable(True)
            self.button_export.Enable(True)
            self.checkbox_compile.Enable(True)

#            self.checkbox_provider.Enable(True)
            wx.CallAfter(self.PerformExtract)

        def PerformExtract(self):
            try:
                self.tempdir = ExtractArchive(self.artman.zipfile)
            except:
                wx.MessageBox("Extraction Failed.","Error", wx.OK)
                raise

            if sys.platform == "win32":
                exe = "explorer.exe"
            elif sys.platform == "darwin":
                exe = "open"
            elif sys.platform == "linux2":
                exe = "gnome-open"
            else:
                raise NotImplementedError("Not implemented for %s" % sys.platform)

            import subprocess
            subprocess.call([exe, "%s" % self.tempdir])


    a = wx.App()

    artman = GetArtManager()
    dlg = MyDialog(None, artman = artman)

    dlg.ShowModal()
    a.MainLoop()
