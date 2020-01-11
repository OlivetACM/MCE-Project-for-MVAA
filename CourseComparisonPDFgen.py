from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas as cv
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from PIL import Image
PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
styles = getSampleStyleSheet()
import datetime

from tabula import wrapper

#for testing

from Course import Course
from Reviewer import Reviewer


class CourseComparisonPDFgen:


    def __init__(self, oc_course, jst_course, reviewer):#pulling information from course objects.
        self.instr_name = reviewer.name
        self.dep_name = reviewer.department
        self.m_course = jst_course.number
        self.oc_course = oc_course.number
        self.oc_description = oc_course.description
        self.mc_description = jst_course.description
        self.oc_course_name = oc_course.name
        self.mc_course_name = jst_course.name
        self.total_pages = 1
        self.story = [Spacer(1,inch*.5)]
        self.styles = getSampleStyleSheet()

    def page_numbers(self, canvas, doc):
        canvas.setFont('Times-Roman',12)
        canvas.drawCentredString(PAGE_WIDTH/2.0, inch-20, "Page %d of %d" % (doc.page, self.total_pages))

    #designed to set up the first page header
    def first_page_setup(self, canvas, doc):
        self.canvas = canvas
        style_normal = self.styles['Normal']
        title_paragraph = Paragraph("<para alignment='center'>Military Credit Equivalency Course Evaluation Form Olivet College (version 6.24.2019)</para>", style=style_normal)
        aw, ah = 250, 20
        w,h = title_paragraph.wrap(aw, ah)#used to wrap the paragraph
        oc_college_image = Image.open("OlivetCollegeLogo.jpg")#inserting the image so that it can be placed in the header of the form.
        canvas.saveState()
        canvas.setFont('Times-Roman',12)
        oc_college_image_location_x = (PAGE_WIDTH/2)-oc_college_image.size[0]*.25
        oc_college_image_location_y = PAGE_HEIGHT-(oc_college_image.size[1]+35)
        placed_image = canvas.drawInlineImage(oc_college_image,oc_college_image_location_x,oc_college_image_location_y, width=oc_college_image.size[0]*.5,height=oc_college_image.size[1]*.5)
        title_paragraph.drawOn(canvas, (PAGE_WIDTH/2)-title_paragraph.width/2, PAGE_HEIGHT-(title_paragraph.height+placed_image[1]+90))
        self.page_numbers(canvas, doc)#placing the page number at the bottom of the page
        canvas.restoreState()
    
    #this is responsible for the page number at the botom of every page after the first.
    def later_pages(self, canvas, doc):
        self.total_pages+=1
        canvas.saveState()
        self.page_numbers(canvas, doc)
        self.radio_button_placer(canvas)
        canvas.restoreState()
        

    def introduction(self):
        style = self.styles['BodyText']
        introduction_para = Paragraph(FormInformation.intro_paragraph, style=style)
        return_para = Paragraph(FormInformation.return_information, style=style)
        self.story.append(introduction_para)
        self.story.append(return_para)

    #creates the first table
    def header_table(self):
        self.story.append(Spacer(1,cm*.3))
        table_width = (self.doc.width/3)-5
        now = datetime.datetime.now()
        date_created = Paragraph(str(now.month) + "-" + str(now.day) + "-" + str(now.year), style=styles["Normal"])
        military_course =  Paragraph(self.m_course + " - " + self.mc_course_name + "\n" + self.mc_description, style=styles["BodyText"])
        evaluator_info = Paragraph('Evaluator Name:\n' + self.instr_name + '\nDepartment:\n' + self.dep_name, style=styles["BodyText"])
        data = [['Date of Initiation:', 'JST or AU course for which Credit/Equivalency is sought:',''],
                [date_created,military_course,''],
                [evaluator_info, 'Olivet College course being considered for possible equivalency:','']]
        t = Table(data, colWidths=table_width, style=[('BOX', (0, 0), (-1, -1), .25, colors.black),
                                                                ('LINEAFTER', (0,0), (0,-1), .25, colors.black),
                                                                ('LINEABOVE', (0,2), (-1,2), .25, colors.black),
                                                                ('VALIGN', (0,0),(-1,-1),'TOP'),#very important, alignes everything at the top of each cell.
                                                                ('SPAN', (1,1), (2,2)),
                                                                ('SPAN', (0,2), (0,-1))])

        self.story.append(t)

    def create_table(self, dr, dc):
        table = []
        for i in range(0,dc):
            table.append([])
        for y in range(0,len(table)):
            for i in range(0, dr):
                table[y].append('')
        return table

    def add_row_table(self, data):
        data.append([])
        for x in range(0,len(data[0])):
            data[-1].append('')
        return data, len(data)
            
    def outcome_comparison_table_header(self, oc_outcome):
        self.story.append(Spacer(1,cm*.3))
        equivalence_style = ParagraphStyle(name="Equivalence_Style")
        table_header_style = ParagraphStyle(name="Table_Header_Style")
        equivalence_style.fontSize = 8
        equivalence_style.alignment = 1
        table_header_style.alignment = 1
        rows, columns, self.offset = 11, 1, 1.36#3.88 at 14 rows, 5.13 at 12, 6.01 at 11 
        header_outcome = "<b>JST/AU Learning Outcome</b><br />" + oc_outcome
        table_header = Paragraph(header_outcome, style=table_header_style)
        no_match = Paragraph("No match<br />(0-33%)", style=equivalence_style)
        moderate_match = Paragraph("Moderate Match<br />(34-67%)", style=equivalence_style)
        strong_match = Paragraph("Strong<br />Match (68-100%)", style=equivalence_style)
        data = self.create_table(dr=rows,dc=columns)
        data[0][0] = table_header 
        data[0][-3] = no_match
        data[0][-2] = moderate_match
        data[0][-1] = strong_match
        table_style = TableStyle([('GRID', (0,0), (-1,-1), .25, colors.black),
                                ('VALIGN',(0,0),(-1,-1),'TOP'),
                                ('SPAN', (0,0), (-4, 0)),
                                ('SPAN', (0,1), (-4, 1))])
        return table_style, data
    
    def outcome_comparisons(self, jst_outcomes, oc_outcome):
        table_style, data = self.outcome_comparison_table_header(oc_outcome)
        
        for i in range(0,len(jst_outcomes)):
            data, count = self.add_row_table(data)
            data[count-1][0] = jst_outcomes[i]
            table_style.add('SPAN', (0,count-1), (-4, count-1))

        table = Table(data, colWidths=(self.doc.width/len(data[0]))-self.offset, style=table_style)
        self.story.append(table)

    def test(self):
        pass


    def document_create(self):
        self.doc = SimpleDocTemplate("MCE-TEMPLATE-6.24.2019-radio-restricted.pdf", pagesize=letter, rightMargin=50, leftMargin=50)
        self.introduction()
        self.header_table()
        self.outcome_comparisons(['test1', 'test2', 'test3', 'test4','whatisthis'], "temp oc_outcome")
        self.doc.build(self.story, onFirstPage=self.first_page_setup, onLaterPages=self.later_pages)

        for fram_pos in self.doc.pos_frames:
            print("fram pos is: ", fram_pos)
        for cell_pos in self.doc.cell_positions:
            print("cell pos: ", cell_pos)
        self.test()

    def radio_button_placer(self,c):
        form = c.acroForm
        form.radio(name='group1', tooltip='Apple',
               value='apple', selected=True,
               x=110, y=650, buttonStyle='check',
               borderStyle='solid', shape='square',
               borderColor=colors.blue, fillColor=colors.magenta, 
               textColor=colors.blue, forceBorder=True)
        form.radio(name='group1', tooltip='Banana',
               value='banana', selected=False,
               x=110, y=600, buttonStyle='check',
               borderStyle='solid', shape='square',
               borderColor=colors.blue, fillColor=colors.yellow, 
               textColor=colors.blue, forceBorder=True)
        form.radio(name='group1', tooltip='Orange',
               value='orange', selected=False,
               x=110, y=550, buttonStyle='check',
               borderStyle='solid', shape='square',
               borderColor=colors.blue, fillColor=colors.orange, 
               textColor=colors.blue, forceBorder=True)
        c.save()

        
        

class FormInformation:


    intro_paragraph = """<para alignment='justify'>Purpose: This form is for determination of course equivalency credit or general college credit 
    for military courses and trainings listed on the Joint Services Transcript (JST) or Air University (AU) transcript 
    of U.S. military active duty or veteran students at Olivet College (OC). Learning outcomes as identified on the JST 
    or AU and evaluated by the American Council on Education (ACE) will be compared to OC course learning outcomes and 
    assessed for alignment with OC course learning outcomes by the department chair(s) or designee(s). The department 
    chair or designee will then make an overall recommendation of credit equivalency to the assistant dean for academic 
    records for approval. Approved JST/AU equivalencies will be entered into the OC’s course equivalency database and 
    reported on the college’s website. Only OC courses at the 100/200 level should be evaluated for course equivalency; 
    OC courses at the 300/400 level require further approval by the dean of faculty.</para>"""

    return_information = """This form is to be returned to the assistant dean for academic records <u>within 7 days</u> of the date of its initiation."""

    

if __name__ == '__main__':
    database = 'db.sqlite3'
    course_pairs = ['PE 107', 'A-830-0030', 'Nick Juday']
    OC_Course = Course(database, course_pairs[0])
    JST_Course = Course(database, course_pairs[1])
    Reviewer = Reviewer(database, course_pairs[2])
    test_course_compare = CourseComparisonPDFgen(OC_Course, JST_Course, Reviewer)
    test_course_compare.document_create()




#print statments added to Tables.py
#also prints in doctemplate
#check out frames next










