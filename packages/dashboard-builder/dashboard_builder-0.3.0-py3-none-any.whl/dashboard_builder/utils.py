import os
import sys

def get_jinja_subtemplate(template_name):
    current_dir = os.path.dirname(__file__) #noqa: E501 add the parent folder to the path, e.g., root folder of dashboard_builder package 
    sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "../../")))
    template_path = os.path.join(current_dir, 'components/templates', template_name)
    with open(template_path, 'r') as file:
        return file.read()