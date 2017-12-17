import sys
import time

from nv9biller import Biller


def main(port):
    biller = Biller(port)

    print('-------------------')
    print('Biller test program')
    print('SN: {:08X}'.format(biller.serial))
    print('--------------------')

    print('Enabling biller...')
    biller.channels_set(biller.CH_ALL)
    biller.display_enable()
    biller.enable()

    print('Done! Try to insert some notes (Ctrl+C to quit)')
    while True:
        try:
            events = biller.poll()
            for event in events:
                print(event)

            time.sleep(0.5)
        except KeyboardInterrupt:
            break

    print('Disabling biller...')
    biller.disable()
    biller.display_disable()
    biller.channels_set(None)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('Serial port not provided\n')
        sys.exit(1)

    main(sys.argv[1])
