import MAPI
from MAPI.Util import *
from MAPI.Time import *
from MAPI.Struct import *

from plugintemplates import *

class addKeyword(IMapiDAgentPlugin):
    def PostDelivery(self, session, addrbook, store, folder, message):
        props = message.GetProps([0x8507001f], 0)
        Elements=props[0].Value.split('-', 2)
        if(len(Elements) == 2):
           try:
                   subelem = Elements[1].decode('utf-8').split('@');
                   str = subelem[0]
                   message.SetProps([SPropValue(0x8506101f, [str])])
                   message.SaveChanges(0)
           except:
                   self.logger.logFatal(sys.exc_info()[0])
        return MP_CONTINUE
