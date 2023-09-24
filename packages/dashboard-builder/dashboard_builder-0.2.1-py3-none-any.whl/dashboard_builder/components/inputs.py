# components/inputs.py

from flask import render_template_string
import os
import sys

def get_html_subtemplate(template_name):
    current_dir = os.path.dirname(__file__) #noqa: E501 add the parent folder to the path, e.g., root folder of dashboard_builder package 
    sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "../..")))
    template_path = os.path.join(current_dir, 'templates', template_name)
    with open(template_path, 'r') as file:
        return file.read()

class BaseInput:
    def __init__(self, name, default_value=""):
        self.name = name
        self.default_value = default_value

    def capture(self, request):
        self.value = request.form.get(self.name, self.default_value)

class InputDropdown(BaseInput):
    def __init__(self, name, label, 
                 values, action_url="/", selected_value="Select All"):
        super().__init__(name, selected_value)
        
        self.label = label
        if isinstance(values, tuple) and len(values) == 2 and hasattr(values[0], 'loc'):
            self.values = ["Select All"] + values[0][values[1]].unique().tolist()
        elif isinstance(values, list):
            self.values = ["Select All"] + values
        else:
            raise ValueError("""Invalid values provided. It should be either 
                             a list or a tuple with DataFrame and column name.""")
        
        self.action_url = action_url
        self.selected_value = selected_value

    def capture(self, request):
        self.value = request.form.get(self.name)

        print(f"Captured value for {self.name}: {self.value}")  # debugging
        
        if not self.value:
            self.value = "Select All"

        self.selected_value = self.value

    def render(self):
        return render_template_string(
            get_html_subtemplate("inputs/inputdropdown.html"), 
            name=self.name, label=self.label, 
            values=self.values, selected_value=self.selected_value)
    
class TextInput(BaseInput):
    def __init__(self, name, label, default_value=""):
        super().__init__(name, default_value)
        self.label = label

    def capture(self, request):
        self.value = request.form.get(self.name, self.default_value)
        self.default_value = self.value

    def render(self):
        return render_template_string(
            get_html_subtemplate("inputs/textinput.html"),
            name=self.name, label=self.label, 
            default_value=self.default_value)

class InputSlider_Numerical(BaseInput):
    def __init__(self, name, label, min_value=0, 
                 max_value=100, step=1, default_value=50):
        
        # Initialize the base attributes
        super().__init__(name, default_value)

        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.step = step

    def capture(self, request):
        self.value = int(request.form.get(self.name, self.default_value))
        self.default_value = self.value

    def render(self):
        return render_template_string(
            get_html_subtemplate("inputs/inputslider_numerical.html"),
            name=self.name, label=self.label, 
            min_value=self.min_value, max_value=self.max_value, step=self.step, 
            default_value=self.default_value)

class InputSlider_Categorical(BaseInput):
    def __init__(self, name, label, categories, default_value=None):
        # Ensure the "Select All" is the first option only
        self.categories = ["Select All"] + [cat for cat in categories 
                                            if cat != "Select All"]
        
        # The default value would be the first category if not provided
        super().__init__(name, default_value if default_value else self.categories[0])
        
        self.label = label

    def capture(self, request):
        self.value = request.form.get(self.name, self.default_value)
        # Update the default_value to the captured value for rendering purposes
        self.default_value = self.value

    def render(self):
        # Position is zero-indexed based on categories list
        default_position = self.categories.index(self.default_value)
        return render_template_string(
            get_html_subtemplate("inputs/inputslider_categorical.html"),
            name=self.name, label=self.label, max_position=len(self.categories)-1, 
            default_position=default_position, categories=self.categories)


class InputRadio(BaseInput):
    def __init__(self, name, label, options, default_value=None):
        # Ensure 'Select All' is the first option in the list
        if "Select All" not in options:
            options.insert(0, "Select All")

        # If no default_value is provided, set it to the first option
        super().__init__(name, default_value if default_value else options[0])

        self.label = label
        self.options = options

    def capture(self, request):
        captured_value = request.form.get(self.name)
        if not captured_value:
            # If no value is captured (i.e., no radio button was clicked),
            # keep the default_value unchanged.
            self.value = self.default_value
        else:
            self.value = captured_value
            # Update the default_value to the captured value for rendering purposes
            self.default_value = captured_value

    def render(self):
        return render_template_string(
            get_html_subtemplate("inputs/inputradio.html"),
            name=self.name, label=self.label, options=self.options, 
            default_value=self.default_value)
