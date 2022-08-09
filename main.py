import getopt
import sys
from code_generator import generate


def main(argv):

    input_file, output_file = '', ''
    try:
        opts, args = getopt.getopt(argv, "dhpsi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg

    with open('tests/' + input_file, "r") as input_file_data:
        code = input_file_data.read()
    output_file = open('tests/' + output_file, "w")
    mips_code = generate(code)
    output_file.write(mips_code)


if __name__ == "__main__":
    main(sys.argv[1:])
