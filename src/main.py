"Imports"
import sys
import getopt
import remote
import model

def main(argv):
    "Main function for remote"

    ## Read arguments
    port = "1238"

    try:
        opts, _ = getopt.getopt(argv, "hp:", ["port="])
    except getopt.GetoptError:
        print 'remote.py -p port'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'remote.py -p port'
            sys.exit()
        elif opt in ("-p", "--port"):
            port = arg

    print "Starting model on port " + port

    #################
    ## Start model ##
    #################
    remote.run(int(port), model.MODEL)

if __name__ == "__main__":
    main(sys.argv[1:])
