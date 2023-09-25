class Config:
    def __init__(self, custom_template_dir: str = "templates", footer_text: str = ""):

        """
        
        Parameters
        ----------
        template_dir : str, optional
            The directory where the templates are stored, by default "templates"

        footer_text : str, optional
            The text to display in the footer of the dashboard, by default ""

        """

        self.custom_template_dir = custom_template_dir
        self.footer_text = footer_text
