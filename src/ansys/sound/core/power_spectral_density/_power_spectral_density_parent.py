"""PowerSpectralDensityParent."""
from .._pyansys_sound import PyAnsysSound

class PowerSpectralDensityParent(PyAnsysSound):
    """
    Provides the base class for PowerSpectralDensity classes.
    
    This is the base class of all PowerSpectralDensity classes and should not be used directly.
    """

    def __init__(self):
        """Init.
        
        Init the class.
        """
        super().__init__()