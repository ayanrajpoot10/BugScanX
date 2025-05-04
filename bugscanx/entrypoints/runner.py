def run_1():
    from bugscanx.modules.scanners_pro import host_scanner_pro
    host_scanner_pro.main()

def run_2():
    from bugscanx.modules.scanners import host_scanner
    host_scanner.main()

def run_3():
    from bugscanx.modules.scanners import cidr_scanner
    cidr_scanner.main()

def run_4():
    from bugscanx.modules.scrapers.subfinder import subfinder
    subfinder.main()

def run_5():
    from bugscanx.modules.scrapers.iplookup import iplookup
    iplookup.main()

def run_6():
    from bugscanx.modules.others import file_toolkit
    file_toolkit.main()

def run_7():
    from bugscanx.modules.scanners import open_port
    open_port.main()

def run_8():
    from bugscanx.modules.others import dns_records
    dns_records.main()

def run_9():
    from bugscanx.modules.others import host_info
    host_info.main()

def run_10():
    from bugscanx.modules.others import script_help
    script_help.show_help()

def run_11():
    from bugscanx.modules.others import script_updater
    script_updater.check_and_update()
