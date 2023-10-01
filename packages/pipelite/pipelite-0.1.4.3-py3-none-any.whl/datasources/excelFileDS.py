__author__ = "datacorner.fr"
__email__ = "admin@datacorner.fr"
__license__ = "MIT"

from pipelite.parents.DataSource import DataSource 
import pipelite.constants as C
import os
import importlib.resources

CFGPARAMS_PATH = "path"
CFGPARAMS_FILENAME = "filename"
CFGPARAMS_SHEET = "sheet"
CFGFILES_DSOBJECT = "excelFileDS.json"

class excelFileDS(DataSource):

    def __init__(self, config, log):
        super().__init__(config, log)
        self.sheet = 0
        self.filename = C.EMPTY

    @property
    def parametersValidationFile(self):
        filename = importlib.resources.files(C.RESOURCE_PKGFOLDER_DATASOURCES).joinpath(CFGFILES_DSOBJECT)
        return str(filename)
    
    def initialize(self, cfg) -> bool:
        """ initialize and check all the needed configuration parameters
        Args:
            params (json list) : params for the data source.
                example: {'separator': ',', 'filename': 'test2.csv', 'path': '/tests/data/', 'encoding': 'utf-8'}
        Returns:
            bool: False if error
        """
        try:
            self.sheet = cfg.getParameter(CFGPARAMS_SHEET, C.EMPTY)
            self.filename = os.path.join(cfg.getParameter(CFGPARAMS_PATH, C.EMPTY), 
                                         cfg.getParameter(CFGPARAMS_FILENAME, C.EMPTY))

            # Checks ...
            if (self.ojbType == C.PLJSONCFG_LOADER):
                if (not os.path.isfile(self.filename)):
                    raise Exception("The file {} does not exist or is not accessible.".format(self.filename))
            
            return True
        except Exception as e:
            self.log.error("{}".format(e))
            return False
    
    def extract(self) -> int:
        """ Returns all the data in a DataFrame format
        Returns:
            pd.DataFrame(): dataset read
        """
        try:
            self.log.info("Extract the Dataset from the file: {}".format(self.filename))
            self.content.read_excel(self.filename, 
                         sheet_name=self.sheet)
            return self.content.count
        except Exception as e:
            self.log.error("{}".format(e))
            return False