class Limits(object):
    """
    Limits to avoid exploding memory consumption in some cases
    """
    def __init__(self, max_text_features=80, max_css_features=120, max_links=2500):
        self.max_text_features = max_text_features
        self.max_css_features = max_css_features
        self.max_links = max_links
