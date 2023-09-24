import os

def get_template(template_name):
    current_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    template_path = os.path.join(current_dir, 'templates', template_name)
    
    with open(template_path, 'r') as file:
        return file.read()
