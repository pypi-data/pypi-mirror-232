import os

templates = os.listdir(os.path.join(os.path.dirname(__file__), 'dashboard_templates'))
templates_dict = {os.path.splitext(template)[0]: template for template in templates}

def get_dashboard_template(template_name):
    """
    Retrieves a dashboard template from the dashboard builder templates directory.

    Args:
    - *template_name (str): The name of the template to retrieve. 
    For example, 'base' will retrieve the 'base.j2' template from the 
    dashboard builder templates directory. 

    Currently you have two options:
    - 'base': This is a template that contains a sidebar and a main content area. 
    This should be used if you want interactive widgets in the sidebar.
    - 'base_no_sidebar': This is a template that contains only a main content area. 
    This should be used if you do not want a sidebar with interactive inputs. 

    Returns:
    - str: The content of the template. 

    """
    current_dir = os.path.dirname(__file__) 
    # Fetching the correct file name from the dictionary
    file_name = templates_dict.get(template_name, template_name)
    template_path = os.path.join(current_dir, 'dashboard_templates', file_name)
    
    with open(template_path, 'r') as file:
        return file.read()
