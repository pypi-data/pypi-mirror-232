# components/managers.py

from flask import render_template_string
from markdown import markdown

from .inputs import (
    InputDropdown,
    InputSlider_Numerical,
    InputSlider_Categorical,
    InputRadio,
    TextInput
)


FORM_GROUP_TEMPLATE = """
<form method="post" action="{{ action_url }}">
    {% if markdown_top %}
        <div class="markdown-body">{{ markdown_top|safe }}</div>
    {% endif %}
    
    {% for input_component in inputs %}
        <div class="mb-4">{{ input_component|safe }}</div>
    {% endfor %}

    {% if markdown_bottom %}
        <div class="markdown-body mb-2">{{ markdown_bottom|safe }}</div>
    {% endif %}
    
    <button 
        type="submit" 
        class="rounded bg-white px-2 py-1 text-sm font-semibold 
        text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 
        hover:bg-gray-50"
    >
        Select
    </button>
</form>
"""


class ComponentManager:

    _registry = {}  # to keep track of available input types

    @classmethod
    def register_component(cls, component_type, component_class):
        """Register an input component type with the manager."""
        cls._registry[component_type] = component_class

    @classmethod
    def create_component(cls, component_type, *args, **kwargs):
        """Factory method to create and return an instance of an input component."""
        if component_type not in cls._registry:
            raise ValueError(f"No component type {component_type} registered.")
        
        component_class = cls._registry[component_type]
        return component_class(*args, **kwargs)

    @classmethod
    def create_form_group(cls, manager_instance, action_url, markdown_top, markdown_bottom, inputs): # noqa
        """
        Create a form group with various input types.

        Args:
        - manager_instance (ComponentManager): An instance of ComponentManager 
            to register inputs and form groups. 
        - action_url (str): The URL the form should post to.
        - markdown_top (str): Markdown content to display at the top of the form group.
        - markdown_bottom (str): Markdown content to display at the bottom of the 
            form group.
        - inputs (list): List of dictionaries describing each input 
            component.

        Returns:
        - FormGroup: The created FormGroup instance.
        """
        form_group = FormGroup(action_url=action_url, markdown_top=markdown_top, markdown_bottom=markdown_bottom) # noqa
        
        # Create and add inputs based on the 'inputs' parameter
        for input_data in inputs:
            input_type = input_data.pop('type')  # Extract the 'type' key and remove it from the dictionary # noqa
            input_component = cls.create_component(input_type, **input_data)
            form_group.add_inputs(input_component)
            manager_instance.register_inputs(input_component)

        # Register the form group
        manager_instance.register_form_groups(form_group)
        
        return form_group



    """
    Manages components (inputs, outputs, and layouts) for a dashboard or view.
    This class facilitates registering, updating, and rendering components.
    """
    def __init__(self, request):
        """
        Initialize the ComponentManager with a request object to handle 
        input components.
        
        Args:
            request (flask.Request): The current Flask request object.
        """
        self.request = request
        self.inputs = []
        self.form_groups = []   # list to store registered form groups
        self.outputs = []
        self.layouts = []


    def register_inputs(self, *input_components):
        """
        Register multiple input components, capture their values from the request, 
        and append them to the inputs list.

        Args:
        - *input_components (BaseInput): The input components to register.

        Returns:
        - list: List of registered input components.
        """
        for input_component in input_components:
            input_component.capture(self.request)
            self.inputs.append(input_component)
        return self.inputs
    
    def register_form_groups(self, *form_groups):
        """
        Register multiple form groups and append them to the form_groups list.
        
        Args:
        - *form_groups (FormGroupManager): The form groups to register.

        Returns:
        - list: List of registered form groups.
        """
        for form_group in form_groups:
            self.form_groups.append(form_group)
        return self.form_groups
    
    def register_output(self, output_component):
        """
        Register an output component and append it to the outputs list.
        
        Args:
        - output_component (BaseOutput): The output component to register.

        Returns:
        - BaseOutput: The registered output component.
        """
        self.outputs.append(output_component)
        return output_component
    
    def register_outputs(self, *output_components):
        """
        Register multiple output components and append them to the outputs list.
        
        Args:
        - *output_components (BaseOutput): The output components to register.

        Returns:
        - list: List of registered output components.
        """
        for output_component in output_components:
            self.outputs.append(output_component)
        return self.outputs
    
    def register_layouts(self, *layouts):
        """Register one or more layouts.

        Args:
        - *layouts (ColumnLayout): The layouts to register.

        Returns:
        - list: List of registered layouts.
        """
        for layout in layouts:
            self.outputs.append(layout)
        return layouts
    
    def render_inputs(self):
        """
        Render all the registered input components.
        
        Returns:
        - list: List of rendered input components.
        """
        return [input_component.render() for input_component in self.inputs]
    
    def render_form_groups(self):
        """
        Render each form group in the form_groups list as an HTML string.
        
        For each form group, the method:
        1. Renders its input components.
        2. Converts markdown content to HTML.
        3. Renders the entire form group with the provided FORM_GROUP_TEMPLATE.

        Returns:
        - list: List of rendered HTML strings for each form group.
        """
        rendered_form_groups = []
        for form_group in self.form_groups:
            inputs = [input_component.render() for input_component in form_group.inputs]
            rendered_form_group = render_template_string(
                FORM_GROUP_TEMPLATE, 
                action_url=form_group.action_url, 
                inputs=inputs,
                markdown_top=markdown(form_group.markdown_top),
                markdown_bottom=markdown(form_group.markdown_bottom)
            )
            rendered_form_groups.append(rendered_form_group)
        return rendered_form_groups
    
    def render_outputs(self):
        """
        Render all the registered output components.
        
        Returns:
        - list: List of rendered output components.
        """
        return [output_component.render() for output_component in self.outputs]
    
    def render_layouts(self):
        """Render all registered layouts."""
        return [layout.render() for layout in self.layouts]

class FormGroup:
    """
    Represents a form group that can contain multiple input components 
    and optional markdown content at the top and bottom.
    """
    def __init__(self, action_url='/', markdown_top=None, markdown_bottom=None):
        """
        Initializes a FormGroup with an action URL and optional markdown content.

        Args:
            action_url (str, optional): URL to which the form data should be posted. 
                Defaults to '/'.
            markdown_top (str, optional): Markdown content to be displayed at the 
                top of the section. Defaults to None.
            markdown_bottom (str, optional): Markdown content to be displayed at 
                the bottom of the section. Defaults to None.
        """
        self.action_url = action_url
        self.inputs = []
        self.markdown_top = markdown_top
        self.markdown_bottom = markdown_bottom


    def get_input(self, input_name):
        """Retrieve an input component by its name."""
        for input_component in self.inputs:
            if input_component.name == input_name:
                return input_component
        raise ValueError(f"No input with name {input_name} found in the form group.")

    def add_input(self, input_component):
        """Add a single input component to the form group."""
        self.inputs.append(input_component)

    def add_inputs(self, *input_components):
        """
        Add multiple input components to the form group.

        Args:
        - *input_components (BaseInput): The input components to add.

        Returns:
        - None
        """
        for input_component in input_components:
            self.inputs.append(input_component)

    def create_form_group(self, action_url, markdown_top, markdown_bottom, inputs):
        # Create the form group
        form_group = FormGroup(action_url=action_url, markdown_top=markdown_top, markdown_bottom=markdown_bottom) # noqa 
        
        # Create and add inputs based on the inputs parameter
        for input_data in inputs:
            if input_data['type'] == 'dropdown':
                input_component = InputDropdown(
                    name=input_data['name'], 
                    label=input_data['label'], 
                    values=input_data['values']
                )
                form_group.add_inputs(input_component)
                self.register_inputs(input_component)

        # Register the form group
        self.register_form_groups(form_group)
        
        return form_group
    

ComponentManager.register_component('dropdown', InputDropdown)
ComponentManager.register_component('text', TextInput)
ComponentManager.register_component('slider_numerical', InputSlider_Numerical)
ComponentManager.register_component('slider_categorical', InputSlider_Categorical)
ComponentManager.register_component('radio', InputRadio)