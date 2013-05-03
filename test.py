from markdown import markdown
from markdown_postprocess import postprocess
import re

html = markdown("""
Hello!
-----

world

$E=mc^2>0$

$$E=mc^2>0$$

<iframe width="560" height="315" src="http://www.youtube.com/embed/zA92Rw6kNWw" frameborder="0" allowfullscreen></iframe>
<script type="text/javascript" src="/jquery/js/jquery-ui-1.9.2.custom.min.js"></script>

""",safe_mode='escape')

print postprocess(html)

text = """
Image ![iii][im1]
[im1]: /img?key=ahFkZXZ-aGVsbG9wZGZ3b3JsZHILCxIFSW1hZ2UYLgw
aaa
"""

image_link_pattern = re.compile('!\[.*?\]\[(.+?)\]')
id_pattern_template = '\n\[%s\]:.+'
pattern = id_pattern_template % 'im1'

print pattern

mo = re.search(pattern,text)
print mo.groups()
out = re.sub(pattern,'\n+++', text)
print text
print out
