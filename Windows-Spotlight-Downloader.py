import traceback
import requests, os , re , json
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup as BS

STATE_FILE = "state.json"
start_time = datetime.now()
print("The program started at " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
FirstRun = True
Counter = 0
url = 'https://windows10spotlight.com'
proxies = {'http': 'socks5://192.168.1.3:1080','https': 'socks5://192.168.1.3:1080'}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://google.com',
    'Connection': 'keep-alive'
}
timeout = 5

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def URLGrabber(url):
    try:
        global request , TestStatus
        TestStatus = True
        request = requests.get(url, headers=headers , timeout=timeout)
        return request , TestStatus
    except:
        TestStatus = False
        print("Network Error. Please Check Your Connection And Try Again...")
        return TestStatus

def FileSaver(content,path):
    try:
        os.makedirs('Download\\%s' % Type)
    except:
        pass
    try:
        global Counter
        with open(path , "wb") as file:
            file.write(content)
            Counter += 1
            print("%i File(s) Saved" % Counter)
    except:
        print("File is locked or inaccessible.")

def HTMLParser(data):
    global soup , PageTitle
    data = request.text
    soup = BS(data,"html.parser")
    PageTitle = re.sub("[^A-Za-z0-9]"," ",str(soup.find("h1").text).strip()).strip().replace('   ',' ').replace('  ',' ')
    return soup , PageTitle

def main():
    global Type , url , FirstRun , state
    state = load_state()
    if state.get("full_run_done") == None:
        state["full_run_done"] = False
        save_state(state)
    while True:
        URLGrabber(url)
        if TestStatus == True:
            if request.status_code == 200:
                HTMLParser(request)
                if FirstRun == True:
                    LastPageNumber = str(soup.find("div", class_="nav-links").find('span' , class_='page-numbers dots').find_next('a' , class_='page-numbers').text).replace(',','')
                    RecentPostDate = soup.find("span", class_="date").text
                    FirstRun = False
                CurrentPageNumber = str(soup.find("span", class_="page-numbers current").text).replace(',','')
                print('Page %s of %s ' % (CurrentPageNumber , LastPageNumber))
                PostsLinks = soup.find_all("a", class_="anons-thumbnail show")
                try:
                    NextPage = soup.find("a", class_="next page-numbers").get('href')
                    url = NextPage
                except:
                    url = None
                    pass
                PostURL = []
                ImageURL = []
                for link in PostsLinks:
                    PostURL.append(link.get('href'))
                for Post in PostURL:
                    URLGrabber(Post)
                    if TestStatus == True:
                        if request.status_code == 200:
                            HTMLParser(request)
                            ImageLink = soup.find("div", class_="entry").find_all('a')
                            for imglink in ImageLink:
                                if imglink == ImageLink[-1]:
                                    Type = 'Portrait'
                                else:
                                    Type = 'Landscape'
                                ImageURL.append(imglink.get('href'))
                                ContentURL = imglink.get('href')
                                Extension = ContentURL.rsplit('.',1)[-1]
                                if Extension.lower() == 'jpg' or Extension.lower() == 'png' or Extension.lower() == 'bmp' or Extension.lower() == 'tiff' or Extension.lower() == 'webp':
                                    Path = 'Download\\%s\\%s-%s.%s' % (Type , PageTitle , Type , Extension)
                                    if not(os.path.isfile(Path) and os.access(Path, os.R_OK) and os.stat(Path).st_size > 10240):
                                        URLGrabber(ContentURL)
                                        if TestStatus == True:
                                                if request.status_code == 200:
                                                    Content = request.content
                                                    FileSaver(Content,Path)
                                    else:
                                        print('File already exists:' , Path)
                                #sleep(1)
                if url == None:
                    print('That was last page.')
                    state["full_run_done"] = True
                    state["last_post_date"] = RecentPostDate
                    save_state(state)
                    break
        else:
            print('Trying Again After 30 Seconds...')
            sleep(30)
            continue
    end_time = datetime.now()
    duration = end_time - start_time
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    print("The program ended at " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(f"The program ran in {hours} hour(s), {minutes} minute(s), and {seconds} second(s).")
    pass

try:
    main()
except Exception:
    print("An error occurred. Details are written to 'error.log'")
    traceback.print_exc()
    with open("error.log", "a") as log_file:
        log_file.write("=== ERROR START ===\n")
        traceback.print_exc(file=log_file)
        log_file.write("=== ERROR END ===\n\n")
finally:
    input("Press Enter to exit...")