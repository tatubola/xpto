def calculate_percent_use_of_switch_ports(ports, available_ports):
    if ports:
        return round(
            (available_ports * 100) / (ports.count())
        ) if available_ports else 100
    else:
        return 0
