#!/usr/bin/python2.7
import zlib, cgitb, cgi, os

##
## TODO 's are reminders for the mature production implementation
##
class AbstractRecordService:

    def resolveFile(self, filename):
          raise Exception("resolveFile method not implemented")

    def onError(self, returnCode, message):
        print ("Status: " + returnCode)
        print ("Content-Type: text/html\r\n")
        print(message)

    def main(self):
        ## TODO make debugging switchable in config file
        self.debug()

        obj = zlib.decompressobj(16 + zlib.MAX_WBITS)
        filename = os.environ['REQUEST_URI'].split('/')[-1].split('?')[0]
        offset = int(os.environ['HTTP_RANGE'].split('-')[0].strip('bytes='))
        ## TODO check that range header exists and is specified in bytes. Otherwise return a 416.
        in_body = False
        try:
            with open(self.resolveFile(filename)) as fin:
                fin.seek(offset) ## TODO check try/except that this is not larger than the file
                while True:
                    data = fin.read(1024 * 1024)
                    if data == '':
                        break
                    try:
                        decompress_data = obj.decompress(data)
                        if not(in_body):
                            print("Content-type: application/warc\r\n")
                            in_body = True
                        print(decompress_data)
                    except zlib.error as e:
                        self.onError("416 Requested Range Not Satisfiable", "Invalid offset: " + filename + ":" + str(offset))
        except IOError as e:
            self.onError("404 Not Found", "Could not find file " + filename)

    def debug(self):
        cgitb.enable()
        cgi.test()


class PrototypeRecordService(AbstractRecordService):
    def resolveFile(self, filename):
            ## form = cgi.FieldStorage()
            ## TODO form values can be used in other implementations e.g. form["collection"].value might be part of the file path
            return '/data/' + filename

if __name__ == "__main__":
    ## TODO read the service name from a config-file
    service = "PrototypeRecordService"
    serviceClass_ = globals()[service]
    serviceClass_().main()


