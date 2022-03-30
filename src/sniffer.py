# coding=utf-8

from scapy import all as cap


def get_iface():
    faces = cap.get_working_ifaces()
    for face in faces:
        if face.name == 'Wi-Fi':
            return face
    return None


def main():
    face = get_iface()
    source = cap.SniffSource(iface=face)
    # source = cap.SniffSource(iface=cap.conf.iface)
    wire = cap.WiresharkSink()

    def transf(pkt):
        if not pkt or cap.IP not in pkt:
            return pkt
        pkt[cap.IP].src = "1.1.1.1"
        pkt[cap.IP].dst = "2.2.2.2"
        print(pkt)
        return pkt

    source > cap.TransformDrain(transf)
    p = cap.PipeEngine(source)
    p.start()
    p.wait_and_stop()


if __name__ == '__main__':
    main()
