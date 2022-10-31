# %%
#Pyqt 관련 import
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic

#파싱 관련 import
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import datetime
from bs4 import BeautifulSoup
import re


# %%
class Paper:
    def __init__(self):
        self.paperName = 'name'
        self.paperID = 'ID'
        self.course = 'course'
        self.deadline = 'deadline'
        self.summit = 'summit'
        self.important = False
    
    #Paper의 정보를 입력하는 메소드
    def InputPaperInfo(self, name, ID, course, deadline, summit):
        self.paperName = name
        self.paperID = ID
        self.course = course
        self.deadline = deadline
        self.summit = summit
    
    #Paper의 정보를 출력하는 메소드
    def GetPaperName(self):
        return self.paperName
    
    def GetPaperID(self):
        return self.paperID
    
    def GetPaperCourse(self):
        return self.course
    
    def GetPaperDeadline(self):
        return self.deadline
    
    def GetPaperSummit(self):
        return self.summit
    
    def GetPaperImportant(self):
        return self.important
    
    #Paper의 중요 표시를 설정하는 메소드
    def MakePaperImportant (self):
        self.Important = True
    
    #Paper의 중요 표시를 해제하는 메소드
    def MakePaperUnimportant (self):
        self.Important = False

class course:
    def __init__(self):
        self.courseID = 0
        self.courseName = 'course'
        self.paperList = []        
    
    def inputCourseInfo(self, name, ID, paperList):
        self.courseID = ID
        self.courseName = name
        self.course = paperList

class TotalPaperList:
    def __init__(self):
        self.totalList = []
        self.unimportantList = []
        self.importantList = []
    
    def MakeImportant(self, paperID):
        for paper in self.totalPaperList:
            if paper.paperID == paperID:
                self.importantList.append(paper)
                self.unimportantList.remove(paper)
                break
        self.sortImportantList()
        for paper in self.totalList:
            if paper.getPaperID() == paperID:
                paper.makeImportant()
    
    #과제를 일반 과제로 설정하고, 일반 과제 리스트에 추가하는 메소드
    def MakeUnimportant(self, paperID):
        for paper in importantList:
            if paper.paperID == paperID:
                totalList.append(paper)
                importantList.remove(paper)
                break
        self.sortTotalList()
        for paper in totalList:
            if paper.getPaperID() == paperID:
                paper.makeUnimportant()
    
    def UpdateList(self):
        for paper in self.totalList:
            if paper.GetPaperImportant():
                self.ImportantList.append(paper)
            else:
                self.unimportantList.append(paper)
            
            
    def UpdatePaper(self, driver, Url):
        driver.get(Url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        #과목 리스트 생성
        title_list = soup.find_all('a', 'course_link')

        for title in title_list:
            #과목 생성 및 이름, ID 저장
            addr = title.get('href')
            courseNameData = title.text
            sidx = courseNameData.find('부')
            eidx = courseNameData.find('[')
            courseName = courseNameData[sidx+1:eidx]
            courseID_arr = re.findall("\d+", addr)
            courseID = courseID_arr[0]
            
            #과제 확인 및 미제출 과제를 리스트에 추가
            paper_default = 'https://uclass.uos.ac.kr/mod/assign/index.php?id='
            paper_home = paper_default + courseID
            driver.get(paper_home)
            html_paper = driver.page_source
            soup = BeautifulSoup(html_paper, 'lxml')                    
            for data in soup.find_all('td', attrs = {"class":"cell c3"}):
                #과제 제출 여부가 미제출인 과제를 추출하여 등록
                if data.text != '제출 완료':
                    
                    #과제 생성 및 이름, ID 저장
                    newPaper = Paper()
                    newPaper.summit = data.text
                    paperName = data.find_previous_sibling('td', attrs = {"class":"cell c1"}).text
                    paperID_data = data.find_previous_sibling('td', attrs = {"class":"cell c1"}).find('a')
                    paperID = re.findall("\d+", paperID_data.get('href'))[0]
                    
                    #제출 기한 계산 및 저장
                    deadline = []
                    data_deadline = data.find_previous_sibling('td', attrs = {"class":"cell c2"})
                    date = re.findall("\d+", data_deadline.text)
                    index = 0
                    for time in date:
                        deadline.append(date[index])
                        index += 1
                    if len(deadline[2]) == 1:
                        deadline[2] = '0' + deadline[2]
                    
                    summit = data.text
                    #이미 있는 과제의 경우, 해당 과제에 덮어쓰고 마무리
                    #없을 경우(덮어쓰지 않고 마지막까지 오면) 새로운 과제로 추가
                    newPaper.InputPaperInfo(paperName, paperID, courseName, deadline, summit)
                    self.totalList.append(newPaper)

    

class UserData:
    def __init__(self):
        self.userID = ''
        self.userPW = ''
        self.loginUrl = 'https://uclass.uos.ac.kr/login.php'
        self.mainUrl = 'https://uclass.uos.ac.kr/'
        self.totalList = TotalPaperList()
        self.startWeb()
        
    def startWeb(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options = options)
        self.driver.get(self.loginUrl)
    
    def Login(self, ID, PW):
        if ID == '' or PW == '':
            return '아이디와 비밀번호는 반드시 입력해야 합니다.'
        
        sleep(0.5)
        self.driver.find_element_by_name('username').send_keys(ID)
        sleep(0.5)
        self.driver.find_element_by_name('password').send_keys(PW)
        
        self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div/div/div[1]/div[1]/div[2]/form/div[2]/input').click()
        
        if self.driver.current_url == self.mainUrl:
            userID = ID
            userPW = PW
            return 'success'
        else:
            errorCode = re.findall("\d+", self.driver.current_url)
            if errorCode[0] == '1':
                return '현재, 브라우저의 쿠키가 작동하지 않습니다.'
            elif errorCode[0] == '2':
                return '사용자 아이디 : 아이디에는 영어소문자, 숫자, 밑줄( _ ), 하이폰( - ), 마침표( . ) 또는 @ 기호만 쓸 수 있습니다.'
            elif errorCode[0] == '3':
                return '아이디 또는 패스워드가 잘못 입력되었습니다.'

# %%
form_class = uic.loadUiType("sicheduler.ui")[0]


class Ui(QMainWindow, form_class): ##JK 12050400
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.UserData = UserData()
        self.pushButton_login.clicked.connect(self.login)
        
#         self.assignmentWidget()
#         self.assignmentList()

#     def assignmentList(self):
#         a = ["1", "2", "3", "4"]
#         model = QStandardItemModel()
#         for x in a:
#             model.appendRow(QStandardItem(x))
#         self.listView_0.setModel(model)
    
    def login(self):
        print(self.inputId.text())
        msg = self.UserData.Login(self.inputId.text(), self.inputPassword.text())
        print(msg)
        if msg == 'success':
            self.stackedWidget.setCurrentIndex(1)
            #0,0 셀 데이터 설정
            self.tableWidget.setItem(0,0,QTableWidgetItem('하나'))
            self.downloading()

    def assignmentWidget(self):
        a = QListWidgetItem(QIcon("./icon.png"), "1234") # 각각 (setIcon, setText)로 수정 가능
        print(a.sizeHint())
        self.listWidget.addItem(a)
    
    def downloading(self):
        self.checkBox = []
        self.pushButton = []
        
        print("11")
        
        self.tableWidget.setColumnWidth(0, 150)
        self.tableWidget.setColumnWidth(1, 250)
        self.tableWidget.setColumnWidth(2, 150)
        self.tableWidget.setColumnWidth(3, 100)
        self.tableWidget.setColumnWidth(4, 50)
        self.tableWidget.setColumnWidth(5, 10)
        self.tableWidget_2.setColumnWidth(0, 150)
        self.tableWidget_2.setColumnWidth(1, 250)
        self.tableWidget_2.setColumnWidth(2, 150)
        self.tableWidget_2.setColumnWidth(3, 100)
        self.tableWidget_2.setColumnWidth(4, 50)
        self.tableWidget_2.setColumnWidth(5, 10)
        self.UserData.totalList.UpdatePaper(self.UserData.driver, self.UserData.mainUrl)
        self.UserData.totalList.UpdateList()
        row = 0
        print(len(self.UserData.totalList.unimportantList))
        for paper in self.UserData.totalList.importantList:
            name = paper.GetPaperName()
            course = paper.GetPaperCourse()
            deadline = '. '.join(paper.GetPaperDeadline())
            summit = paper.GetPaperSummit()
            globals()['chbox_{}'.format(row)] = QCheckBox()
            globals()['pbutton_{}'.format(row)] = QPushButton("...")
            self.checkBox.append(globals()['chbox_{}'.format(row)])
            self.pushButton.append(globals()['pbutton_{}'.format(row)])
            self.tableWidget.setRowCount(row+1)
            self.tableWidget.setItem(row,0,QTableWidgetItem(name))
            self.tableWidget.setItem(row,1,QTableWidgetItem(course))
            self.tableWidget.setItem(row,2,QTableWidgetItem(deadline))
            self.tableWidget.setItem(row,3,QTableWidgetItem(summit))
            self.tableWidget.setCellWidget(row,4,self.pushButton[row])
            self.tableWidget.setCellWidget(row,5,self.checkBox[row])
            print(row)
            row += 1
        print('22')
        print(row)
        row = 0
        for paper in self.UserData.totalList.unimportantList:
            name = paper.GetPaperName()
            course = paper.GetPaperCourse()
            deadline = '. '.join(paper.GetPaperDeadline())
            summit = paper.GetPaperSummit()
            globals()['chbox_{}'.format(row)] = QCheckBox()
            globals()['pbutton_{}'.format(row)] = QPushButton("...")
            self.checkBox.append(globals()['chbox_{}'.format(row)])
            self.pushButton.append(globals()['pbutton_{}'.format(row)])
            self.tableWidget_2.setRowCount(row+1)
            self.tableWidget_2.setItem(row,0,QTableWidgetItem(name))
            self.tableWidget_2.setItem(row,1,QTableWidgetItem(course))
            self.tableWidget_2.setItem(row,2,QTableWidgetItem(deadline))
            self.tableWidget_2.setItem(row,3,QTableWidgetItem(summit))
            self.tableWidget_2.setCellWidget(row,4,self.pushButton[row])
            self.tableWidget_2.setCellWidget(row,5,self.checkBox[row])
            print(row)
            row += 1
        print("33")
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    currentUi = Ui()
    currentUi.show()
    sys.exit(app.exec_())


# 리소스 변경 시마다 터미널창에 입력
# pyrcc5 resource.qrc -o resource_rc.py

# 실행파일로 만들기
# pyinstaller -w -F main.py


# %%
# %%