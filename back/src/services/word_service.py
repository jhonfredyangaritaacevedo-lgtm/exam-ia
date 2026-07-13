from io import BytesIO
from typing import Dict, Any

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml

from models.exam import Exam


class WordService:
    """Service to generate Word documents for exams, matching the PDF design."""

    CONTENT_WIDTH_CM = 17.18

    def generate_exam_word(self, exam: Exam, include_solutions: bool = False) -> bytes:
        if not exam.result:
            raise ValueError("Exam has no content to generate Word document")

        doc = Document()

        style = doc.styles['Normal']
        style.font.size = Pt(9)
        style.paragraph_format.space_before = Pt(0)
        style.paragraph_format.space_after = Pt(0)

        for section in doc.sections:
            section.top_margin = Cm(1.91)
            section.bottom_margin = Cm(1.91)
            section.left_margin = Cm(1.91)
            section.right_margin = Cm(1.91)

        title_para = doc.add_paragraph()
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_para.paragraph_format.space_after = Pt(2)
        title_run = title_para.add_run(exam.title)
        title_run.bold = True
        title_run.font.size = Pt(14)
        title_run.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)

        count_para = doc.add_paragraph()
        count_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        count_para.paragraph_format.space_after = Pt(8)
        count_run = count_para.add_run(f"{exam.area} · Grado {exam.grado}° · {exam.num_questions} preguntas")
        count_run.italic = True
        count_run.font.size = Pt(9)
        count_run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

        if not include_solutions:
            self._add_student_info_section(doc)

        instructions_text = exam.result.get(
            'instructions',
            'Lee cuidadosamente cada pregunta y selecciona la respuesta correcta.'
        )
        self._add_instructions_section(doc, instructions_text)

        questions = exam.result.get('questions', [])
        for i, question in enumerate(questions, 1):
            self._add_question(doc, question, i, include_solutions)

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    def _add_student_info_section(self, doc: Document):
        name_para = doc.add_paragraph()
        name_para.paragraph_format.space_after = Pt(4)
        name_run = name_para.add_run("Nombre: ")
        name_run.bold = True
        name_run.font.size = Pt(10)
        name_para.add_run("_" * 60).font.size = Pt(10)

        table = doc.add_table(rows=1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.LEFT

        cell_date = table.cell(0, 0)
        p = cell_date.paragraphs[0]
        run = p.add_run("Fecha: ")
        run.bold = True
        run.font.size = Pt(10)
        p.add_run("_" * 18).font.size = Pt(10)

        cell_course = table.cell(0, 1)
        p = cell_course.paragraphs[0]
        run = p.add_run("Curso: ")
        run.bold = True
        run.font.size = Pt(10)
        p.add_run("_" * 18).font.size = Pt(10)

        self._remove_table_borders(table)

        spacer = doc.add_paragraph()
        spacer.paragraph_format.space_after = Pt(6)

    def _add_instructions_section(self, doc: Document, text: str):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.LEFT
        table.columns[0].width = Cm(self.CONTENT_WIDTH_CM)

        cell = table.cell(0, 0)
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="f8f9fa"/>')
        cell._tc.get_or_add_tcPr().append(shading)

        p = cell.paragraphs[0]
        run = p.add_run("Instrucciones: ")
        run.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x49, 0x50, 0x57)
        run2 = p.add_run(text)
        run2.font.size = Pt(9)
        run2.font.color.rgb = RGBColor(0x49, 0x50, 0x57)

        self._set_cell_padding(cell, top=120, bottom=120, left=160, right=160)
        self._set_table_border(table, color="dee2e6")

        spacer = doc.add_paragraph()
        spacer.paragraph_format.space_after = Pt(6)

    def _add_question(self, doc: Document, question: Dict[str, Any], num: int, include_solutions: bool):
        question_text = question.get('stem', '')
        question_type = question.get('type', 'multiple_choice')
        type_label = self._get_question_type_label(question_type)

        q_para = doc.add_paragraph()
        q_para.paragraph_format.space_before = Pt(6)
        q_para.paragraph_format.space_after = Pt(3)
        num_run = q_para.add_run(f"{num}. ")
        num_run.bold = True
        num_run.font.size = Pt(10)
        text_run = q_para.add_run(question_text)
        text_run.bold = True
        text_run.font.size = Pt(10)
        type_run = q_para.add_run(f" ({type_label})")
        type_run.italic = True
        type_run.font.size = Pt(8)
        type_run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

        if question_type in ('multiple_choice', 'true_false'):
            self._add_options(doc, question, include_solutions, question_type)
        else:
            self._add_open_answer(doc, question, include_solutions, is_essay=(question_type == 'essay'))

        if include_solutions and question.get('justification'):
            self._add_justification(doc, question['justification'])

    def _add_options(self, doc: Document, question: Dict[str, Any], include_solutions: bool, question_type: str):
        options = question.get('options', []) or []

        for i, opt in enumerate(options):
            text = opt.get('text', '')
            is_correct = bool(opt.get('correct'))
            if question_type == 'true_false':
                letter = 'V' if text.lower().startswith('v') else 'F'
            else:
                letter = chr(65 + i)

            if include_solutions:
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(1)
                run = p.add_run(f"{letter}) ")
                run.bold = True
                run.font.size = Pt(9)
                text_run = p.add_run(text)
                text_run.font.size = Pt(9)

                if is_correct:
                    check_run = p.add_run(" ✓")
                    check_run.font.size = Pt(9)
                    self._set_paragraph_shading(p, "d4edda")
                    for r in p.runs:
                        r.font.color.rgb = RGBColor(0x15, 0x57, 0x24)
            else:
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(1)
                p.paragraph_format.left_indent = Pt(10)
                circle_run = p.add_run(f"  {letter}  ")
                circle_run.bold = True
                circle_run.font.size = Pt(9)
                self._add_circle_border(circle_run)
                text_run = p.add_run(f"  {text}")
                text_run.font.size = Pt(9)

    def _add_open_answer(self, doc: Document, question: Dict[str, Any], include_solutions: bool, is_essay: bool):
        if include_solutions:
            expected = question.get('expected_answer', '')
            table = doc.add_table(rows=1, cols=1)
            table.columns[0].width = Cm(self.CONTENT_WIDTH_CM)
            cell = table.cell(0, 0)
            shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="f8f9fa"/>')
            cell._tc.get_or_add_tcPr().append(shading)

            p = cell.paragraphs[0]
            run = p.add_run("R: ")
            run.bold = True
            run.font.size = Pt(9)
            p.add_run(expected).font.size = Pt(9)

            self._set_cell_padding(cell, top=100, bottom=100, left=120, right=120)
            self._set_table_border(table, color="28a745")
        else:
            num_lines = 5 if is_essay else 3
            table = doc.add_table(rows=num_lines, cols=1)
            table.columns[0].width = Cm(self.CONTENT_WIDTH_CM)

            for row_idx in range(num_lines):
                cell = table.cell(row_idx, 0)
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                tr = table.rows[row_idx]._tr
                trPr = tr.get_or_add_trPr()
                trHeight = parse_xml(f'<w:trHeight {nsdecls("w")} w:val="400" w:hRule="exact"/>')
                trPr.append(trHeight)

            tbl = table._tbl
            tblPr = tbl.tblPr if tbl.tblPr is not None else parse_xml(f'<w:tblPr {nsdecls("w")}/>')
            borders = parse_xml(
                f'<w:tblBorders {nsdecls("w")}>'
                f'  <w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
                f'  <w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
                f'  <w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
                f'  <w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
                f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
                f'  <w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
                f'</w:tblBorders>'
            )
            tblPr.append(borders)
            last_cell = table.cell(num_lines - 1, 0)
            tcPr = last_cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(
                f'<w:tcBorders {nsdecls("w")}>'
                f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
                f'</w:tcBorders>'
            )
            tcPr.append(tcBorders)

    def _add_justification(self, doc: Document, justification: str):
        table = doc.add_table(rows=1, cols=1)
        table.columns[0].width = Cm(self.CONTENT_WIDTH_CM)
        cell = table.cell(0, 0)

        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="fff3cd"/>')
        cell._tc.get_or_add_tcPr().append(shading)

        p = cell.paragraphs[0]
        run = p.add_run("Justificación: ")
        run.bold = True
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(0x85, 0x64, 0x04)
        text_run = p.add_run(justification)
        text_run.font.size = Pt(8)
        text_run.font.color.rgb = RGBColor(0x85, 0x64, 0x04)

        self._set_cell_padding(cell, top=80, bottom=80, left=120, right=120)
        self._set_table_border(table, color="ffeaa7")

    def _get_question_type_label(self, question_type: str) -> str:
        type_labels = {
            'multiple_choice': 'Selección múltiple',
            'true_false': 'Falso/Verdadero',
            'short_answer': 'Respuesta corta',
            'essay': 'Ensayo'
        }
        return type_labels.get(question_type, 'Pregunta')

    # --- Helper methods for Word XML manipulation ---

    def _remove_table_borders(self, table):
        tbl = table._tbl
        tblPr = tbl.tblPr if tbl.tblPr is not None else parse_xml(f'<w:tblPr {nsdecls("w")}/>')
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'  <w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
            f'  <w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
            f'  <w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
            f'  <w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
            f'  <w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
            f'  <w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
            f'</w:tblBorders>'
        )
        tblPr.append(borders)

    def _set_table_border(self, table, color: str = "000000"):
        tbl = table._tbl
        tblPr = tbl.tblPr if tbl.tblPr is not None else parse_xml(f'<w:tblPr {nsdecls("w")}/>')
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
            f'  <w:left w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
            f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
            f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
            f'</w:tblBorders>'
        )
        tblPr.append(borders)

    def _set_cell_padding(self, cell, top=0, bottom=0, left=0, right=0):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(
            f'<w:tcMar {nsdecls("w")}>'
            f'  <w:top w:w="{top}" w:type="dxa"/>'
            f'  <w:left w:w="{left}" w:type="dxa"/>'
            f'  <w:bottom w:w="{bottom}" w:type="dxa"/>'
            f'  <w:right w:w="{right}" w:type="dxa"/>'
            f'</w:tcMar>'
        )
        tcPr.append(tcMar)

    def _set_paragraph_shading(self, paragraph, color: str):
        pPr = paragraph._p.get_or_add_pPr()
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}" w:val="clear"/>')
        pPr.append(shading)

    def _add_circle_border(self, run):
        rPr = run._r.get_or_add_rPr()
        bdr = parse_xml(
            f'<w:bdr {nsdecls("w")} w:val="single" w:sz="4" w:space="1" w:color="000000"/>'
        )
        rPr.append(bdr)


word_service = WordService()
