import re

youtube_pattern = re.compile('&lt;iframe(.*?)src="http://www\.youtube\.com/embed/(.*?)&gt;&lt;/iframe&gt;')
inline_math_pattern = re.compile('\$(.*?)\$')

def postprocess(html):
    tmp = re.sub(youtube_pattern,'<iframe \g<1> src="http://www.youtube.com/embed/\g<2>></iframe>',html)
    tmp = re.sub(inline_math_pattern,'\\(\g<1>\\)',tmp)
    return tmp
