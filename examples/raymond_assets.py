MY_ARCHIVE = (
    "UEsDBBQAAAAIAHGYfE7ohFjAQwAAAGwAAAAMAAAAcmF5bW9uZC5odG1ss8koyc2x4+VSAAKbjNTEFCgb"
    "zC/JLMlJtVOorlYAsxRqaxVs9CGCUB36UC02SfkplSBBoFoQE6gUKKgPFQUqA9kCAFBLAQIUABQAAAAI"
    "AHGYfE7ohFjAQwAAAGwAAAAMAAAAAAAAAAAAAACAAQAAAAByYXltb25kLmh0bWxQSwUGAAAAAAEAAQA6"
    "AAAAbQAAAAAA"
            )

#<-------------------------------------------------------------------------->#
#----------------------------------------------------------------------------
# Name:         PyEmbeddedAssetManager.py
# Purpose:      Make asset repositories easier to maintain and refactor
# Home:         https://github.com/kbrafford/PyEmbeddedAssetManager
#----------------------------------------------------------------------------

__version__ = "2.0"
__author__  = "github.com/kbrafford"
__date__    = "3 Mar 2019"

import zipfile
import sys
if sys.version_info[0] == 2:
    PYVER = 2
    from cStringIO import StringIO
else:
    PYVER = 3
    from io import BytesIO

import base64
import os

ArtManager = None

def GetArtManager():
    global ArtManager
    if ArtManager == None:
        ArtManager = _ArtManager()
    return ArtManager

class _ArtManager(object):
    def __init__(self, archive = MY_ARCHIVE, root=""):
        data = base64.b64decode(bytes(archive.encode()))
        self.zipfile = None
        self.assetusagelist = set([])
        if archive:
            if PYVER == 3:
                self.zipfile = zipfile.ZipFile(BytesIO(data),"r")
            else:
                self.zipfile = zipfile.ZipFile(StringIO(data),"r")
            self.assetusagelist = set(self.GetAssetList())
        self.root = root
        self.imagecache, self.bitmapcache, self.iconcache = {},{},{}
    def SetRoot(self, root):
        self.root = root
    def GetImage(self, filename):
        import wx        
        filename = os.path.join(self.root,filename)
        self.assetusagelist.discard(filename)
        if self.imagecache.has_key(filename):
            return self.imagecache[filename]
        bitmapfile = self.zipfile.open(filename)
        if PYVER == 3:
            image = wx.ImageFromStream(BytesIO(bitmapfile.read()))
        else:
            image = wx.ImageFromStream(StringIO(bitmapfile.read()))
        self.imagecache[filename] = image
        return image
    def GetBitmap(self, filename):
        import wx        
        filename = os.path.join(self.root,filename)
        self.assetusagelist.discard(filename)
        if self.bitmapcache.has_key(filename):
            return self.bitmapcache[filename]
        bitmapfile = self.zipfile.open(filename)
        if PYVER == 3:
            image = wx.ImageFromStream(BytesIO(bitmapfile.read()))
        else:
            image = wx.ImageFromStream(StringIO(bitmapfile.read()))
        bitmap = image.ConvertToBitmap()
        self.bitmapcache[filename] = bitmap
        return bitmap
    def GetIcon(self, filename):
        import wx
        filename = os.path.join(self.root,filename)
        self.assetusagelist.discard(filename)
        if self.iconcache.has_key(filename):
            return self.iconcache[filename]
        bitmapfile = self.zipfile.open(filename)
        if PYVER == 3:
            image = wx.ImageFromStream(BytesIO(bitmapfile.read()))
        else:
            image = wx.ImageFromStream(StringIO(bitmapfile.read()))
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(image))
        self.iconcache[filename] = icon
        return icon
    def GetAssetList(self):
        return self.zipfile.namelist() if self.zipfile else []
    def GetNamedContents(self, name):
        filename = os.path.join(self.root,name)
        self.assetusagelist.discard(filename)
        fp = self.zipfile.open(filename)
        contents = fp.read()
        if PYVER == 3:
            contents = contents.decode()
        return contents
    def GetLicense(self,lic_fname="License.txt"):
        return self.GetNamedContents(lic_fname)
    def GetUnusedAssetList(self):
        """returns a set of assets that were not used so far in this session.
        useful for people to find assets that don't spark joy any more."""
        return self.assetusagelist

if __name__ == "__main__":
    import wx
    import tempfile
    import textwrap
    import shutil

    class InMemoryZip(object):
        """InMemoryZip class, courtesy of this stack overflow article:
   http://stackoverflow.com/questions/2463770/python-in-memory-zip-library"""
        def __init__(self):
            # Create the in-memory file-like object
            if PYVER == 3:
                self.in_memory_zip = BytesIO()
            else:
                self.in_memory_zip = StringIO()

        def append(self, filename_in_zip, file_contents):
            '''Appends a file with name filename_in_zip and contents of
               file_contents to the in-memory zip.'''
            # Get a handle to the in-memory zip in append mode
            zf = zipfile.ZipFile(self.in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)
            # Write the file to the in-memory zip
            if PYVER == 3:
                zf.writestr(filename_in_zip, BytesIO(file_contents).getvalue())
            else:                
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
        b64data = base64.b64encode(zipfiledata)
        b64lines = textwrap.wrap(b64data.decode(), 80)
        b64lines = ['    "%s"\n' % str(line) for line in b64lines]
        if len(b64lines) > 0:
            new_archive = ["MY_ARCHIVE = (\n"]
            new_archive.extend(b64lines)
            new_archive.append("            )\n\n")
        else:
            new_archive = ['MY_ARCHIVE = ""\n']
        return new_archive

    def ProcessModule(new_archive, filename, template):
        with open(template, "r") as f:
            while True:
                line = f.readline()
                if line.startswith("#<---"):
                    keeper = [line]
                    keeper.extend(f.readlines())
                    break
        if not filename.endswith(".py"): filename += ".py"
        f = open(filename, "w")
        f.writelines(new_archive)
        f.writelines(keeper)
        f.close()

    class MyDialog(wx.Dialog):
        def __init__(self, *args, **kwds):
            self.artman = kwds.pop("artman", None)
            if self.artman == None:
                wx.MessageBox("No Asset Manager specified", "Error", wx.OK)
                self.EndModal(-1)
                return

            kwds["pos"] = (5,5)

            # begin wxGlade: MyDialog.__init__
            kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
            wx.Dialog.__init__(self, *args, **kwds)
            self.button_explore = wx.Button(self, wx.ID_ANY, "Extract and Explore")
            self.button_encode = wx.Button(self, wx.ID_ANY, "Encode and Repack")
            self.button_export = wx.Button(self, wx.ID_ANY, "Export New Module")
            self.button_delete = wx.Button(self, wx.ID_ANY, "Delete Temp Files (No Reencode)")

            self.__set_properties()
            self.__do_layout()
            # end wxGlade

            self.button_explore.Bind(wx.EVT_BUTTON, self.OnExplore)
            self.button_encode.Bind(wx.EVT_BUTTON, self.OnEncode)
            self.button_export.Bind(wx.EVT_BUTTON, self.OnExport)
            self.button_delete.Bind(wx.EVT_BUTTON, self.OnDelete)

            self.button_encode.Enable(False)
            self.button_delete.Enable(False)
            self.button_export.Enable(False)

            self.Bind(wx.EVT_CLOSE, self.OnClose)

            #self.SetSizer(self.mainsizer)
            #self.width, h = self.mainsizer.CalcMin()
            #w,h = self.mainsizer.CalcMin()
            #self.SetSize((self.width, h+30))

        def __set_properties(self):
            # begin wxGlade: MyDialog.__set_properties
            self.SetTitle("Asset Manager")
            self.button_explore.SetDefault()
            # end wxGlade

            self.SetTitle("Asset Manager - %s" % sys.argv[0])

        def __do_layout(self):
            # begin wxGlade: MyDialog.__do_layout
            mainsizer = wx.BoxSizer(wx.HORIZONTAL)
            vsizer = wx.BoxSizer(wx.VERTICAL)
            mainsizer.Add(self.button_explore, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
            static_line_1 = wx.StaticLine(self, wx.ID_ANY, style=wx.LI_VERTICAL)
            mainsizer.Add(static_line_1, 0, wx.ALL | wx.EXPAND, 5)
            vsizer.Add(self.button_encode, 0, wx.ALL, 5)
            vsizer.Add(self.button_export, 0, wx.ALL, 5)
            mainsizer.Add(vsizer, 0, 0, 0)
            static_line_2 = wx.StaticLine(self, wx.ID_ANY, style=wx.LI_VERTICAL)
            mainsizer.Add(static_line_2, 0, wx.ALL | wx.EXPAND, 5)
            mainsizer.Add(self.button_delete, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
            self.SetSizer(mainsizer)
            mainsizer.Fit(self)
            self.Layout()
            # end wxGlade

        def OnClose(self, event):
            self.EndModal(0)

        def OnDelete(self, event):
            self.button_delete.Enable(False)
            self.button_encode.Enable(False)
            wx.CallAfter(self.PerformDelete)

        def PerformDelete(self):
            while DeleteTempFiles(self.tempdir) == False:
                wx.MessageBox("Can not delete the temp files.  You may need to close the app","Error", wx.OK)
            self.Close()

        def OnExport(self, event):
            import os
            dlg = wx.FileDialog(self, "Export New Module", os.getcwd(), "", "*.py", wx.FD_SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                new_archive = BundleArchive(self.tempdir)
                filename = dlg.GetPath()
                ourfile = sys.argv[0]
                self.button_delete.Enable(False)
                self.button_encode.Enable(False)
                ProcessModule(new_archive, filename, ourfile)
                self.PerformDelete()

        def OnEncode(self, event):
            self.button_delete.Enable(False)
            self.button_encode.Enable(False)
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
            if os.path.split(sys.argv[0])[1] not in ("PyEmbeddedAssetManager.py", "PyEmbeddedAssetManager.pyw"):
                self.button_encode.Enable(True)
            self.button_delete.Enable(True)
            self.button_export.Enable(True)
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
            elif "linux" in sys.platform:
                exe = "xdg-open"
            else:
                raise NotImplementedError("Not implemented for %s" % sys.platform)

            import subprocess
            subprocess.call([exe, "%s" % self.tempdir])

    a = wx.App()
    artman = GetArtManager()

    dlg = MyDialog(None, artman = artman)
    dlg.ShowModal()
    dlg.Destroy()

    a.MainLoop()
