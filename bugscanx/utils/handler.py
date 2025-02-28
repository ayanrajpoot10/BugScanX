import asyncio

def run_1():
    from bugscanx.modules.scanners.pro import main_pro_scanner
    main_pro_scanner.pro_main()

def run_2():
    from bugscanx.modules.scanners import host_scanner
    host_scanner.sub_main()

def run_3():
    from bugscanx.modules.scanners import cidr_scanner
    cidr_scanner.cidr_main()

def run_4():
    from bugscanx.modules.scrappers.subfinder import sub_finder
    asyncio.run(sub_finder.find_subdomains())

def run_5():
    from bugscanx.modules.scrappers.ip_lookup import ip_lookup
    asyncio.run(ip_lookup.iplookup_main())

def run_6():
    from bugscanx.modules.miscellaneous import txt_toolkit
    txt_toolkit.txt_toolkit_main()

def run_7():
    from bugscanx.modules.scanners import open_port
    open_port.open_port_main()

def run_8():
    from bugscanx.modules.miscellaneous import dns_info
    dns_info.dns_main()

def run_9():
    from bugscanx.modules.miscellaneous import osint
    osint.osint_main()

def run_10():
    from bugscanx.modules.miscellaneous import script_help
    script_help.show_help()

def run_11():
    from bugscanx.modules.miscellaneous import script_updater
    script_updater.check_and_update()
