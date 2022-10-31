from enum import auto
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic


# 파싱 관련 import
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


class Paper:
    def __init__(self):
        self.paperName = 'name'
        self.paperID = 'ID'
        self.course = 'course'
        self.deadline = 'deadline'
        self.summit = 'summit'
        self.info = 'info'
        self.important = False
    
    # Paper의 정보를 입력하는 메소드
    def InputPaperInfo(self, name, ID, course, deadline, summit, info):
        self.paperName = name
        self.paperID = ID
        self.course = course
        self.deadline = deadline
        self.summit = summit
        self.info = info
    
    # Paper의 정보를 출력하는 메소드
    def GetPaperData(self):
        return self.paperName, self.paperID, self.course, self.deadline, self.summit, self.info
    
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
    
    def GetPaperInfo(self):
        return self.paperName, self.paperID, self.course, self.deadline, self.summit, self.info
    
    def GetPaperImportant(self):
        return self.important
    
    #Paper의 중요 표시를 설정하는 메소드
    def MakePaperImportant (self):
        self.important = True
    
    #Paper의 중요 표시를 해제하는 메소드
    def MakePaperUnimportant (self):
        self.important = False

class TotalPaperList:
    def __init__(self):
        self.totalList = []
        self.unimportantList = []
        self.importantList = []
        self.alarmList = []
        self.needAlarm = 0
        self.alarmSet = [0, 1, 0, 0]

    
    def MakeImportant(self, paperID):
        for paper in self.totalList:
            if paper.GetPaperID() == paperID:
                paper.MakePaperImportant()
    
    #과제를 일반 과제로 설정하고, 일반 과제 리스트에 추가하는 메소드
    def MakeUnimportant(self, paperID):
        for paper in self.totalList:
            if paper.GetPaperID() == paperID:
                paper.MakePaperUnimportant()
                
    def AddPaper(self, paper):
        self.totalList.append(paper)
    
    def UpdateList(self):
        self.importantList = []
        self.unimportantList = []
        for paper in self.totalList:
            if paper.GetPaperImportant() == True:
                self.importantList.append(paper)
            else:
                self.unimportantList.append(paper)

##############################################################            
    def CalculateTime(self,startTime,endTime):
        remainTime = endTime-startTime
        remainDays = remainTime.days
        remainHours = remainTime.seconds//3600
        remainMinutes = remainTime.seconds//60-remainHours*60
        remainSeconds = remainTime.seconds-remainHours*3600-remainMinutes*60
        remainTimes = [remainDays,remainHours,remainMinutes,remainSeconds]
        return remainTimes
################################################################

    def UpdatePaper(self, driver, Url):
        self.alarmList = []
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
                    if len(self.totalList) == 0:
                        newPaper = Paper()
                        newPaper.InputPaperInfo(paperName, paperID, courseName, deadline, summit, info)
                        self.totalList.append(newPaper)
                    else:
                        for idx in range(0, len(self.totalList)):
                            if paperID == self.totalList[idx].GetPaperID():
                                self.totalList[idx].InputPaperInfo(paperName, paperID, courseName, deadline, summit, info)
                                break
                            
                            if idx == len(self.totalList)-1:
                                newPaper = Paper()
                                newPaper.InputPaperInfo(paperName, paperID, courseName, deadline, summit, info)
                                self.totalList.append(newPaper)
    def CheckAlarm(self):
        self.needAlarm = 0
        for paper in self.totalList:
            deadline = paper.GetPaperDeadline()
            ######################################################
                    #alarm default = 1hour
                    #[일, 시, 분, 초]

            alarmZero = [0 ,0 ,0 ,0] 
            startTime = datetime.datetime.now()
            endTime = datetime.datetime(int(deadline[0]),int(deadline[1]),int(deadline[2]),int(deadline[3]),int(deadline[4]))
            remainTimes = self.CalculateTime(startTime,endTime)
            #알람 시간보다 과제 남은 시간이 작으면 알람을 울림
            if alarmZero < remainTimes < self.alarmSet :
                courseName = paper.GetPaperCourse()
                paperName = paper.GetPaperName()
                self.needAlarm += 1
                alarmData = [courseName, paperName, endTime]
                self.alarmList.append(alarmData)
                print(self.needAlarm)
            ####################################################
    
    def GetAlarmSet(self):
        return self.alarmSet

    def DeletePaper(self, paperID):
        for paper in self.totalList:
            if paper.GetPaperID() == paperID:
                self.totalList.remove(paper)

    def ClearList(self):
        self.totalList = []
        self.importantList = []
        self.unimportantList = []
        self.alarmSet = [0, 1, 0, 0]
                
    def CheckID(self, paperID):
        for paper in self.totalList:
            if paperID == paper.GetPaperID():
                return True
        return False

    def SetAlarm(self, alarmSetting):
        self.alarmSet = alarmSetting

    def ClearAlarm(self):
        self.needAlarm -= 1

    def GetAlarmData(self):
        return self.alarmList.pop()

    def GetImportantList(self):
        return self.importantList
    
    def GetUnimportantList(self):
        return self.unimportantList

    def IsAlarm(self):
        return self.needAlarm

class UserData:
    def __init__(self):
        self.userID = ''
        self.userPW = ''
        self.loginUrl = 'https://uclass.uos.ac.kr/login.php'
        self.mainUrl = 'https://uclass.uos.ac.kr/'
        self.totalList = TotalPaperList()
        self.StartWeb()
        
    def StartWeb(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options = options)
        self.driver.get(self.loginUrl)
    
    def Login(self, ID, PW):
        if ID == '' or PW == '':
            return '아이디와 비밀번호는 반드시 입력해야 합니다.'
        
        self.driver.get(self.loginUrl)
        self.driver.find_element_by_name('username').send_keys(ID)
        self.driver.find_element_by_name('password').send_keys(PW)
        
        self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div/div/div[1]/div[1]/div[2]/form/div[2]/input').click()
        
        if self.driver.current_url == self.mainUrl:
            self.userID = ID
            self.userPW = PW
            return 'success'
        else:
            errorCode = re.findall("\d+", self.driver.current_url)
            if errorCode[0] == '1':
                return '현재, 브라우저의 쿠키가 작동하지 않습니다.'
            elif errorCode[0] == '2':
                return '사용자 아이디 : 아이디에는 영어소문자, 숫자, 밑줄( _ ), 하이폰( - ), 마침표( . ) 또는 @ 기호만 쓸 수 있습니다.'
            elif errorCode[0] == '3':
                return '아이디 또는 패스워드가 잘못 입력되었습니다.'
    
    def Logout(self):
        self.totalList.ClearList()
        self.driver.get(self.mainUrl)
        self.driver.find_element_by_xpath('/html/body/div[3]/div[1]/nav/div/div[2]/ul/li[8]/a').click()
        
    def Update(self):
        self.totalList.UpdatePaper(self.driver, self.mainUrl)
        self.totalList.UpdateList()      

    def UpdateList(self):
        self.totalList.UpdateList()

    def GetImportantList(self):
        return self.totalList.GetImportantList()
    
    def GetUnimportantList(self):
        return self.totalList.GetUnimportantList()

    def IsAlarm(self):
        return self.totalList.IsAlarm()
    
    def GetAlarmData(self):
        return self.totalList.GetAlarmData()

    def ClearAlarm(self):
        self.totalList.ClearAlarm()
    
    def GetAlarmSet(self):
        return self.totalList.GetAlarmSet()

    def DeletePaper(self, paperID):
        self.totalList.DeletePaper(paperID)

    def SetAlarm(self, alarmSetting):
        self.totalList.SetAlarm(alarmSetting)

    def MakeImportant(self, paperID):
        self.totalList.MakeImportant(paperID)

    def MakeUnimportant(self, paperID):
        self.totalList.MakeUnimportant(paperID)

    def CheckID(self, paperID):
        return self.totalList.CheckID(paperID)

    def CheckAlarm(self):
        self.totalList.CheckAlarm()
    

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
        self.inputPassword.returnPressed.connect(self.Login)
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

    def Logout(self):
        quitMessage = "로그아웃 하시겠습니까?"
        reply = QMessageBox.question(self, 'Message', quitMessage, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.autoLogin = 0
            self.loginCount = 0
            self.SaveUserData()
            self.userData.Logout()
            self.inputId.clear()
            self.inputPassword.clear()
            self.stackedWidget.setCurrentIndex(0)


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
    
    def SetAutoLogin(self):
        sender = self.sender()
        if sender.isChecked():
            self.autoLogin = 1
        else:
            self.autoLogin = 0
    
    def SaveUserData(self):
        with open('log.p','wb')as file:
            pickle.dump(self.autoLogin,file)
            pickle.dump(self.userData.userID,file)
            pickle.dump(self.userData.userPW,file)
            pickle.dump(self.userData.totalList,file)
        
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
        self.userData.totalList.AddPaper(newPaper)
        self.userData.totalList.UpdateList()
        self.PrintPaperList()
        self.ReturnHome()
    
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
                    self.userData.totalList = pickle.load(file)
                    print("autologin almost there...")
                self.inputId.setText(ID1)
                self.inputPassword.setText(PW1)    
                self.Login()
                    
        else :
            print("auto login exception occured")

    def Login(self):
        self.autoLogin = 0
        print('login process starts...')
        msg = self.userData.Login(self.inputId.text(), self.inputPassword.text())
        print(msg)
        if msg == 'success':
            if os.path.exists('log.p') and os.path.getsize('log.p')>0:
                with open('log.p','rb') as file:
                    autoLogin = pickle.load(file)
                    ID1 = pickle.load(file)
                    PW1 = pickle.load(file)
                    PastList = pickle.load(file)
                if (ID1 == self.inputId.text() and PW1 == self.inputPassword.text()):
                    self.autoLogin = autoLogin
                    self.userData.totalList = PastList

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

    def assignmentWidget(self):
        a = QListWidgetItem(QIcon("./icon.png"), "1234") # 각각 (setIcon, setText)로 수정 가능
        print(a.sizeHint())
        self.listWidget.addItem(a)
   
    def PrintPaperList(self):
        importantList = self.userData.GetImportantList()
        unimportantList = self.userData.GetUnimportantList()
        self.importantCheckBox = []
        self.importantPushButton = []
        self.unimportantCheckBox = []
        self.unimportantPushButton = []
        
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

    def NewPaper(self):#과제추가
        self.stackedWidget.setCurrentWidget(self.page_2)
        self.stackedWidget.setCurrentWidget(self.page_2)
        nowtime = datetime.datetime.now()
        self.spinBox_year.setValue(nowtime.year)
        self.spinBox_month.setValue(nowtime.month)
        self.spinBox_day.setValue(nowtime.day)
        self.spinBox_hour.setValue(nowtime.hour)
        self.spinBox_minute.setValue(nowtime.minute)
    
    def ReturnHome(self):#홈화면 돌아가기 #완성
        self.stackedWidget.setCurrentWidget(self.page_1)
    
    def Setting(self): #환경설정창 이동 #완성 
        self.stackedWidget.setCurrentWidget(self.page_4)
        alarmTime = self.userData.GetAlarmSet()
        self.spinBox_alarm_day.setValue(alarmTime[0])
        self.spinBox_alarm_hour.setValue(alarmTime[1])
        self.spinBox_alarm_minute.setValue(alarmTime[2])

        if self.autoLogin == 1:
            self.checkBox_autoLogin.setChecked(True)
        else:
            self.checkBox_autoLogin.setChecked(False)
        
    def Refresh(self): #과제 새로고침
        self.userData.Update()
        self.PrintPaperList()
        self.CheckAlarm()
        
###############################
        
        
    #def moreinfo(self): #과제정보자세히창이동후 과제정보 로드해야겠쥬
     #   self.stackedWidget.setCurrentWidget(self.page_3)

##################################################################    
    def SetAlarmTime(self): #알람시간 설정   
        
        day = self.spinBox_alarm_day.value()#시간값
        hour = self.spinBox_alarm_hour.value()
        minute = self.spinBox_alarm_minute.value()
        #self.alarmtime = [day, hour, minute, 0]
        alarmSetting = [day, hour, minute, 0]
        self.userData.SetAlarm(alarmSetting)

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
#####################################################################

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