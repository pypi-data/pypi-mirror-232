import os

templates = os.listdir(os.path.join(os.path.dirname(__file__), 'dashboard_templates'))
templates_dict = {os.path.splitext(template)[0]: template for template in templates}

def get_dashboard_template(template_name: str) -> str:
    """
    Retrieves a dashboard template from the dashboard builder templates directory.

    Args:
        template_name (str): The name of the template to retrieve. For example, 'base' 
        will retrieve the 'base.j2' template from the dashboard builder templates 
        directory.

        Currently, you have two options:
        - 'base': Template with a sidebar and main content area. Use for interactive 
            widgets in the sidebar.
        - 'base_no_sidebar': Template with only a main content area. Use if no sidebar 
            with interactive inputs is desired.

    Returns:
        str: The content of the template.
    """
    current_dir = os.path.dirname(__file__) 
    file_name = templates_dict.get(template_name, template_name)
    template_path = os.path.join(current_dir, 'dashboard_templates', file_name)
    
    with open(template_path, 'r') as file:
        return file.read()

def get_dashboard_template_custom(template_name_with_extension: str, config) -> str:
    """
    Retrieves a custom dashboard template from a user-defined templates directory.

    Args:
        template_name_with_extension (str): The name of the template, including its 
        file extension. For example, 'my_template.j2' or 'another_template.html' 
        will retrieve the respective template from the user-defined templates directory.
        
        config (Config): The Config object containing configuration for the dashboard.

    Returns:
        str: The content of the template.

    Raises:
        FileNotFoundError: If the specified template is not found in the 
        user-defined directory.
    """
    template_dir = config.custom_template_dir  # Accessing  custom template directory from the Config object # noqa: E501
    template_path = os.path.join(template_dir, template_name_with_extension)
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template '{template_name_with_extension}' not found in the directory '{template_dir}'") # noqa: E501
    
    with open(template_path, 'r') as file:
        return file.read()
