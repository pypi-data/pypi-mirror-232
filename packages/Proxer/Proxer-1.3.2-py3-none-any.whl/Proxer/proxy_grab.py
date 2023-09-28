
from json import loads
from requests import get
from bs4 import BeautifulSoup
from os import system
from sys import platform

cls = lambda: system("cls") if platform in ["win32", "cygwin"] else system("clear")

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'} # Be sure to add a browser header to bypass protection

_blacklisted = ['IP address', 'Port', 'Country, City', '<td class="speed_col">Speed</td>', 'Type', 'Anonymity', 'Latest update']
_connection_protocol = ["HTTP", "HTTPS", "SOCKS4", "SOCKS5"]
_anonymity_type = ["High", "Average", "Low", "no"]
_protocol_addons = {"HTTP": "h", "HTTPS": "s", "SOCKS4": "4", "SOCKS5": "5"} 
_anonymity_addons = {"High": "4", "Average": "3", "Low": "2", "no": "1"}

class proxyGrab:
    class proxyscrape:
        def request(protocol="http"):
            url = f"https://api.proxyscrape.com/v2/?request=getproxies&protocol={protocol}&timeout=10000&country=all&ssl=all&anonymity=all"
            request = get(url, headers=headers)
            return request 
        def sort(request) -> dict:
            api_data = request.text
            result = []
            for i in api_data.split("\r\n"):
                try: result.append({"address": i.split(":")[0], "port": i.split(":")[1]})
                except IndexError:...
            return result
    class geonode:
        def request(proxies=50):
            url = f"https://proxylist.geonode.com/api/proxy-list?limit={proxies}&page=1&sort_by=lastChecked&sort_type=desc" # Using geonode API
            request = get(url, headers=headers)
            return request.text
        def sort(request) -> dict:
            print(request)
            api_data = loads(request)
            result = []
            for i in api_data["data"]:
                result.append({"address": i["ip"], "port": i["port"], "protocol": i["protocols"], "city": i["city"], "last_update": i["updated_at"]})
            return result
    class free_proxy_list:
        def request():
            """This function doing request to free proxy list"""
            url = "https://free-proxy-list.net/"
            request = get(url, headers=headers)
            return request
        def sort(request) -> dict:
            """This function using request and converts it to dict"""
            soup = BeautifulSoup(request.text, 'html.parser')
            all = soup.find_all('td')
            result_item = {}
            result = []
            for i in all:
                i = str(i)
                if "<td>" in i:
                    i = i.replace("<td>", "").replace("</td>", "") # Remove the opening and closing HTML tags <td> and </td>.
                if i.replace(".", "").isdigit() and len(i) > 5:
                    result_item["address"] = i
                elif i.isdigit():
                    result_item["port"] = i
                else:
                    if result_item != {}:
                        result_item["protocol"] = "HTTP"
                        result.append(result_item)
                    result_item = {}
            return result
    class hidemyname:
        def request(page: int=1):
            """This function makes a request and returns a response from the resource"""
            url_prefix = "" # Used for content filtering and other results. In essence, it is an expanded capability to produce results
            d = 64 # Progression difference
            if page > 2: # NOTE: Change this > to this >=
                a = d*(page-1) # Calculate the required term of the progression using the formula
                url_prefix = f"?start={str(a)}#list" # Adding the result to the link prefix
            elif page == 2: # NOTE: I know that this is the same as above, it is important to remove in the future
                url_prefix = f"?start={str(d)}#list" # Add at once the difference of the progression

            url = "https://hidemy.name/en/proxy-list/" + url_prefix
            
            request = get(url, headers=headers)
            return request
        def sort(request) -> dict:
            """This function converts the query result into a conveniently readable dictionary"""
            soup = BeautifulSoup(request.text, 'html.parser')
            all = soup.find_all('td')
            result = [] # This list will be returned by this function
            result_item = {} # One specific item will be stored here
            for i in all:
                i = str(i)
                if "<td>" in i:
                    i = i.replace("<td>", "").replace("</td>", "") # Remove the opening and closing HTML tags <td> and </td>.
                if i not in _blacklisted and "div" not in i: # Remove blocked words (watch src/config.py)
                    if "." in i: # This is the IP address
                        result_item["address"] = i
                    if i.isdigit(): # It's a port.
                        result_item["port"] = i
                    if i in _anonymity_type: # This is the anonymity of the connection
                        result_item["anonymity"] = i
                    elif "protocol" not in result_item:
                        if i in _connection_protocol: # It's protocol.
                            result_item["protocol"] = i
                    else:
                        if result_item != {}:
                            result.append(result_item)
                        result_item = {}
            return result

def update_proxy_list(mode="hidemyname"):
    """
    Mode:
        hidemyname - scrape https://hidemy.name/en/proxy-list/
        free_proxy_list - scrape https://free-proxy-list.net/
        proxyscrape - scrape https://proxyscrape.com/
    """

    if mode == "hidemyname":
        output = []
        for d in range(1, 5):
            request = proxyGrab.hidemyname.request(page=d)
            result = proxyGrab.hidemyname.sort(request=request)
            for i in result:
                output.append(i)
        
        return output

    if mode == "free_proxy_list":
        request = proxyGrab.free_proxy_list.request()
        result = proxyGrab.free_proxy_list.sort(request)
        
        return result

    if mode == "proxyscrape":
        request = proxyGrab.proxyscrape.request(protocol="socks5")
        result = proxyGrab.proxyscrape.sort(request)
        return result
    
if __name__ == "__main__":
    print(update_proxy_list())