from markdown import markdown
import re

pattern1 = re.compile('&lt;iframe(.*?)src="http://www\.youtube\.com/embed/(.*?)&gt;&lt;/iframe&gt;')

def postprocess(html):
    return re.sub(pattern1,'<iframe \g<1> src="http://www.youtube.com/embed/\g<2>></iframe>',html)

html = markdown("""
Hello!
-----

world

\(E=mc^2>0\)

<iframe width="560" height="315" src="http://www.youtube.com/embed/zA92Rw6kNWw" frameborder="0" allowfullscreen></iframe>
<script type="text/javascript" src="/jquery/js/jquery-ui-1.9.2.custom.min.js"></script>

""",safe_mode='escape')

mo = re.search('&lt;iframe(.*?)src="http://www\.youtube\.com/embed/(.*?)&gt;&lt;/iframe&gt;',html)
#mo = re.search('\$(.*)','$html')

print mo.group(1), mo.group(2)
print postprocess(html)
