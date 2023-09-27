import obpgenerator.manufacturing_settings as settings

class Contour:
    def __init__(self):
        self.paths = [] # Array of matplotlib.path describing the contour
        self.settings = self.manufacturing_settings = settings.ManufacturingSetting() # Manufacturing settings
        self.melt_strategy = "point_random" # Melting strategy
        self.melt_settings = dict() # Melting settings
        self.nmb_of_scans = 1 # Number of times the Contour should be scanned
        self.start_angle = 0 # At which angle (in degree) in each path the scan should start