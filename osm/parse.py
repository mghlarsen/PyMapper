import sys
import string
import xml.sax

class OsmDocumentHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.state = 'INIT'
        self.data = list()

    def startDocument(self):
        if self.state != 'INIT':
            raise xml.sax.SAXException("Not initialized properly.") 
        self.state = 'START'     
        self.doc_attrs = None
    
    def endDocument(self):
        if self.state != 'END':
            raise xml.sax.SAXException("Malformed input.")
        self.state = 'INIT'

    def startElement(self, name, attrs):
        if self.state == 'START':
            if name == 'osm':
                self.doc_attrs = attrs
                self.state = 'BASE'
            else:
                raise xml.sax.SAXException("Missing <osm> tag.")
        elif self.state == 'BASE':
            if name == 'bounds':
                self.data.append(('BOUNDS', attrs))
            elif name == 'node':
                self.state = 'NODE'
                self.tags = dict()
                self.nodeAttrs = attrs
            elif name == 'way':
                self.state = 'WAY'
                self.tags = dict()
                self.wayNodes = list()
                self.wayAttrs = attrs
            elif name == 'relation':
                self.state = 'RELATION'
                self.tags = dict()
                self.relationMembers = list()
                self.relationAttrs = attrs
            else:
                raise xml.sax.SAXException("Invalid tag '<%s>' in BASE state." % (name, ))
        elif self.state == 'NODE':
            if name == 'tag':
                self.tags[attrs['k']] = attrs['v']
            else:
                raise xml.sax.SAXException("Invalid tag '<%s>' in NODE state." % (name, ))
        elif self.state == 'WAY':
            if name == 'tag':
                self.tags[attrs['k']] = attrs['v']
            elif name == 'nd':
                self.wayNodes.append(attrs['ref'])
            else:
                raise xml.sax.SAXException("Invalid tag '<%s>' in WAY state." % (name, ))
        elif self.state == 'RELATION':
            if name == 'tag':
                self.tags[attrs['k']] = attrs['v']
            elif name == 'member':
                self.relationMembers.append((attrs['role'], attrs['type'], attrs['ref']))
            else:
                raise xml.sax.SAXException("Invalid tag '<%s>' in RELATION state." % (name, ))
        else:
            raise xml.sax.SAXException("Unknown state '%s'." % (self.state, ))

    def endElement(self, name):
        if self.state == 'BASE':
            if name == 'osm':
                self.state = 'END'
            elif name == 'bounds':
                pass
            else:
                raise xml.sax.SAXException("Invalid closing tag '</%s>' in BASE state." % (name, ))
        elif self.state == 'NODE':
            if name == 'node':
                self.state = 'BASE'
                self.data.append(('NODE', self.nodeAttrs, self.tags))
                self.nodeAttrs = None
                self.tags = None
            elif name == 'tag':
                pass
            else:
                raise xml.sax.SAXException("Invalid closing tag </%s> in NODE state." % (name, ))
        elif self.state == 'WAY':
            if name == 'way':
                self.state = 'BASE'
                self.data.append(('WAY', self.wayAttrs, self.tags, self.wayNodes))
                self.wayAttrs = None
                self.wayNodes = None
                self.tags = None
            elif name == 'tag' or name == 'nd':
                pass
            else:
                raise xml.sax.SAXException("Invalid closing tag </%s> in WAY state." % (name, ))
        elif self.state == 'RELATION':
            if name == 'relation':
                self.state = 'BASE'
                self.data.append(('RELATION', self.relationAttrs, self.tags, self.relationMembers))
                self.relationAttrs = None
                self.relationMembers = None
                self.tags = None
            elif name == 'tag' or name == 'member':
                pass
            else:
                raise xml.sax.SAXException("Invalid closing tag </%s> in RELATION state." % (name, ))
        else:
            raise xml.sax.SAXException("Unknown state '%s'." % (self.state, ))

    def characters(self, chrs):
        pass

def parse(inFile):
    handler = OsmDocumentHandler()   
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    parser.parse(inFile)
    return handler.data

def test(inFileName):
    inFile = open(inFileName, 'r')
    data = parse(inFile)
    inFile.close()
    for d in data:
        print d

def main():
    args = sys.argv[1:]
    if len(args) != 1:
        print 'usage: python test.py infile.xml'
        sys.exit(-1)
    test(args[0])

if __name__ == '__main__':
    main()

