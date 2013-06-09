import re
from markdown import markdown

youtube_pattern = re.compile('&lt;iframe(.*?)src="http://www\.youtube\.com/embed/(.*?)&gt;&lt;/iframe&gt;')
inline_math_pattern = re.compile('\$(.*?)\$')
math_pattern = re.compile('\$\$(.*?)\$\$')

def postprocess(html):
    tmp = re.sub(math_pattern,'\\[\g<1>\\]',html)
    tmp = re.sub(inline_math_pattern,'\\(\g<1>\\)',tmp)
    # this is only needed in escape safety mode
    #tmp = re.sub(youtube_pattern,'<iframe \g<1> src="http://www.youtube.com/embed/\g<2>></iframe>',tmp)
    return tmp

def mymarkdown(text):
    formatted_text = markdown(text)   #,safe_mode='escape')
    formatted_text = postprocess(formatted_text)
    return formatted_text
