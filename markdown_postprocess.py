import re

youtube_pattern = re.compile('&lt;iframe(.*?)src="http://www\.youtube\.com/embed/(.*?)&gt;&lt;/iframe&gt;')

def postprocess(html):
    return re.sub(youtube_pattern,'<iframe \g<1> src="http://www.youtube.com/embed/\g<2>></iframe>',html)
