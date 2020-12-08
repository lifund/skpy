
#================================================================
#==================== Python 3.8.6 libraries ====================
#================================================================

from sys import argv, exit
from time import strftime
import requests as req
from bs4 import BeautifulSoup
import csv
from pathlib import Path
from datetime import datetime





#========================================================================================================
#==================== bs4 오브젝트의 자식 엘리먼트 탐색/삭제를 위한 shorthand 메소드 ====================
#========================================================================================================

def bs4_selectAndStrip(parentElement=BeautifulSoup("<html></html>", 'html.parser'),selector=""):
    result = parentElement.select(selector)[0].text.replace('\n',' ').replace('\r',' ').replace('\r\n',' ').strip()
    return result
    
def bs4_extractElement(parentElement=BeautifulSoup("<html></html>", 'html.parser'),selector=""):
    """ ## !! This method will mutate the original parentElement object """
    parentElement.select(selector)[0].extract()
    pass





#=======================================================================
#==================== 성남시 베스트매물 페이지 요청 ====================
#=======================================================================

def r114SeongnamBest_request(page):
    """성남시 베스트매물 페이지들 중, 특정 페이지를 요청한다. 응답받은 HTML 문서를 String 으로 반환한다.

    Args:
        page (int, optional): Page number to request. Defaults to 1.

    Returns:
        String: Http response String.
    """

    # https://www.r114.com/?_c=memul&_m=p10 로 요청했을 때, 
    # 매물 리스트 컨테이너가 비어있는 것으로 보아 ( <ul class="list_article Best" style="display:none;"> )
    # 스크립트가 해당 컨텐츠를 동적으로 요청한다는 것을 알 수 있었습니다.
    # 따라서 브라우져 도구를 통해 스크립트가 어떤 요청을 보내는지 찾아서 해당 http 요청을 그대로 가져왔습니다. 
    # 주소
    url = 'https://www.r114.com/?_c=memul&_m=p10&_a=index.ajax'
    # 헤더
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'DNT': '1',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.r114.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.r114.com/?c=memul&m=p10&direct=A',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6',
        'Cookie': 'Memul%5FComplexNm=; Memul%5FComplexCd=; Memul%5FMemulType2=01; Memul%5FMemulStyle=0; ASPSESSIONIDCADCABAB=ACNPNLLBFKFGNIDIABFFLMKM; ACEUACS=1601380901620212205; ACEUCI2=1; _ga=GA1.2.796886702.1607175988; _gid=GA1.2.700095657.1607175988; ACEFCID=UID-5FCB8F33399F420C70EC39D1; ACEUCI=1; _fbp=fb.1.1607175988692.1088556853; nvtk=; foot_navi=opennavi; mapSize=downsize; Memul%5FTabGbn=0; __gads=ID=ae7729b33087d6ae-22d5ba9705c5007f:T=1607175999:RT=1607175999:S=ALNI_MZjFkEOKleX8PaaTOT8rDsOIx9hRw; Memul%5FCortarNo=4113000000; Memul%5FAddr=%EA%B2%BD%EA%B8%B0%EB%8F%84%7C%EC%84%B1%EB%82%A8%EC%8B%9C%7C%7C127%2E12651632305776%7C37%2E4199249073357; Memul%5FComplexCdPrev=; _ACS100397=6335; _ACU100397=1607176045601212205.1607176417626.1.0.2122056MXRPI5NZ8YRC.0.0.0.....; fCode=A; Memul%5FMemulType1=A01; _ACR0=09fa33842bf054d6ace4867b3b0fddfac8885215; _ACS100396=7731; wcs_bt=8c647232a98f8:1607178480; _ACU100396=1607175987216212205.1607178480822.1.0.212205MDTECN8BJWOBH.0.0.0.....; _gat=1'
    }
    # 포스트 바디
    body = {
        "page": page,
        "addr1": "경기도",
        "addr2": "성남시",
        "addr3": "",
        "complexCd": "" ,
        "complexTypeName": "",
        "newVilla": 0,
        "sortTag": "",
        "sortTag2": "",
        "rndValue": 775,
        "areaSize": "",
        "areaSizeType": "" 
    }

    # 요청하여 응답받은 메세지를 String 으로 바꾸고 리턴.
    res = req.post(url,headers=headers,data=body).text
    return res
    




#===================================================================================================
#==================== 성남 베스트메물 응답 메세지를 파싱하여 필요한 데이터 추출 ====================
#===================================================================================================

def r114Best_parseList(pageContent="<html></html>", memul_length=0):
    """성남시 베스트매물 페이지를 파싱한다. 매물 데이터가 담긴 리스트를 반환한다.

    Args:
        pageContent (str, optional): 성남시 베스트매물 페이지 텍스트가 담긴 String. Defaults to "<html></html>".
        memul_length (int, optional): 기존 결과 리스트의 길이. Defaults to 0.

    Returns:
        list: 한 페이지에 있는 모든 매물 데이터의 리스트
    """

    # 각 DOM 오브젝트에 대한 querySelector.
    list_selector = {
        "매물 이름" : "strong > span",
        "거래 유형" : "strong > em > span",
        "매물 가격" : "strong > em",
        "업로드 날짜" : "span.tag_comm3 > em",
        "매물 종류" : "span.txt > strong",
        "매물 세부사항" : "span.txt > span",
        "매물 설명" : "span.txt > em",
        "매물 위치 타이틀" : "span.txt > p > span",
        "매물 위치" : "span.txt > p"
    }

    # BeautifulSoup 으로 만든 DOM 객체.
    soup = BeautifulSoup(pageContent, 'html.parser')
    
    # 페이지내 리스트가 없는 경우 파싱하지 않고 빈 리스트 리턴.
    if(len(soup.select('a.cont'))==0):
        return []
    # 파싱 시작
    else:
        # 데이터를 저장할 2D 리스트 초기화
        pageData = []
        # 페이지에 있는 모든 매물 리스트를 찾음 (컨텐츠를 읽어본 결과, 각 매물 리스트의 컨텐츠는 공통적으로, .cont 클래스를 가진 <a> 부모 엘리먼트에 들어있었음)
        elementList = soup.select('a.cont')
        # .cont 는 첫 페이지에 최대 51개 존재했지만, 마지막 (51th) 엘리먼트는 어떤 템플릿 엔진 문법이 렌더되지 않고 {물건코드(제휴)} 와 같이 남아있었음.
        # 따라서 마지막 엘리먼트를 제외하기 위해 -1 한 값을 count 에 저장. 
        count = len(elementList) -1

        # count 만큼 반복.
        for j in range(count):

            # 이번 이터레이션의 엘리먼트
            currentElement = elementList[j]
            # 이번 이터레이션의 데이터를 저장할 리스트 초기화
            currentData = []

            # 매물 순위 (페이지 넘버가 2 이상인 경우를 위해, 기존 결과 리스트의 길이를 더해준다)
            currentData.append(memul_length+j+1)
            # 각 데이터를 파싱.
            currentData.append(bs4_selectAndStrip(currentElement,list_selector['매물 이름']))
            currentData.append(bs4_selectAndStrip(currentElement,list_selector['거래 유형']))
            # 해당 DOM 안의 불필요한 자식 엘리먼트를 제거.
            bs4_extractElement(currentElement,list_selector['거래 유형'])
            currentData.append(bs4_selectAndStrip(currentElement,list_selector['매물 가격']))
            currentData.append(bs4_selectAndStrip(currentElement,list_selector['업로드 날짜']))
            currentData.append(bs4_selectAndStrip(currentElement,list_selector['매물 종류']))
            # 방갯수/면적/층수가 붙어있는 스트링, 공백문자로 파싱하려했으나 구성이 규칙적이지 않아 그대로 둠. (예: 목련자영빌라 301동의 경우, 방갯수가 없고, 면적/층수밖에 없음.)
            currentData.append(bs4_selectAndStrip(currentElement,list_selector['매물 세부사항']))
            currentData.append(bs4_selectAndStrip(currentElement,list_selector['매물 설명']))
            # 해당 DOM 안의 불필요한 자식 엘리먼트를 제거.
            bs4_extractElement(currentElement,list_selector['매물 위치 타이틀'])
            currentData.append(bs4_selectAndStrip(currentElement,list_selector['매물 위치']))
            
            # 이번 이터레이션의 데이터를 이번 페이지 리스트에 추가
            pageData.append(currentData)

        # 이번 페이지 리스트 리턴
        return pageData





#=====================================================
#==================== 메인 메소드 ====================
#=====================================================

if __name__ == "__main__":

    # 크롤링 옵션 변수들
    # csv 파일 절대경로
    csvPath = ''
    # 크롤링할 페이지수
    maxPage = 0

    #-------------------------------------------------------
    #-------------------- CLI 옵션 설정 --------------------
    #-------------------------------------------------------

    #-------------------- 도움말 출력 --------------------
    helpText = '''
    CLI Options
    -h      : print this help
    -f      : absolute path of DIRECTORY to save a csv file. (String) 
              [ Notice ] Do not include a file name.
              [ Notice ] Do not include a non-existing subdirectory.
    -m      : a number of pages to crawl (Int)
    '''
    # -h 옵션이 있으면 도움말 덱스트 프린트
    if '-h' in argv:
        print(helpText)
        exit()


    #-------------------- args 파싱 --------------------
    # 파일명을 제외한 argv 반복
    for i in range(1,len(argv)):
        # 옵션 플래그를 찾음, 바로 다음에 arg 가 있는지 검사 (try/catch) (옵션 플래그 없이 주어진 arg 는 무시)
        if('-' in argv[i]):
            try:
                argv[i+1]
            except:
                print('\n    option without parameter')
                print(helpText)
                exit()
            else:
                # 바로 다음에 있는 arg 가 또 다른 옵션인지 검사 (try/catch)
                if('-' in argv[i+1]):
                    print('\n    option without parameter')
                    print(helpText)
                    exit()
                else:
                    # 옵션 플래그가 -f -m 중 하나인지 확인
                    if(argv[i] in ['-f','-m']):
                        # 옵션 플래그가 -f 이면, 패러미터를 csvPath 에 저장 (경로가 잘못된 경우는 file 모듈에서 예외처리해줄 것임)
                        if(argv[i] == '-f'):
                            csvPath = Path.joinpath(Path(argv[i+1]), datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3]+'.csv')
                        # 옵션 플래그가 -m 이면, 패러미터를 int 파싱할수 있는지 검사 (try/catch), 가능하면 maxPage 에 저장.
                        if(argv[i] == '-m'):
                            try:
                                int(argv[i+1])
                            except:
                                print('\n    maxPage has to be integer')
                                print(helpText)
                                exit()
                            else:
                                maxPage = int(argv[i+1])
                    # -f -m 이외에 유효하지 않은 옵션 플래그인 경우 처리.
                    else:
                        print('\n    unknown option',argv[i],argv[i+1])
                        print(helpText)
                        exit()
                


    #-----------------------------------------------------------------------------
    #-------------------- CLI 옵션이 없는 경우 기본 옵션 설정 --------------------
    #-----------------------------------------------------------------------------

    if(csvPath==''):
        # csv 파일이 저장될 디렉토리 mkdir. (스크립트경로/r114SeongnamBest) 
        if not Path.joinpath(Path.cwd(),'result').exists():
            Path.mkdir(Path.joinpath(Path.cwd(),'result'))
        
        # 파일명은 milliseconds 3자리를 포함한 시간 스트링을 사용.
        timeStamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3]
        
        # 완성된 경로.
        csvPath = Path.joinpath(Path.cwd(),'result',timeStamp+'.csv')

    if(maxPage==0):
        # 파싱할 페이지수 지정.
        maxPage = 1



    #------------------------------------------------
    #-------------------- 크롤링 --------------------
    #------------------------------------------------

    while True:

        #-------------------- 타이머 시작 --------------------

        timeStamp_start = datetime.now()

        #-------------------- 매물 리스트 얻기 --------------------

        # csv 데이터를 담을 리스트.
        memul = [
            [
                "순위",
                "매물 이름",
                "거래 유형",
                "가격",
                "업로드 날짜",
                "매물 유형",
                "매물 세부사항 (방갯수/면적/층수)",
                "상세 설명",
                "위치"
            ]
        ]

        # maxPage 만큼 반복하며 요청+파싱.
        for pageNumber in range(1,maxPage+1):
            print(pageNumber,'/',maxPage,'페이지 크롤링 중 ...')
            pageHTMLString = r114SeongnamBest_request(pageNumber)
            pageMemulList = r114Best_parseList(pageHTMLString, len(memul))
            # 마지막 페이지 파싱이 끝난 경우, 반복 중단
            if(pageMemulList == []):
                print(pageNumber,'요청한 모든 페이지 크롤링 완료 !')
                break
            memul += pageMemulList

        #-------------------- CSV 파일 쓰기 --------------------
        
        with open(csvPath, 'w', newline='\r\n') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(memul)

        #-------------------- 타이머 끝 --------------------

        timeStamp_end = datetime.now()

        #-------------------- 결과 프린트 --------------------

        print(f'''
        웹사이트 주소:          https://www.r114.com/?_c=memul&_m=p10&_a=index.ajax
        크롤링 결과 csv 경로:   '{csvPath}'
        크롤링한 총 페이지 수:  {maxPage} 페이지
        클롤링한 총 매물 수:    {len(memul)} 개
        소요 시간:              {(timeStamp_end - timeStamp_start).total_seconds()} 초
        시작 시간:              {timeStamp_start.strftime('%Y년 %m월 %d일 %H시 %M분 %S초 %f')}
        완료 시간:              {timeStamp_end.strftime('%Y년 %m월 %d일 %H시 %M분 %S초 %f')}    
        ''')

        #-------------------- 계속하시겠습니까? --------------------

        userInput_continue = input('계속하시겠습니까? [네/아니오]  ')
        if(userInput_continue in ['네','아니오']):
            if(userInput_continue == '네'):
                continue
            if(userInput_continue == '아니오'):
                print('안녕히 가십시오')
                exit()
        else:
            print('네/아니오 중 하나만 입력 가능합니다.')
            exit()
            
        