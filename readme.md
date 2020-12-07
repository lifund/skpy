# 프로그래밍입문 기말과제

## 학생정보
- 서장원
- 영상학과
- 2014314580

---

## 추가 기능
1. CLI arguments 로 다음과 같은 크롤링 옵션을 설정할 수 있습니다.

   - -m : 크롤링할 총 페이지수 설정
     * 1000 을 전댈해본 결과, 성남시 인기 매물 페이지는 총 200페이지 입니다. (12월 7일 기준)
     * 페이지당 응답속도가 1초 이내로 짧습니다. 크롤링이 막히는 상황을 피하기 위해서는 연속적인 사용을 피해야할듯 합니다.

   - -f : csv 파일을 저장할 경로
     * 파일명을 제외한 절대경로를 받습니다.
     * 존재하지 않는 디렉토리는 전달할 수 없습니다.
   
   - ( -h 플래그를 전달하면 CLI 인터페이스 사용에 대한 도움말을 볼 수 있습니다. )
  
---

## 미리 정의한 함수

### bs4 shorthands
```python
1. def bs4_selectAndStrip (parentElement=BeautifulSoup("<html></html>", 'html.parser'),selector=""):
```
   - bs4 DOM 객체와, querySelector 을 받습니다. 
   - 해당되는 객체를 찾습니다.
   - 해당 객체의 .text 컨텐츠를 .strip() 하고, \r \n \r\n 을 공백 문자로 대체해서 리턴합니다.
```python
2. def bs4_extractElement (parentElement=BeautifulSoup("<html></html>", 'html.parser'),selector=""):
```
   - bs4 DOM 객체와, querySelector 을 받습니다.
   - 해당되는 객체를 찾습니다.
   - .extract() 메소드를 이용하여, 전달받은 객체에서 찾은 자손을 제거합니다.
   - .extract() 메소드는 기존 객체를 수정합니다.

### key functions
```python
1. def r114SeongnamBest_request(page):
```
   - 요청할 페이지 넘버(page)를 받아, 성남시 베스트매물 사이트에 해당하는 페이지를 요청합니다.
   - 응답 메세지를 String 으로 리턴합니다.
```python
1. def r114Best_parseList(pageContent="<html></html>", memul_length=0):
```
   - 성남시 베스트매물 페이지 String 컨텐츠(pageContent)를 받아,
   - bs4 를 이용해 DOM 객체를 만들고,
   - 필요한 데이터를 파싱하여,
   - 각 매물의 데이터 List 가 들어있는 2D List 를 리턴합니다. 

---

## main 루틴

아래 모든 코드는 while True 루틴에 들어있습니다.
1. 전달된 CLI 인풋을 파싱하여, -m 혹은 -f 옵션이 있으면, 각각 maxPage 와 csvPath 변수에 저장합니다.
2. 전달된 CLI 옵션이 없으면, 디폴트 옵션을 설정합니다.
    *타이머 시작*
3. maxPage 만큼 반복하며,
   - 각 페이지의 매물 데이터 리스트를, memul 변수에 저장합니다.
4. csvPaht 에 csv 파일을 씁니다.
    *타이머 끝*
5. 결과를 커멘드라인에 출력합니다.
6. 유저 인풋을 받아, 
   - '예' 이면 continue 를
   - '아니오' 이면 인사 후 sys.exit() 을
   - 그 외의 것이면 잘못된 입력임을 알려준 후 sys.exit() 을 실행합니다. 
