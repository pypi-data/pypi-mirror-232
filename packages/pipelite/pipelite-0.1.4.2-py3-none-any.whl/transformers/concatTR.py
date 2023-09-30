__author__ = "datacorner.fr"
__email__ = "admin@datacorner.fr"
__license__ = "MIT"

import pipelite.utils.constants as C
from pipelite.parents.Transformer import Transformer
from pipelite.etlDataset import etlDataset
from pipelite.etlDatasets import etlDatasets

CFGFILES_DSOBJECT = C.CFG_PARAMETER_DEF_FOLDER + "/transformers/concatTR.json"

class concatTR(Transformer):

    @property
    def parametersValidationFile(self):
        return CFGFILES_DSOBJECT
    
    def initialize(self, params) -> bool:
        """ Initialize and makes some checks (params) for that transformer
        Args:
            params (json): parameters
        Returns:
            bool: False if error
        """
        return True
    
    def transform(self, dsStack):
        """ Concatenate 2 or more datasets together
        Args:
            dsStack (etlDatasets): multiple datasets to concat in a collection
        Returns:
            etlDatasets: Output etlDataset collection of the transformer(s).
            int: Number of rows transformed
        """
        try:
            output = etlDataset()
            self.log.info("There are {} datasets to concatenate".format(dsStack.count))
            for obj in dsStack:
                self.log.debug("Adding {} rows from the dataset {}".format(obj.count, obj.name))
                output.concatWith(obj)
            # Return the output as a collection with only one item with the excepted name
            dsOutputs = etlDatasets()
            # Create from the source another instance of the data
            output.name = self.dsOutputs[0]
            dsOutputs.add(output)
            return dsOutputs, output.count
        except Exception as e:
            self.log.info("concatTR.transform() -> ".format(e))
            return dsStack, 0