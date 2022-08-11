import sys, getopt
import code_generator


def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "dhpsi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-d':
            debug = True
        if opt == '-s':
            run_scanner_option = True
        if opt == '-p':
            run_parser_option = True
        if opt == '-h':
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    with open('tests/' + inputfile, "r") as input_file:
        code = input_file.read()

    output_file = open('tests/' + outputfile, "w")

    mips = code_generator.generate(code)
    output_file.write(mips)


if __name__ == "__main__":
    main(sys.argv[1:])
