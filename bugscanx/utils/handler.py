def run_host_scanner_pro():
    from bugscanx.modules.scanners.pro import main_pro_scanner
    main_pro_scanner.main()

def run_host_scanner():
    from bugscanx.modules.scanners import sub_scan
    sub_scan.get_scan_inputs()

def run_cidr_scanner():
    from bugscanx.modules.scanners import ip_scan
    ip_scan.get_ip_scan_inputs()

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

def run_dns_records():
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
