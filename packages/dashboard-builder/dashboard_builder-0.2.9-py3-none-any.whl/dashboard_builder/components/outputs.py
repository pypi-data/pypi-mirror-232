# components/outputs.py

from flask import render_template_string
import io
import base64
import json
from markdown import markdown
from ..utils import get_jinja_subtemplate

class OutputText:
    def __init__(self, content):
        self.content = content

    def render(self):
        return render_template_string(
            get_jinja_subtemplate("outputs/outputtext.j2"),
            content=self.content)

class OutputChart_Matplotlib:
    def __init__(self, matplob_object):
        self.matplob_object = matplob_object

    def render(self):
        # Create a bytes buffer for the image to save to
        buf = io.BytesIO()

        # Convert the plt object to a Figure, then save the figure to the buffer
        self.matplob_object.savefig(buf, format="png", bbox_inches='tight')
        buf.seek(0)

        # Convert bytes to a data URL (base64 encoding)
        encoded_bytes = base64.b64encode(buf.getvalue())
        data_url = "data:image/png;base64," + encoded_bytes.decode('utf8')

        buf.close()

        return render_template_string(
            get_jinja_subtemplate("outputs/outputchart_matplotlib.j2"),
            image=data_url)


class OutputChart_Altair:
    def __init__(self, altair_chart, chart_title, chart_id):
        self.altair_chart = altair_chart
        self.chart_title = chart_title
        self.chart_id = chart_id

    def render(self):
        chart_json = json.dumps(self.altair_chart.to_dict())
        
        return render_template_string(
            get_jinja_subtemplate("outputs/outputchart_altair.j2"),
            chart_json=chart_json, chart_title = self.chart_title,
            chart_id=self.chart_id)


class OutputTable_HTML:
    def __init__(self, data):
        self.data = data  # Assuming data is a list of dictionaries

    def render(self):
        return render_template_string(
            get_jinja_subtemplate("outputs/outputtable_html.j2"),
            data=self.data)


class OutputImage:
    def __init__(self, src, alt=""):
        self.src = src
        self.alt = alt

    def render(self):
        return render_template_string(
            get_jinja_subtemplate("outputs/outputimage.j2"),
            src=self.src, alt=self.alt)


class OutputMarkdown:
    def __init__(self, markdown_content):
        self.markdown_content = markdown_content

    def render(self):
        html_content = markdown(self.markdown_content)    
        return render_template_string(
            get_jinja_subtemplate("outputs/outputmarkdown.j2"),
            content=html_content)