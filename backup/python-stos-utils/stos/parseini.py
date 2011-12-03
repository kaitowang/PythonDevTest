#Name: parseini.py
#Desc: A module to provide a set of high-level APIs to parse ini files.
#Date: 2011.05.10

class ParseINIBase:
    """\
ParseINIBase - The base class for ParseINI

An abstract class to for ParseINI module, you should not use it directly.
    """
    def getValue(cls,session,key):
        pass
    def getKeyList(cls,session):
        pass
    def getSessionList(cls):
        pass
    def setValue(cls,session,key,value):
        pass
    def writeINI(cls):
        pass

class ParseINIcp(ParseINIBase):
    def __init__(cls,inifile):
        import ConfigParser
        cls._inifile=inifile
        cls._config=ConfigParser.ConfigParser()
        cls._config.optionxform=str
        cls._config.read(cls._inifile)
    def getValue(cls,session,key):
        return cls._config.get(session,key)
    def getKeyList(cls,session):
        return [ i[0] for i in cls._config.items(session) ]
    def getSessionList(cls):
        return cls._config.sections()
    def setValue(cls,session,key,value):
        cls._config.set(session,key,value)
        return value
    def writeINI(cls):
        cls._config.write(open(cls._inifile,'w'))

#class ParseINIco(ParseINIBase):
#    def __init__(cls,inifile):
#        import configobj
#        cls._inifile=inifile
#        cls._config=configobj.ConfigObj(cls._inifile)
#    def getValue(cls,session,key):
#        return cls._config[session][key]
#    def getKeyList(cls,session):
#        return cls._config[session].keys()
#    def getSessionList(cls):
#        return cls._config.keys()
#    def setValue(cls,session,key,value):
#        cls._config[session][key]=value
#        return value
#    def writeINI(cls):
#        cls._config.write()
