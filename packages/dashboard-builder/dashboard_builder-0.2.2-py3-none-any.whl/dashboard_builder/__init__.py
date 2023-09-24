import os

templates = os.listdir(os.path.join(os.path.dirname(__file__), 'templates'))
templates_dict = {os.path.splitext(template)[0]: template for template in templates}

def get_dashboard_template(template_name):
    """
    Retrieves a dashboard template from the dashboard builder templates directory.

    Args:
    - *template_name (str): The name of the template to retrieve. 
    For example, 'base' will retrieve the 'base.html' template from the 
    dashboard builder templates directory. 

    Returns:
    - str: The content of the template. 

    """
    current_dir = os.path.dirname(__file__) 
    # Fetching the correct file name from the dictionary
    file_name = templates_dict.get(template_name, template_name)
    template_path = os.path.join(current_dir, 'templates', file_name)
    
    with open(template_path, 'r') as file:
        return file.read()
