class Config:
    def __init__(self, custom_template_dir: str = "templates", footer_text: str = ""):
        """
        Initializes a new instance of the Config class.

        Args:
            custom_template_dir (str, optional): The directory where 
                the templates are stored. Defaults to "templates".
            footer_text (str, optional): The text to display in the footer of 
                the dashboard. Defaults to an empty string.

        Example:
            >>> config = Config(custom_template_dir="my_templates", 
                    footer_text="My Dashboard") 

        """
        self.custom_template_dir = custom_template_dir
        self.footer_text = footer_text
