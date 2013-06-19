import re
from markdown import markdown
from image import Image
from question import Question

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

def update_links(chapter, text):
    """Parse the new text and correct if needed.
    
    Consider input text to have Markdown format.
    - Image names in reference links need to have urls.
    """
    # find all image tags in form ![Alt text][image_name]
    # and interpret image_name as markdown reference id
    # so text must contain line [image_name]: /proper_image_url
    image_link_pattern = re.compile('!\[.*?\]\[(.+?)\]')
    id_pattern_template = '\n\[%s\]:.+'
    match_list = re.findall(image_link_pattern, text)
    refresh = chapter.refresh
    for id in match_list:
        pattern = id_pattern_template % id
        image = Image.get_image_by_name(chapter, id)
        if not re.search(pattern,text):  # there is no [id]: /url string
            if image:
                text += '\n['+id+']: '+'/img?key='+str(image.key())
        elif refresh: # refresh anyway
            if image:
                text = re.sub(pattern,'\n['+id+']: '+'/img?key='+str(image.key()),text)
            else:
                text = re.sub(pattern,'',text)
                
    return text
            
def markdown_questionlist(qlist):
    qlist.formatted_questions = []
    for q in qlist.questions:
        if isinstance(q,Question):
            question = q
        else:
            question = Question.get(q)
        if question:
            question.formatted_text = mymarkdown(question.text)
            qlist.formatted_questions.append(question)
    
def markdown_questionlists(qlists):
    for qlist in qlists:
        markdown_questionlist(qlist)
