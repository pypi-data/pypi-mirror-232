import sys
import argparse

from karentify import karentify


def main(args):
    cmdline = argparse.ArgumentParser(description='Unleash your inner Karen, demanding entitlements')
    cmdline.add_argument('--dEmAnD-MaNaGeR', '-D', action='store_true', help='Demand to speak to somebody with actual authority')
    cmdline.add_argument('--aCtInG-OuT', '-V', action='count', default=0, help='Make visually clear that this issue is serious')
    cmdline.add_argument('entitlement', type=str, nargs='*', help='Your important message')
    opts = cmdline.parse_args(args)

    if opts.entitlement:
        print(karentify(' '.join(opts.entitlement), opts.aCtInG_OuT))
    else:
        if sys.stdin.isatty():
            print('Hello, how can I help you?')

        for s in sys.stdin:
            print(karentify(s.strip(), act_out=opts.aCtInG_OuT))

    if opts.dEmAnD_MaNaGeR:
        print()
        print(karentify('and I would like to talk to your manager', opts.aCtInG_OuT))


def run():
    # if this is not split up, the cli can't be tested by injecting args
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()
