def run_host_checker():
    from bugscanx.modules.scanners import host_checker
    host_checker.main()

def run_sub_scan():
    from bugscanx.modules.scanners import sub_scan
    hosts, ports, output_file, threads, = sub_scan.get_scan_inputs()
    if hosts is None:
        return
    sub_scan.perform_scan(hosts, ports, output_file, threads)

def run_ip_scan():
    from bugscanx.modules.scanners import ip_scan
    hosts, ports, output_file, threads, method = ip_scan.get_ip_scan_inputs()
    ip_scan.perform_ip_scan(hosts, ports, output_file, threads, method)

def run_sub_finder():
    from bugscanx.modules.scrappers import sub_finder
    sub_finder.find_subdomains()

def run_ip_lookup():
    from bugscanx.modules.scrappers import ip_lookup
    ip_lookup.Ip_lookup_menu()

def run_txt_toolkit():
    from bugscanx.modules.miscellaneous import txt_toolkit
    txt_toolkit.txt_toolkit_main_menu()

def run_open_port():
    from bugscanx.modules.scanners import open_port
    open_port.open_port_checker()

def run_dns_info():
    from bugscanx.modules.miscellaneous import dns_info
    dns_info.main()

def run_osint():
    from bugscanx.modules.miscellaneous import osint
    osint.osint_main()

def run_help_menu():
    from bugscanx.modules.miscellaneous import script_help
    script_help.show_help()

def run_script_updater():
    from bugscanx.modules.miscellaneous import script_updater
    script_updater.check_and_update()
