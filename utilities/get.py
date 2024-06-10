import os
from sys import platform
from flask import render_template, make_response, url_for
from flask_login import current_user
from core.database import db_session
from core.models import Test, TestAnswer, Question, QuestionOption
from . import convert
import pdfkit
import base64
from PIL import Image, ImageDraw, ImageFont
from time import time


def file_extension(filename):
    return os.path.splitext(filename)[1]


def practiceDetails(practice_id):
    if current_user and practice_id:
        practiceModel = db_session.query(TestAnswer).filter_by(user_id=current_user.id, id=practice_id).first()
        testModel     = db_session.query(Test).filter_by(id=practiceModel.test_id).first()
        

        passingPercentage   = 60
        # payload             = practiceModel.getPayload()

        percentGain = round((practiceModel.marks_obtain * 100 / practiceModel.total_marks), 2)
        subject = testModel.getSubject()

        
        practiceData = {
            'statics' : {
                'user_name'         : current_user.fullName,
                'test_id'           : testModel.id,
                'test_name'         : testModel.name,
                'subject_name'      : subject['name'],
                # 'subject_logo'      : subject['logo'],
                'subject_id'        : subject['id'],
                'subject_logo'      : url_for('static', filename='img/logos/'+subject['logo']),
                'marks_obtain'      : practiceModel.marks_obtain,
                'total_marks'       : practiceModel.total_marks,
                'percentage'        : percentGain,
                'question_attend'   : practiceModel.question_attend,
                'total_question'    : practiceModel.total_question,
                'time_taken'        : convert.secondsToTime(practiceModel.time_taken),
                'created_at'        : practiceModel.created_at.strftime("%d / %m / %Y"),
                'result'            : "PASS" if percentGain >=  passingPercentage else "FAILED",
                'certificate'       : practiceModel.certificate
            }
            # 'qna' : []
        }

        
        # for question_id, obj in payload['qna'].items():

        #     questionModel   = db_session.query(Question).filter_by(id=question_id).first()
        #     optionModels    = db_session.query(QuestionOption).filter_by(question_id=question_id).all()
            
        #     right_answer = False
        #     for i in optionModels:
        #         if i.is_correct:
        #             right_answer = i.id
        #             break

        #     optionData = {
        #         'params'        : {
        #             'selected_answer'   : int(obj['option_id']),
        #             'right_answer'      : int(right_answer)
        #         },
        #         'option-list'   : []
        #     }
        #     for option in optionModels:
        #         optionData['option-list'].append({
        #             'option_id' : option.id,
        #             # 'option'    : option.option,
        #             'is_correct': option.is_correct
        #         })
            
        #     practiceData['qna'].append({
        #         'question_id'   : questionModel.id,
        #         # 'question'      : questionModel.question,
        #         'options'       : optionData
        #     })
        
    
        return practiceData




def certificate(params):

    # return image from files if already generated
    if params['certificate']:
        return {
                'status'    : True,
                'image_name': params['certificate'],
                'image'     : Image.open(f"static/files/certificates/{params['certificate']}")
            }


    image   = Image.open('templates/certificates/certificate-template.jpg')
    draw    = ImageDraw.Draw(image)
    color   = [0,0,0]

    if platform == "linux" or platform == "linux2":
        font_name = "Arial.ttf"
    elif platform == "darwin":
        font_name = "Arial.ttf"
    elif platform == "win32" or platform == "cygwin":
        font_name = "arial.ttf"
    textList = [
        {
            'box_coordinates': [0, 0],
            'text': params['user_name'],
            'font_name': font_name,
            'font_size': 100,
            'font_color': color
        },
        {
            'box_coordinates': [0, -300],
            'text': f"has completed \"{params['test_name']}\" test",
            'font_name': font_name,
            'font_size': 80,
            'font_color': color
        },
        {
            'box_coordinates': [0, -500],
            'text': f"on Date: {params['created_at']}",
            'font_name': font_name,
            'font_size': 80,
            'font_color': color
        },
        {
            'box_coordinates': [0, -800],
            'text': f"The Topic consists of Questions related to {params['subject_name']}",
            'font_name': font_name,
            'font_size': 55,
            'font_color': color
        },
        {
            'box_coordinates': [0, -1000],
            'text': f"Successfully secured {params['percentage']}% and {params['result']} the test.",
            'font_name': font_name,
            'font_size': 55,
            'font_color': color
        }
    ]
    try:
        for i in textList:
            text        = i['text']
            font        = ImageFont.truetype(i['font_name'], i['font_size'])
            _, _, w, h  = draw.textbbox(tuple(i['box_coordinates']), text, font=font)
            xy          = ((2800-w)/2, (1200-h)/2)
            draw.text(xy=xy, text=text, fill=tuple(i['font_color']), font=font)

        image_name = f"{current_user.id}_{params['subject_id']}_{params['test_id']}_{int(time())}.jpg"
        image.save(f"static/files/certificates/{image_name}")
        
        return {
            'status'    : True,
            'image_name': image_name,
            'image'     : image
        }

    except:
        return False




# def certificate(params):
#     if platform == "linux" or platform == "linux2":
#         config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
#     elif platform == "darwin":
#         config = pdfkit.configuration(wkhtmltopdf=r"/usr/local/bin/wkhtmltopdf")
#     elif platform == "win32" or platform == "cygwin":
#         config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")


#     options = {
#         'page-size'     : 'A4',
#         'margin-top'    : '0.0in',
#         'margin-right'  : '0.0in',
#         'margin-bottom' : '0.0in',
#         'margin-left'   : '0.0in',
#         'orientation'   : 'landscape',
#         'encoding'      : 'UTF-8'
#     }

#     rendered = render_template(r"certificates/test-certificate.html", params=params)
#     # rendered = render_template("certificates/test-certificate.html")
#     # rendered = html
#     # pdf = pdfkit.from_file(
#     #     input = "templates/certificates/test-certificate.html",
#     #     configuration = config,
#     #     options=options
#     # )
#     pdf = pdfkit.from_string(
#         input=rendered,
#         options=options,
#         configuration=config
#     )

#     return pdf

#     # pdf.save(os.path.join(APP_ROOT, r'static/files/certificates', secure_filename('output.pdf')))
#     # with open(os.path.join(r'static\files\certificates', secure_filename('output.pdf')), 'wb') as f:
#     #     f.write(pdf)
    
#     # response = make_response(pdf)
#     # response.headers['Content-Type'] = 'application/pdf'
#     # response.headers['Content-Disposition'] = 'inline; filename=output.pdf'

#     # return response



    