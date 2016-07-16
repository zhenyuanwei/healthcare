'''
Created on Jul 8, 2016

@author: wzy
'''
def phoneNumberCheck(phonenumber):
    returnValue = True
    if len(phonenumber) != 11 :
        returnValue = False
        
    formatType = '0123456789'
    for c in phonenumber :
        if not c in formatType :
            returnValue = False
            
    return returnValue

def required(item):
    returnValue = True
    if len(item) == 0:
        returnValue = False
        
    return returnValue