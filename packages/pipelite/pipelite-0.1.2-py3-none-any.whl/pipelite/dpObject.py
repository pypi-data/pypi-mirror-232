__author__ = "datacorner.fr"
__email__ = "admin@datacorner.fr"
__license__ = "MIT"

import importlib
import pipelite.utils.constants as C

class dpObject:
    def __init__(self, config, log):
        self.log = log
        self.config = config
        self.name = ""
        self.ojbType = None

    def getValFromDict(self, params, name, default=None):
        """ return the param[name] value, if does not exist returns default
        Args:
            params (dict): python dict
            name (str): name
            default (obj, optional): Default value
        Returns:
            obj: value
        """
        try:
            return params[name] 
        except:
            return default

    def initialize(self, params) -> bool:
        """ initialize and check all the needed configuration parameters
        Args:
            params: set of json parameters for the object initialisation
        Returns:
            bool: False if error
        """
        return True
    
    @staticmethod
    def instantiate(fullClassPath, config, log):
        """ This function dynamically instanciate the right data Class to create a pipeline object. Note: the class must inherit from the dpInstantiableObj class.
            This to avoid in loading all the connectors (if any of them failed for example) when making a global import, 
            by this way only the needed import is done on the fly
            Args:
                classname (str): full classname (must inherit from the dpInstantiableObj Class)
            Returns:
                Object (dpInstantiableObj): Object
        """
        try:
            # Get the class to instantiate
            if (fullClassPath == C.EMPTY):
                raise Exception("The {} parameter is mandatory and cannot be empty".format(fullClassPath))
            else:
                # Get the latest element : the class name without the path
                pipelineClass = fullClassPath.split(".")[-1]

            # Instantiate the pipeline object
            log.debug("pipelineFactory.instantiate(): Import module -> {}".format(fullClassPath))
            datasourceObject = importlib.import_module(name=fullClassPath)
            log.debug("pipelineFactory.instantiate(): Module {} imported, instantiate the class".format(fullClassPath))
            pipelineClassInst = getattr(datasourceObject, pipelineClass)
            objectInst = pipelineClassInst(config=config, log=log)
            log.info("Class instantiated successfully")
            return objectInst
        except Exception as e:
            log.error("etlObject.instantiate(): Error when loading the Class: {}".format(str(e)))
        return None