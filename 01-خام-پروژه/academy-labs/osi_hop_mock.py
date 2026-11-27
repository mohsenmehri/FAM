"""Educational forwarding illustration; no packets, sockets or IOS devices."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Packet:
    src_ip: str
    dst_ip: str
    ttl: int


def forward(packet, ingress_dst_mac, egress_src_mac, next_hop_mac):
    """Model a successful IPv4 router hop; assume route and neighbor exist."""
    if packet.ttl <= 1:
        raise ValueError("TTL expired before forwarding")
    if not all((ingress_dst_mac, egress_src_mac, next_hop_mac)):
        raise ValueError("A successful hop requires link-layer addresses")
    return {
        "incoming_frame_dst": ingress_dst_mac,
        "outgoing_frame_src": egress_src_mac,
        "outgoing_frame_dst": next_hop_mac,
        "packet": Packet(packet.src_ip, packet.dst_ip, packet.ttl - 1),
    }


def main():
    result = forward(Packet("192.0.2.10", "198.51.100.80", 64),
                     "02:00:00:00:01:01", "02:00:00:00:02:01", "02:00:00:00:02:02")
    print("Mock only; no network traffic")
    print("outgoing L2:", result["outgoing_frame_src"], "->", result["outgoing_frame_dst"])
    print("L3:", result["packet"].src_ip, "->", result["packet"].dst_ip, "TTL", result["packet"].ttl)


if __name__ == "__main__":
    main()
