#UI 관련 import
from enum import auto
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
import random
import pickle
import os

#과제 클래스
class Paper:
    def __init__(self):
        self._paperName = 'name'
        self._paperID = 'ID'
        self._course = 'course'
        self._deadline = 'deadline'
        self._summit = 'summit'
        self._info = 'info'
        self._important = False
    
    #Paper의 정보를 입력하는 메소드
    def InputPaperInfo(self, name, ID, course, deadline, summit, info):
        self._paperName = name
        self._paperID = ID
        self._course = course
        self._deadline = deadline
        self._summit = summit
        self._info = info
    
    #Paper의 정보를 출력하는 메소드    
    def GetPaperData(self):
        return self._paperName, self._paperID, self._course, self._deadline, self._summit, self._info
    
    #과제이름
    def GetPaperName(self):
        return self._paperName
    
    #과제 ID값
    def GetPaperID(self):
        return self._paperID
    
    #강의 이름
    def GetPaperCourse(self):
        return self._course
    
    #과제 제출 기한
    def GetPaperDeadline(self):
        return self._deadline
    
    #과제 제출여부
    def GetPaperSummit(self):
        return self._summit
    
    #과제 세부정보
    def GetPaperInfo(self):
        return self._paperName, self._paperID, self._course, self._deadline, self._summit, self._info
    
    #과제 중요여부 확인
    def GetPaperImportant(self):
        return self._important
    
    #Paper의 중요 표시를 설정하는 메소드
    def MakePaperImportant (self):
        self._important = True
    
    #Paper의 중요 표시를 해제하는 메소드
    def MakePaperUnimportant (self):
        self._important = False

#전체 과제 클래스 
class TotalPaperList:
    def __init__(self):
        self._totalList = []
        self._unimportantList = []
        self._importantList = []
        self._alarmList = []
        self._needAlarm = 0
        self._alarmSet = [0, 1, 0, 0]
    
    #인터넷에서 과제 내용 업데이트
    def UpdatePaper(self, driver, Url):
        self._alarmList = []
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
            paperHomeBase = 'https://uclass.uos.ac.kr/mod/assign/index.php?id='
            paperHome = paperHomeBase + courseID
            driver.get(paperHome)
            htmlPaper = driver.page_source
            soup = BeautifulSoup(htmlPaper, 'lxml')                    
            for data in soup.find_all('td', attrs = {"class":"cell c3"}):
                #과제 제출 여부가 미제출인 과제를 추출하여 등록
                if data.text != '제출 완료':
                    
                    #과제 생성 및 이름, ID 저장
                    paperName = data.find_previous_sibling('td', attrs = {"class":"cell c1"}).text
                    paperIDData = data.find_previous_sibling('td', attrs = {"class":"cell c1"}).find('a')
                    paperID = re.findall("\d+", paperIDData.get('href'))[0]
                    #제출 기한 계산 및 저장
                    deadline = []
                    deadlineData = data.find_previous_sibling('td', attrs = {"class":"cell c2"})
                    date = re.findall("\d+", deadlineData.text)
                    for idx in range(0, len(date)):
                        deadline.append(date[idx])
                    
                    if len(deadline[2]) == 1:
                        deadline[2] = '0' + deadline[2]
                    
                    summit = data.text
                    paperUrl = 'https://uclass.uos.ac.kr/mod/assign/view.php?id=' + paperID
                    driver.get(paperUrl)
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'lxml')
                    sub = soup.find_all('div', attrs = {"class":"no-overflow"})
                    if len(sub):
                        info = sub[0].text
                    else:
                        info = ''
                    #이미 있는 과제의 경우, 해당 과제에 덮어쓰고 마무리
                    #없을 경우(덮어쓰지 않고 마지막까지 오면) 새로운 과제로 추가
                    if len(self._totalList) == 0:
                        newPaper = Paper()
                        newPaper.InputPaperInfo(paperName, paperID, courseName, deadline, summit, info)
                        self._totalList.append(newPaper)
                    else:
                        for idx in range(0, len(self._totalList)):
                            if paperID == self._totalList[idx].GetPaperID():
                                self._totalList[idx].InputPaperInfo(paperName, paperID, courseName, deadline, summit, info)
                                break
                            
                            if idx == len(self._totalList)-1:
                                newPaper = Paper()
                                newPaper.InputPaperInfo(paperName, paperID, courseName, deadline, summit, info)
                                self._totalList.append(newPaper)

    #과제 리스트 업데이트
    def UpdateList(self):
        self._importantList = []
        self._unimportantList = []
        for paper in self._totalList:
            if paper.GetPaperImportant() == True:
                self._importantList.append(paper)
            else:
                self._unimportantList.append(paper)

    #과제를 중요 과제로 설정하고, 중요 과제 리스트에 추가하는 메소드
    def MakeImportant(self, paperID):
        for paper in self._totalList:
            if paper.GetPaperID() == paperID:
                paper.MakePaperImportant()
    
    #과제를 일반 과제로 설정하고, 일반 과제 리스트에 추가하는 메소드
    def MakeUnimportant(self, paperID):
        for paper in self._totalList:
            if paper.GetPaperID() == paperID:
                paper.MakePaperUnimportant()
    
    #과제 수동 추가
    def AddPaper(self, paper):
        self._totalList.append(paper)

    #과제 삭제
    def DeletePaper(self, paperID):
        for paper in self._totalList:
            if paper.GetPaperID() == paperID:
                self._totalList.remove(paper)
    
    #과제 제출까지 남은시간 계산      
    def CalculateTime(self,startTime,endTime):
        remainTime = endTime-startTime
        remainDays = remainTime.days
        remainHours = remainTime.seconds//3600
        remainMinutes = remainTime.seconds//60-remainHours*60
        remainSeconds = remainTime.seconds-remainHours*3600-remainMinutes*60
        remainTimes = [remainDays,remainHours,remainMinutes,remainSeconds]
        return remainTimes

    #남은시간과 알람시간을 비교하여 알람을 울림
    def CheckAlarm(self):
        self._needAlarm = 0
        for paper in self._totalList:
            deadline = paper.GetPaperDeadline()
                    #alarm default = 1hour
                    #[일, 시, 분, 초]
            alarmZero = [0 ,0 ,0 ,0] 
            startTime = datetime.datetime.now()
            endTime = datetime.datetime(int(deadline[0]),int(deadline[1]),int(deadline[2]),int(deadline[3]),int(deadline[4]))
            remainTimes = self.CalculateTime(startTime,endTime)
            #알람 시간보다 과제 남은 시간이 작으면 알람을 울림
            if alarmZero < remainTimes < self._alarmSet :
                courseName = paper.GetPaperCourse()
                paperName = paper.GetPaperName()
                self._needAlarm += 1
                alarmData = [courseName, paperName, endTime]
                self._alarmList.append(alarmData)
                print(self._needAlarm)
            
    #사용자 지정 알람시간 획득
    def GetAlarmSet(self):
        return self._alarmSet

    #과제란 초기화
    def ClearList(self):
        self._totalList = []
        self._importantList = []
        self._unimportantList = []
        self._alarmSet = [0, 1, 0, 0]
                
    #과제 ID 비교
    def CheckID(self, paperID):
        for paper in self._totalList:
            if paperID == paper.GetPaperID():
                return True
        return False

    #알람 시간 설정
    def SetAlarm(self, alarmSetting):
        self._alarmSet = alarmSetting
    
    #알람 한번 울린후 처리
    def ClearAlarm(self):
        self._needAlarm -= 1
    
    #울려야하는 알람의 정보 확인
    def GetAlarmData(self):
        return self._alarmList.pop()

    #중요과제목록 확인
    def GetImportantList(self):
        return self._importantList
    
    #일반과제목록 확인
    def GetUnimportantList(self):
        return self._unimportantList

    #필요 알람의 개수 확인
    def IsAlarm(self):
        return self._needAlarm

#사용자 정보    
class UserData:
    def __init__(self):
        self._userID = ''
        self._userPW = ''
        self._loginUrl = 'https://uclass.uos.ac.kr/login.php'
        self._mainUrl = 'https://uclass.uos.ac.kr/'
        self._totalList = TotalPaperList()
        self.StartWeb()
    
    #인터넷 접속
    def StartWeb(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self._driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options = options)
        self._driver.get(self._loginUrl)
    
    #사용자 로그인 
    def Login(self, ID, PW):
        if ID == '' or PW == '':
            return '아이디와 비밀번호는 반드시 입력해야 합니다.'
        
        self._driver.get(self._loginUrl)
        self._driver.find_element_by_name('username').send_keys(ID)
        self._driver.find_element_by_name('password').send_keys(PW)
        self._driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div/div/div[1]/div[1]/div[2]/form/div[2]/input').click()
        
        if self._driver.current_url == self._mainUrl:
            self._userID = ID
            self._userPW = PW
            return 'success'
        else:
            errorCode = re.findall("\d+", self._driver.current_url)
            if errorCode[0] == '1':
                return '현재, 브라우저의 쿠키가 작동하지 않습니다.'
            elif errorCode[0] == '2':
                return '사용자 아이디 : 아이디에는 영어소문자, 숫자, 밑줄( _ ), 하이폰( - ), 마침표( . ) 또는 @ 기호만 쓸 수 있습니다.'
            elif errorCode[0] == '3':
                return '아이디 또는 패스워드가 잘못 입력되었습니다.'
    
    #로그아웃
    def Logout(self):
        self._totalList.ClearList()
        self._driver.get(self._mainUrl)
        self._driver.find_element_by_xpath('/html/body/div[3]/div[1]/nav/div/div[2]/ul/li[8]/a').click()#웹상 로그아웃
    
    #과제 불러오기 + 업데이트
    def Update(self):
        self._totalList.UpdatePaper(self._driver, self._mainUrl)
        self._totalList.UpdateList()      
    
    #과제 리스트 업데이트
    def UpdateList(self):
        self._totalList.UpdateList()
    
    #중요과제 확인
    def GetImportantList(self):
        return self._totalList.GetImportantList()
    
    #일반과제 확인
    def GetUnimportantList(self):
        return self._totalList.GetUnimportantList()

    #필요알람개수 확인
    def IsAlarm(self):
        return self._totalList.IsAlarm()
    
    #울려야하는 알람의 정보 확인
    def GetAlarmData(self):
        return self._totalList.GetAlarmData()

    #알람 한번 울린후 처리
    def ClearAlarm(self):
        self._totalList.ClearAlarm()
    
    #사용자 지정 알람시간 획득
    def GetAlarmSet(self):
        return self._totalList.GetAlarmSet()

    #과제 삭제
    def DeletePaper(self, paperID):
        self._totalList.DeletePaper(paperID)

    #알람 시간 설정
    def SetAlarm(self, alarmSetting):
        self._totalList.SetAlarm(alarmSetting)

    #입력한 과제를 중요과제로 지정
    def MakeImportant(self, paperID):
        self._totalList.MakeImportant(paperID)

    #입력한 과제를 일반과제로 지정
    def MakeUnimportant(self, paperID):
        self._totalList.MakeUnimportant(paperID)

    #과제 ID 확인
    def CheckID(self, paperID):
        return self._totalList.CheckID(paperID)

    #알람 필요여부 확인하고 울리기
    def CheckAlarm(self):
        self._totalList.CheckAlarm()

    #과제 추가
    def AddPaper(self, paper):
        self._totalList.AddPaper(paper)
    

#UI 부분
formClass = uic.loadUiType("sicheduler.ui")[0]
class Ui(QMainWindow, formClass): ##JK 12050400
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.userData = UserData()
        self.loginCount = 0
        self.currentPaper = ''
        self.AutoLogin()
        self.StartSetting()
        
    
    def StartSetting(self):
        #버튼 관련 함수 연결
        self.lineEdit_inputPassword.returnPressed.connect(self.Login)
        self.pushButton_login.clicked.connect(self.Login)
        self.pushButton_newAssignment.clicked.connect(self.NewPaper)
        self.pushButton_info_return.clicked.connect(self.ReturnHome)
        self.pushButton_add_return.clicked.connect(self.ReturnHome)
        self.pushButton_setting_return.clicked.connect(self.ReturnHome)
        self.pushButton_setting.clicked.connect(self.Setting)
        self.pushButton_refresh.clicked.connect(self.Refresh)
        self.pushButton_addPaper.clicked.connect(self.AddPaper)
        self.pushButton_set_alarm.clicked.connect(self.SetAlarmTime)
        self.pushButton_logout.clicked.connect(self.Logout)
        self.pushButton_delete.clicked.connect(self.DeletePaper)
        self.checkBox_autoLogin.stateChanged.connect(self.SetAutoLogin)

        #과제를 출력할 테이블 크기 설정
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
    
    #로그아웃 기능
    def Logout(self):
        quitMessage = "로그아웃 하시겠습니까?"
        reply = QMessageBox.question(self, 'Message', quitMessage, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.autoLogin = 0
            self.loginCount = 0
            self.SaveUserData()
            self.userData.Logout()
            self.lineEdit_inputId.clear()
            self.lineEdit_inputPassword.clear()
            self.stackedWidget.setCurrentIndex(0)

    #프로그램 종료
    def closeEvent(self, event):
        if self.stackedWidget.currentIndex() == 0:
            event.accept()
        else:
            quitMessage = "과제 리스트를 저장하고 종료하시겠습니까?"
            reply = QMessageBox.question(self, 'Message', quitMessage, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.SaveUserData()
                event.accept()
            else:
                event.accept()    
    
    #자동로그인
    def SetAutoLogin(self):
        sender = self.sender()
        if sender.isChecked():
            self.autoLogin = 1
        else:
            self.autoLogin = 0
    
    #사용자정보 저장
    def SaveUserData(self):
        with open('log.p','wb')as file:
            pickle.dump(self.autoLogin,file)
            pickle.dump(self.userData._userID,file)
            pickle.dump(self.userData._userPW,file)
            pickle.dump(self.userData._totalList,file)
        
    #과제 추가
    def AddPaper(self):
        course = self.textEdit_course.toPlainText().strip()
        paperName = self.textEdit_name.toPlainText().strip()
        paperID = str(random.randint(10000, 99999))
        while(self.userData.CheckID(paperID)):
            paperID = str(random.randint(10000,99999))
        deadline = ['','','','','']
        deadline[0] = str(self.spinBox_year.value())
        deadline[1] = str(self.spinBox_month.value())
        deadline[2] = str(self.spinBox_day.value())
        deadline[3] = str(self.spinBox_hour.value())
        deadline[4] = str(self.spinBox_minute.value())
        summit = self.textEdit_summit.toPlainText().strip()
        info = self.textEdit_more.toPlainText()
        if course == '' or paperName == '' or summit == '':
            msg = '정보가 부족합니다.\n과목 이름, 과제 이름, 제출 여부는 반드시 포함되어야 합니다.'
            QMessageBox.about(self,"과제 추가 실패",msg)
            return 0
        newPaper = Paper()
        newPaper.InputPaperInfo(paperName, paperID, course, deadline, summit, info)
        self.userData.AddPaper(newPaper)
        self.userData.UpdateList()
        self.PrintPaperList()
        self.ReturnHome()
   
    #자동로그인
    def AutoLogin(self):
        print("autologin process starts...")
        if os.path.exists('log.p') and os.path.getsize('log.p')>0 :
            with open('log.p','rb') as file:
                autoLogin = pickle.load(file)
            if autoLogin:
                with open('log.p','rb') as file:
                    self.autoLogin=pickle.load(file)
                    ID1 = pickle.load(file)
                    PW1 = pickle.load(file)
                    self.userData._totalList = pickle.load(file)
                    print("autologin almost there...")
                self.lineEdit_inputId.setText(ID1)
                self.lineEdit_inputPassword.setText(PW1)    
                self.Login()
                    
        else :
            print("auto login exception occured")
    
    #일반 로그인
    def Login(self):
        self.autoLogin = 0
        print('login process starts...')
        msg = self.userData.Login(self.lineEdit_inputId.text(), self.lineEdit_inputPassword.text())
        print(msg)
        if msg == 'success':
            if os.path.exists('log.p') and os.path.getsize('log.p')>0:
                with open('log.p','rb') as file:
                    autoLogin = pickle.load(file)
                    ID1 = pickle.load(file)
                    PW1 = pickle.load(file)
                    PastList = pickle.load(file)
                if (ID1 == self.lineEdit_inputId.text() and PW1 == self.lineEdit_inputPassword.text()):
                    self.autoLogin = autoLogin
                    self.userData._totalList = PastList

            self.stackedWidget.setCurrentIndex(1)
            self.userData.Update()
            self.PrintPaperList()
            self.CheckAlarm()
        else:
            if self.loginCount == 4:
                quitMessage = '로그인을 5회 실패하였습니다.'
                reply = QMessageBox.question(self, '로그인 실패', quitMessage, QMessageBox.Ok)
                if reply == QMessageBox.Ok:
                    exit()
            else:
                errorMsg = '실패 사유: ' + msg +'\n로그인 5회 실패 시 종료됩니다.'
                QMessageBox.about(self,"로그인 실패",errorMsg)
                self.loginCount+=1
   
    #과제란 과제 출력
    def PrintPaperList(self):
        importantList = self.userData.GetImportantList()
        unimportantList = self.userData.GetUnimportantList()
        self.importantCheckBox = []
        self.importantPushButton = []
        self.unimportantCheckBox = []
        self.unimportantPushButton = []
        
        #과제목록란 상단바
        self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem('과목 이름'))
        self.tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem('과제 이름'))
        self.tableWidget.setHorizontalHeaderItem(2, QTableWidgetItem('제출 기한'))
        self.tableWidget.setHorizontalHeaderItem(3, QTableWidgetItem('제출 여부'))
        self.tableWidget.setHorizontalHeaderItem(4, QTableWidgetItem('자세히'))
        self.tableWidget.setHorizontalHeaderItem(5, QTableWidgetItem('★'))

        self.tableWidget_2.setHorizontalHeaderItem(0, QTableWidgetItem('과목 이름'))
        self.tableWidget_2.setHorizontalHeaderItem(1, QTableWidgetItem('과제 이름'))
        self.tableWidget_2.setHorizontalHeaderItem(2, QTableWidgetItem('제출 기한'))
        self.tableWidget_2.setHorizontalHeaderItem(3, QTableWidgetItem('제출 여부'))
        self.tableWidget_2.setHorizontalHeaderItem(4, QTableWidgetItem('자세히'))
        self.tableWidget_2.setHorizontalHeaderItem(5, QTableWidgetItem('★'))
        
        #중요과제란 출력
        row = 0
        if len(importantList) == 0:
            self.tableWidget.clear()
            self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem('과목 이름'))
            self.tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem('과제 이름'))
            self.tableWidget.setHorizontalHeaderItem(2, QTableWidgetItem('제출 기한'))
            self.tableWidget.setHorizontalHeaderItem(3, QTableWidgetItem('제출 여부'))
            self.tableWidget.setHorizontalHeaderItem(4, QTableWidgetItem('자세히'))
            self.tableWidget.setHorizontalHeaderItem(5, QTableWidgetItem('★'))
            
        for paper in importantList:
            name, ID, course, deadline, summit, info = paper.GetPaperInfo()
            globals()['chbox_{}'.format(row)] = QCheckBox()
            globals()['chbox_{}'.format(row)].setChecked(True)
            globals()['chbox_{}'.format(row)].stateChanged.connect(self.MakeUnimportant)
            globals()['pbutton_{}'.format(row)] = QPushButton("...")
            globals()['pbutton_{}'.format(row)].clicked.connect(self.PrintPaperInfo)
            self.importantCheckBox.append(globals()['chbox_{}'.format(row)])
            self.importantPushButton.append(globals()['pbutton_{}'.format(row)])
            self.tableWidget.setRowCount(row+1)
            self.tableWidget.setItem(row,0,QTableWidgetItem(course))
            self.tableWidget.setItem(row,1,QTableWidgetItem(name))
            self.tableWidget.setItem(row,2,QTableWidgetItem('. '.join(deadline)))
            self.tableWidget.setItem(row,3,QTableWidgetItem(summit))
            self.tableWidget.setCellWidget(row,4,self.importantPushButton[row])
            self.tableWidget.setCellWidget(row,5,self.importantCheckBox[row])
            row += 1
        
        #일반과제란 출력
        row = 0
        if len(unimportantList) == 0:
            self.tableWidget_2.clear()
            self.tableWidget_2.setHorizontalHeaderItem(0, QTableWidgetItem('과목 이름'))
            self.tableWidget_2.setHorizontalHeaderItem(1, QTableWidgetItem('과제 이름'))
            self.tableWidget_2.setHorizontalHeaderItem(2, QTableWidgetItem('제출 기한'))
            self.tableWidget_2.setHorizontalHeaderItem(3, QTableWidgetItem('제출 여부'))
            self.tableWidget_2.setHorizontalHeaderItem(4, QTableWidgetItem('자세히'))
            self.tableWidget_2.setHorizontalHeaderItem(5, QTableWidgetItem('★'))

            
        for paper in unimportantList:
            name, ID, course, deadline, summit, info = paper.GetPaperInfo()
            globals()['chbox2_{}'.format(row)] = QCheckBox()
            globals()['chbox2_{}'.format(row)].setChecked(False)
            globals()['chbox2_{}'.format(row)].stateChanged.connect(self.MakeImportant)
            globals()['pbutton2_{}'.format(row)] = QPushButton("...")
            globals()['pbutton2_{}'.format(row)].clicked.connect(self.PrintPaperInfo)
            self.unimportantCheckBox.append(globals()['chbox2_{}'.format(row)])
            self.unimportantPushButton.append(globals()['pbutton2_{}'.format(row)])
            self.tableWidget_2.setRowCount(row+1)
            self.tableWidget_2.setItem(row,0,QTableWidgetItem(course))
            self.tableWidget_2.setItem(row,1,QTableWidgetItem(name))
            self.tableWidget_2.setItem(row,2,QTableWidgetItem('. '.join(deadline)))
            self.tableWidget_2.setItem(row,3,QTableWidgetItem(summit))
            self.tableWidget_2.setCellWidget(row,4,self.unimportantPushButton[row])
            self.tableWidget_2.setCellWidget(row,5,self.unimportantCheckBox[row])
            row += 1
        
    #과제 상세내용 출력
    def PrintPaperInfo(self):
        sender = self.sender()
        iidx = 0
        uidx = 0
        for pushButton in self.importantPushButton:
            if sender == pushButton:
                break
            iidx += 1
        for pushButton in self.unimportantPushButton:
            if sender == pushButton:
                break
            uidx += 1
        print(iidx, uidx)
        if (iidx != len(self.importantPushButton)) and (uidx == len(self.unimportantPushButton)):
            importantList = self.userData.GetImportantList()
            paper = importantList[iidx]
        
        if (iidx == len(self.importantPushButton)) and (uidx != len(self.unimportantPushButton)):
            unimportantList = self.userData.GetUnimportantList()
            paper = unimportantList[uidx]
        
        name, ID, course, deadline, summit, info = paper.GetPaperInfo()
        self.currentPaper = ID
        self.textBrowser_course_info.setText(course)
        self.textBrowser_name_info.setText(name)
        self.textBrowser_deadline_info.setText(deadline[0]+'년'+deadline[1]+'월'+deadline[2]+'일'+deadline[3]+'시'+deadline[4]+'분')
        self.textBrowser_summit_info.setText(summit)
        self.textBrowser_more_info.setText(info)
        self.stackedWidget.setCurrentIndex(3)
    
    #일반과제를 중요과제로    
    def MakeImportant(self):
        sender = self.sender()
        for row in range(0, len(self.unimportantCheckBox)):
            if sender == globals()['chbox2_{}'.format(row)]:
                break
        unimportantList = self.userData.GetUnimportantList()
        paperID = unimportantList[row].GetPaperID()
        self.userData.MakeImportant(paperID)
        self.userData.UpdateList()
        self.PrintPaperList()
    
    #중요과제를 일반과제로 
    def MakeUnimportant(self):
        sender = self.sender()
        for row in range(0, len(self.importantCheckBox)):
            if sender == globals()['chbox_{}'.format(row)]:
                break
        importantList = self.userData.GetImportantList()
        paperID = importantList[row].GetPaperID()
        self.userData.MakeUnimportant(paperID)
        self.userData.UpdateList()
        self.PrintPaperList()
   
    #과제추가 화면 출력
    def NewPaper(self):
        self.stackedWidget.setCurrentWidget(self.page_2)
        self.textEdit_course.clear()
        self.textEdit_name.clear()
        self.textEdit_summit.clear()
        self.textEdit_more.clear()
        nowtime = datetime.datetime.now()
        self.spinBox_year.setValue(nowtime.year)
        self.spinBox_month.setValue(nowtime.month)
        self.spinBox_day.setValue(nowtime.day)
        self.spinBox_hour.setValue(nowtime.hour)
        self.spinBox_minute.setValue(nowtime.minute)
    
    #기본화면 돌아가기
    def ReturnHome(self):
        self.stackedWidget.setCurrentWidget(self.page_1)
    
    #환경설정
    def Setting(self):
        self.stackedWidget.setCurrentWidget(self.page_4)
        alarmTime = self.userData.GetAlarmSet()
        self.spinBox_alarm_day.setValue(alarmTime[0])
        self.spinBox_alarm_hour.setValue(alarmTime[1])
        self.spinBox_alarm_minute.setValue(alarmTime[2])

        if self.autoLogin == 1:
            self.checkBox_autoLogin.setChecked(True)
        else:
            self.checkBox_autoLogin.setChecked(False)
    
    #과제 새로고침    
    def Refresh(self): 
        self.userData.Update()
        self.PrintPaperList()
        self.CheckAlarm()
    
    #알람시간 설정        
    def SetAlarmTime(self):  
        day = self.spinBox_alarm_day.value()#시간값
        hour = self.spinBox_alarm_hour.value()
        minute = self.spinBox_alarm_minute.value()
        #self.alarmtime = [day, hour, minute, 0]
        alarmSetting = [day, hour, minute, 0]
        self.userData.SetAlarm(alarmSetting)
    
    #알람 필요여부 확인하고 울리기
    def CheckAlarm(self):
        self.userData.CheckAlarm()
        while self.userData.IsAlarm() != 0:
            print("NEED ALARM!!!!")
            AlarmData = self.userData.GetAlarmData()
            AlarmMsg = "과목명: " + AlarmData[0] + "\n과제명: " + AlarmData[1] + "\n제출 기한: " + str(AlarmData[2])
            QMessageBox.about(self,"Alarm",AlarmMsg)
            self.userData.ClearAlarm()
        else:
            print("NOT need alarm")

    #과제 삭제
    def DeletePaper(self):
        paperID = self.currentPaper
        self.userData.DeletePaper(paperID)
        self.stackedWidget.setCurrentIndex(1)
        self.userData.UpdateList()
        self.PrintPaperList()
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    currentUi = Ui()
    currentUi.show()
    sys.exit(app.exec_())


# 리소스 변경 시마다 터미널창에 입력
# pyrcc5 resource.qrc -o resource_rc.py

# 실행파일로 만들기
# pyinstaller -w -F main.py