# PyEmbeddedAssetManager
Makes it easy to maintain and use embedded assets in a python program

#**Quick intro for the time being**

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

#BUT WAIT, THERE'S MORE!

The real strength of the PyEmbeddedAssetManager is the built-in management 
scheme.  Though designed for you to import and use in other applications,
a PyEmbeddedAssetManager module will self-execute as well.  If you run one
of these modules in this fashion, then you get a very simple wx GUI that will
let you:

1. extract your archive of assets into a folder you can browse
2. modify the repository (add, delete, modify, admire, whatever)
3. repack the repo into a new PyEmbeddedAssetManager module

Here is a shot of an Embedded Asset Manager being edited:

![PyEmbeddedAssetManager screen](/tutorial/image_1.png)

Press "Extract and Explore" to view the contents:

![Browsing an empty asset manager](/tutorial/image_2.png)

Add your artwork or other files to your Asset Manager.  You
can also create directories.  Go wild!  Here's a simple example,
using some of my favorite free icons, the Silk set:

![Adding files to the Asset Manager](/tutorial/image_3.png)

Once you've added your assets to the folder, you can press
"Export New Module" and create a new Asset Manager...

![Exporting a new module](/tutorial/image_4.png)

...Complete with your assets and a self-contained ability to edit
the repository:

![New python module](/tutorial/image_5.png)

And when you "run" your new repo in stand-alone mode, you can add
new content, remove files, edit files in place...whatever.  Just
re-encode when you're done.

![Finished repo](/tutorial/image_6.png)


#TODO: 
0. More fully test on Python 2 and 3, fully testing all the wx outputs

1. Add a proper description and tutorial explaining how to use the tool.
   Included will be examples showing how the programmer importing the module
   actually uses it. Update the tutorial too to reflect the new look.

2. Refactoring plan:
  * Support output of images as Numpy arrays
  * direct support of PIL image type?
  * Add cmd-line args for build script automation.  I'll add more details
    later for why someone might want this


