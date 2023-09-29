import sys

import docopt

import wcwidth_browser2 

if __name__ == '__main__':
    sys.exit(wcwidth_browser2.main(wcwidth_browser2.validate_args(docopt.docopt(wcwidth_browser2.__doc__))))
