from markdown import markdown
from markdown_postprocess import postprocess

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
