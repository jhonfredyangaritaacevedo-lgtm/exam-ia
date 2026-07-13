from io import BytesIO
import html
from typing import Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.flowables import Flowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from models.exam import Exam


class CircleLetter(Flowable):
    """Custom flowable para dibujar círculos con letras"""

    def __init__(self, letter, size=12):
        Flowable.__init__(self)
        self.letter = letter
        self.size = size
        self.width = size
        self.height = size

    def draw(self):
        c = self.canv
        c.setFillColor(colors.white)
        c.circle(self.size / 2, self.size / 2, self.size / 2, fill=1, stroke=1)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", self.size * 0.6)
        text_width = c.stringWidth(self.letter, "Helvetica-Bold", self.size * 0.6)
        c.drawString((self.size - text_width) / 2, (self.size * 0.3), self.letter)


class LineFlowable(Flowable):
    """Custom flowable para dibujar líneas de respuesta"""

    def __init__(self, width, spacing_mm=7):
        Flowable.__init__(self)
        self.width = width
        self.spacing = spacing_mm * mm
        self.height = self.spacing

    def draw(self):
        c = self.canv
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.5)
        c.line(0, self.spacing * 0.3, self.width, self.spacing * 0.3)


class PDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='ExamTitle',
            parent=self.styles['Title'],
            fontSize=16,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50')
        ))
        self.styles.add(ParagraphStyle(
            name='QuestionText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            spaceBefore=4,
            fontName='Helvetica-Bold'
        ))
        self.styles.add(ParagraphStyle(
            name='OptionText',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            leftIndent=0
        ))
        self.styles.add(ParagraphStyle(
            name='ExplanationText',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=8,
            spaceBefore=4,
            backColor=colors.HexColor('#fff3cd'),
            borderColor=colors.HexColor('#ffeaa7'),
            borderWidth=1,
            borderPadding=6,
            textColor=colors.HexColor('#856404')
        ))
        self.styles.add(ParagraphStyle(
            name='StudentInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4
        ))
        self.styles.add(ParagraphStyle(
            name='Instructions',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#495057'),
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0
        ))
        self.styles.add(ParagraphStyle(
            name='QuestionCount',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceBefore=5,
            spaceAfter=5
        ))

    def generate_exam_pdf(self, exam: Exam, include_solutions: bool = False) -> bytes:
        if not exam.result:
            raise ValueError("Exam has no content to generate PDF")

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )

        story = []

        story.append(Paragraph(html.escape(exam.title), self.styles['ExamTitle']))
        story.append(Paragraph(
            f"<i>{exam.area} · Grado {exam.grado}° · {exam.num_questions} preguntas</i>",
            self.styles['QuestionCount']
        ))
        story.append(Spacer(1, 15))

        if not include_solutions:
            story.extend(self._create_student_info_section())
            story.append(Spacer(1, 20))

        instructions_text = exam.result.get('instructions', 'Lee cuidadosamente cada pregunta y selecciona la respuesta correcta.')
        story.extend(self._create_instructions_section(instructions_text))
        story.append(Spacer(1, 15))

        questions = exam.result.get('questions', [])
        for i, question in enumerate(questions, 1):
            story.extend(self._generate_question_content(question, i, include_solutions))
            story.append(Spacer(1, 15))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _create_student_info_section(self) -> list:
        story = []

        name_para = Paragraph("<b>Nombre:</b> " + "_" * 60, self.styles['StudentInfo'])
        name_table = Table([[name_para]], colWidths=[6.5 * inch])
        name_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(name_table)
        story.append(Spacer(1, 3 * mm))

        date_para = Paragraph("<b>Fecha:</b> " + "_" * 18, self.styles['StudentInfo'])
        course_para = Paragraph("<b>Curso:</b> " + "_" * 18, self.styles['StudentInfo'])
        empty_para = Paragraph("", self.styles['StudentInfo'])

        date_course_table = Table([[date_para, course_para, empty_para]], colWidths=[2.1 * inch, 2.1 * inch, 2.3 * inch])
        date_course_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(date_course_table)
        return story

    def _create_instructions_section(self, text: str) -> list:
        instructions_para = Paragraph(
            f"<b>Instrucciones:</b><br/>{html.escape(text)}",
            self.styles['Instructions']
        )
        instructions_table = Table([[instructions_para]], colWidths=[6.5 * inch])
        instructions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        return [instructions_table]

    def _generate_question_content(self, question: Dict[str, Any], question_num: int, include_solutions: bool) -> list:
        story = []

        question_text = html.escape(question.get('stem', ''))
        question_type = question.get('type', 'multiple_choice')
        type_label = self._get_question_type_label(question_type)

        story.append(Paragraph(
            f"<b>{question_num}.</b> {question_text} <i>({type_label})</i>",
            self.styles['QuestionText']
        ))

        if question_type in ('multiple_choice', 'true_false'):
            story.extend(self._generate_options_content(question, include_solutions, question_type))
        else:
            story.extend(self._generate_open_answer_content(question, include_solutions, question_type == 'essay'))

        if include_solutions and question.get('justification'):
            story.append(Spacer(1, 8))
            story.append(Paragraph(
                f"<b>Justificación:</b> {html.escape(question['justification'])}",
                self.styles['ExplanationText']
            ))

        return story

    def _generate_options_content(self, question: Dict[str, Any], include_solutions: bool, question_type: str) -> list:
        story = []
        options = question.get('options', []) or []

        for i, opt in enumerate(options):
            text = opt.get('text', '')
            is_correct = bool(opt.get('correct'))
            if question_type == 'true_false':
                letter = 'V' if text.lower().startswith('v') else 'F'
            else:
                letter = chr(65 + i)

            if include_solutions:
                option_text = f"<b>{letter})</b> {html.escape(text)}"
                if is_correct:
                    option_text += " ✓"
                    style = ParagraphStyle(
                        'CorrectOption',
                        parent=self.styles['OptionText'],
                        backColor=colors.HexColor('#d4edda'),
                        textColor=colors.HexColor('#155724'),
                        borderColor=colors.HexColor('#28a745'),
                        borderWidth=1,
                        borderPadding=4
                    )
                else:
                    style = self.styles['OptionText']
                story.append(Paragraph(option_text, style))
            else:
                option_text_para = Paragraph(html.escape(text), self.styles['OptionText'])
                option_table = Table([[CircleLetter(letter), option_text_para]], colWidths=[25, 6 * inch])
                option_table.setStyle(TableStyle([
                    ('FONTNAME', (1, 0), (1, 0), 'Helvetica'),
                    ('FONTSIZE', (1, 0), (1, 0), 9),
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                option_table.hAlign = 'LEFT'
                story.append(option_table)

        return story

    def _generate_open_answer_content(self, question: Dict[str, Any], include_solutions: bool, is_essay: bool) -> list:
        story = []

        if include_solutions:
            expected = html.escape(question.get('expected_answer', ''))
            answer_para = Paragraph(f"<b>R:</b> {expected}", self.styles['Normal'])
            answer_table = Table([[answer_para]], colWidths=[6 * inch])
            answer_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#28a745')),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(answer_table)
        else:
            num_lines = 7 if is_essay else 3
            for _ in range(num_lines):
                story.append(LineFlowable(6.5 * inch, spacing_mm=7))

        return story

    def _get_question_type_label(self, question_type: str) -> str:
        type_labels = {
            'multiple_choice': 'Selección múltiple',
            'true_false': 'Falso/Verdadero',
            'short_answer': 'Respuesta corta',
            'essay': 'Ensayo'
        }
        return type_labels.get(question_type, 'Pregunta')


pdf_service = PDFService()
