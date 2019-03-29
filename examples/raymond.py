from __future__ import print_function
from jinja2 import Template
from raymond_assets import GetArtManager

artman = GetArtManager()

TITLE = "Raymond's Web Page!"
CONTENT = """This is the content for Raymond's web page!"""

# Let's print out the names of all the assets in the bundle
print("Asset bundle contents:\n%s\n" % artman.GetAssetList())

# Let's fetch the template from the asset bundle
tm_text = artman.GetNamedContents("raymond.html")
print("Template contents:\n%s\n" % tm_text)

# Let's make our jinja2 template from our source
template = Template(tm_text)

# Now let's render the template using our content
print("Final product:")
print(template.render(title=TITLE, body=CONTENT))


