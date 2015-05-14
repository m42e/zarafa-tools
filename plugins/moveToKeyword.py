import MAPI
import re
from MAPI.Util import *
from MAPI.Time import *
from MAPI.Struct import *

import pprint

from plugintemplates import *

class moveToKeyword(IMapiDAgentPlugin):

    createFolder = 0

    def PreDelivery(self, session, addrbook, store, folder, message):
        # Get the original recipient
        PS_INTERNET_HEADERS = DEFINE_OLEGUID(0x00020386, 0, 0)
        NAMED_PROPS_INTERNET_HEADERS = [MAPINAMEID(PS_INTERNET_HEADERS, MNID_STRING, u'x-original-to'),]
        namedprop_ids = message.GetIDsFromNames(NAMED_PROPS_INTERNET_HEADERS, 0)
        namedprop_id = CHANGE_PROP_TYPE(namedprop_ids[0], PT_UNICODE)
        address = message.GetProps([namedprop_id], 0)[0]

        mailto = address.Value
        elements = re.split('-|\+|@', mailto)
        tag = elements[1]
        found = 0
        # Search for folder only If we do not want to create it anyway
        if createFolder == 0:
            folderid = store.GetProps([PR_IPM_SUBTREE_ENTRYID], 0)[0].Value
            folder2 = session.OpenEntry(folderid, None, 0)
            table = folder.GetHierarchyTable(0)
            table.SetColumns([PR_DISPLAY_NAME, PR_ENTRYID], 0)

            rows = table.QueryRows(-1, 0)
            for row in rows:
                if row[0].Value == tag:
                    found = 1

        if createFolder == 1 or found == 1:
            folder = folder.CreateFolder(FOLDER_GENERIC, tag.decode('utf-8'), u''.decode('utf-8'), None, MAPI_UNICODE|OPEN_IF_EXISTS)
            #now we have the folder, lets save the message
            msgnew = folder.CreateMessage(None, 0)
            tags = message.GetPropList(MAPI_UNICODE)
            message.CopyProps(tags, 0, None, IID_IMessage, msgnew, 0)
            msgnew.SaveChanges(0)
            #for notifying about the new mail we need a the ids
            folderid = folder.GetProps([PR_ENTRYID], 0)[0].Value
            msgid =  msgnew.GetProps([PR_ENTRYID], 0)[0].Value
            store.NotifyNewMail( NEWMAIL_NOTIFICATION(msgid, folderid, 0, None, 0) )
            # stop here, we already delivered the message successfully
            return MP_STOP_SUCCESS

        # in case we do not have a folder and do not want to create one, 
        # we add the tag to the subject
        subject = message.GetProps([PR_SUBJECT],0)[0].Value
        subject = "%s [%s]" % (subject, subelem)
        message.SetProps([SPropValue(PR_SUBJECT, subject)])
        return MP_CONTINUE

