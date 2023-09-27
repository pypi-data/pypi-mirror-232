from bs4 import BeautifulSoup
# from pprint import pp

import requests
import ast


header = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
          'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.9',
          'Connection': 'keep-alive', 
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15'}
# url = 'https://www.jellycat.com/us/bartholomew-bear-barm3br/'
# resp = requests.get(url, headers=header)
# html = resp.text
# soup = BeautifulSoup(html, "html.parser")
# print(soup.body.get_text().strip())
# with open('html.pkl', 'wb') as f:
#     pickle.dump(resp, f)

def get_page(url, log):
    if "https://www.jellycat.com" not in url:
        if log:
            print("~Not a Valid url, example url: \"https://www.jellycat.com/us/toastie-vivacious-aubergine-tov3au/\"")
        return None
    resp = requests.get(url, headers=header)
    html = resp.text
    soup = BeautifulSoup(html, "html.parser")
    if log:
        print("~Response recieved, Start finding stock list")
    return resp.text

def get_stock(url, s, log):
    soup = BeautifulSoup(s, "html.parser")
    script = soup.findAll("script")
    for n in script:
        if 'variants =' in str(n.text):
            for line in str(n.text).splitlines():
                if 'variants =' in line:
                    if log:
                        print("~Stock Information found, Decoding")
                    temp = ast.literal_eval(_helper(n.text, n.text.find('variants =') + 10))
                    rtn = {}
                    for n in temp.keys():
                        rtn[n] = [temp[n]["name"], temp[n]["stock_level"], url]
                    return rtn
    print("~No Stock information found, try a new link")
    return None

def _helper(s, i):
    stack = []
    end = i
    while s[end] != '{':
        end += 1
    stack.append(True)
    end += 1
    while stack != []:
        if s[end] == '{':
            stack.append(True)
        if s[end] == '}':
            stack.pop()
        end += 1
    return s[i:end]

def check(url, log=True):
    return get_stock(url, get_page(url, log), log)

# if __name__ == '__main__':
#     pp(check("https://www.jellycat.com/us/toastie-vivacious-aubergine-tov3au/"))