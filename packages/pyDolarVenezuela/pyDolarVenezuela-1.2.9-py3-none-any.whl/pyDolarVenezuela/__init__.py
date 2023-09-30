from pyDolarVenezuela import pages
from pyDolarVenezuela import network
from pyDolarVenezuela.tools import currency_converter
from .provider import Provider

import json
from colorama import Fore

version = '1.2.9'

def check_dependence_version():
    response = network.get("https://pypi.org/pypi/pydolarvenezuela/json")
    latest_version = json.loads(response)["info"]["version"]

    if version != latest_version:
        print(f"{Fore.GREEN}New version: {latest_version}.{Fore.RESET} {Fore.RED}Current version {version}.{Fore.RESET} write the following command: pip install --upgrade pyDolarVenezuela\n")

check_dependence_version()

def getdate():
    from pyDolarVenezuela.tools import TimeDollar
    t = TimeDollar()

    return t.get_time_zone()

class Monitor:
    def __init__(self, provider: pages.Monitor) -> None:
        if not isinstance(provider, pages.Monitor):
            raise TypeError("El parámetro debe ser un objeto del tipo Monitor.")
        
        self.provider = provider

    def get_value_monitors(self, monitor_code: str = None, name_property: str = None, prettify: bool = False):
        return Provider.select_monitor(self.provider, monitor_code, name_property, prettify)

__all__ = ['pages', 'currency_converter', 'getdate', 'Monitor']