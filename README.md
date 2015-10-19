# PyEmbeddedAssetManager
Makes it easy to maintain and use embedded assets in a python program

##TODO: 

1. Add a proper description and tutorial explaining how to use the tool
2. Refactoring plan:
  * Support output of images as Numpy arrays
  * Rearrange so that wx isn't required unless necessary (for instance)
    if the user is using for non-image assets
  * Add cmd-line args for build script automation.  I'll add more details
    later for why someone might want this

##**Quick intro for the time being**

The PyEmbeddedAssetManager is a self-modifying python script that acts
as a container for whatever stream archives (read: files) you may want to
have embedded in your Python program.  

If you are deploying your Python application with Py2exe, PyInstaller, or
a similar distribution scheme then instead of having to expose your embedded
files (icons, bitmaps, text files) on the user file system these assets are
actually a part of your application, accessed at runtime.

PyEmbeddedAssetManager provides several methods for accessing your "files"
at runtime, including several that automatically provide conversion to
wx.Python graphics types.  Icons, Bitmaps, and Images are currently supported.

##BUT WAIT, THERE'S MORE!

The real strength of the PyEmbeddedAssetManager is the built-in management 
scheme.  Though designed for you to import and use in other applications,
a PyEmbeddedAssetManager module will self-execute as well.  If you run one
of these modules in this fashion, then you get a very simple wx GUI that will
let you:

1) extract your archive of assets into a folder you can browse
2) modify the repository (add, delete, modify, admire, whatever)
3) repack the repo into a new PyEmbeddedAssetManager module

That's all for now.  I hope to do a proper write-up in a bit.


