import datetime
import random
import string

import httplib2
import numpy as np
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, redirect
from oauth2client.service_account import ServiceAccountCredentials
from sklearn.externals import joblib

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from myApp.form import SingleLineForm, UploadFileForm, DoubleLineForm
from myApp.models import user_data, course_table, course_pdf, pdf_table, UserVoteTable, UserTagTable, UserPreviewTable, \
    PdfTagTable

userName = "x"
userEmail = "x"
PageNo = 0


def home(request):
    global PageNo
    PageNo = 1
    return render(request, "homepage.html", {'UserName': userName})


def registration(request):
    return render(request, "RegistrationPage.html")


def login(request):
    return render(request, "LogInPage.html")


def logout(request):
    global userEmail
    global userName
    userEmail = "x"
    userName = "x"
    return goBackToWhereYouEnded(request)


def validateLogin(request):
    email = request.GET.get('email', None)
    password = request.GET.get('password', None)
    print(getHash(password))

    results = user_data.objects.filter(Email=email, Password=getHash(password))
    Matched = False
    if results.exists():
        Matched = True
        global userName
        global userEmail
        userName = results[0].Name
        userEmail = results[0].Email

    data = {'isValid': Matched}
    return JsonResponse(data)


def addEntry(request):
    email = request.GET.get('email', None)
    password = request.GET.get('password', None)
    Name = request.GET.get('Name', None)
    Institution = request.GET.get('Institution', None)
    ConfirmPwd = request.GET.get('Confirm', None)

    message = 0
    global userName
    global userEmail

    print(email)
    print(password)
    print(ConfirmPwd)

    if "@" not in email:
        message = 1
    elif len(Name) == 0:
        message = 2
    elif len(password) < 8:
        message = 5
    elif password == ConfirmPwd:
        results = user_data.objects.filter(Email=email)
        if results.exists():
            message = 3
        else:
            userEmail = email
            userName = Name
            hrev = user_data(Email=email, Password=getHash(password), Name=Name, Institution=Institution)
            hrev.save()
    else:
        message = 4
    data = {'message': message}
    return JsonResponse(data)


def goBackToWhereYouEnded(request):
    if PageNo <= 1:
        return home(request)
    elif PageNo == 2:
        return deptPage(request)
    elif PageNo == 3:
        return termPage(request)
    elif PageNo == 4:
        return coursePage(request)
    elif PageNo == 5:
        return Lecture(request)


def deptPage(request):
    global PageNo
    PageNo = 2

    global InstitutionName
    for i in request.POST: InstitutionName = i;
    print(InstitutionName)
    results = course_table.objects.filter(Institution=InstitutionName)

    dept = []
    for i in results:
        a = {}
        a['department'] = i.department
        if a not in dept:  dept.append(a)

    for i in dept: print(i)
    Dictionary = {
        'UserName': userName,
        'query_results': dept
    }

    return render(request, "SubjectChoice.html", Dictionary)


def termPage(request):
    global PageNo
    PageNo = 3

    global department
    for i in request.POST: department = i;
    print(department)

    return render(request, "TermChoicePage.html", {'UserName': userName})


def coursePage(request):
    global PageNo
    PageNo = 4

    global LevelTerm
    for i in request.POST: LevelTerm = i;
    print(InstitutionName)
    print(department)
    print(LevelTerm)

    global SortVariable
    SortVariable = 'vote'

    global LastUploaded
    LastUploaded = None

    results = course_table.objects.filter(Institution=InstitutionName, LevelTerm=LevelTerm, department=department)
    courses = []
    for i in results:
        a = {}
        a['course'] = i.course
        if a not in courses:  courses.append(a)

    for i in courses: print(i)

    Dictionary = {
        'UserName': userName,
        'query_results': courses
    }
    return render(request, "CourseDisplayPage.html", Dictionary)


def Lecture(request):
    global PageNo
    PageNo = 5

    global SelectedCourse
    for i in request.POST: SelectedCourse = i;
    print(SelectedCourse)

    global LastUploaded;
    fs = FileSystemStorage();
    if LastUploaded: fs.delete(LastUploaded)

    results = course_pdf.objects.filter(course=SelectedCourse, Institution=InstitutionName)
    Lectures = []
    for i in results:
        print(i.pdfID)
        a = []
        a = pdf_table.objects.filter(pdfID=i.pdfID)
        for j in a:
            b = {}
            b['pdfID'] = j.pdfID
            b['fileName'] = j.fileName
            b['CourseTeacher'] = j.CourseTeacher
            b['uploadDate'] = j.uploadDate
            b['lastAccessed'] = j.lastAccessed
            b['vote'] = j.vote
            if UserVoteTable.objects.filter(Email=userEmail, pdfID=j.pdfID).exists():
                b['VoteButton'] = "UnVote"
            else:
                b['VoteButton'] = "Vote"
            Lectures.append(b)

    Lectures.sort(key=lambda x: x[SortVariable], reverse=True)
    for item in Lectures: item['uploadDate'] = item['uploadDate'].strftime("%b %d, %Y  %I:%M %p")

    Dictionary = {
        'UserName': userName,
        'query_results': Lectures,
        'selectedItem': SortVariable
    }

    print(userName)
    return render(request, "LecturePage.html", Dictionary)


def showPdf(request):
    if request.method == 'POST':
        form = SingleLineForm(request.POST)
        if form.is_valid():
            ID = form.cleaned_data['Field']

    results = pdf_table.objects.filter(pdfID=ID)
    results.update(lastAccessed=datetime.datetime.now())
    for i in results: url = i.driveID

    if userEmail != "x":
        results = UserPreviewTable.objects.filter(Email=userEmail, pdfID=ID)
        if not results.exists(): UserPreviewTable(Email=userEmail, pdfID=ID).save()

    url = "https://drive.google.com/open?id=" + url;
    return redirect(url, True)


def SortBy(request):
    if request.method == 'POST':
        form = SingleLineForm(request.POST)
        if form.is_valid():
            field = form.cleaned_data['Field']

    global SortVariable
    SortVariable = field;

    return HttpResponseRedirect('Lecture')


def uploadBook(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            Title = form.cleaned_data['Title']
            CourseTeacher = form.cleaned_data['CourseTeacher']
            Tag = form.cleaned_data['Tag']
            fs = FileSystemStorage()

            File = request.FILES['File']
            fs.save(File.name, File)

            global LastUploaded
            LastUploaded = File.name

            file_metadata = {'name': Title}
            media = MediaFileUpload(File.name, mimetype='application/pdf', resumable=True)
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
            http = credentials.authorize(httplib2.Http())
            drive_service = build('drive', 'v3', http=http)

            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            file_id = file.get('id')
            print(file_id)

            batch = drive_service.new_batch_http_request()
            user_permission = {'type': 'anyone', 'role': 'reader', 'withLink': True}
            batch.add(drive_service.permissions().create(fileId=file_id, body=user_permission, fields='id', ))
            batch.execute()

            ID = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))
            pdf_table(pdfID=ID, CourseTeacher=CourseTeacher, uploader=userEmail, fileName=Title, driveID=file_id,
                      uploadDate=datetime.datetime.now(), lastAccessed=datetime.datetime.now(), vote=0).save()
            course_pdf(Institution=InstitutionName, course=SelectedCourse, pdfID=ID).save()
            if Tag != "None": PdfTagTable(pdfID=ID, Tag=Tag).save()

            return HttpResponseRedirect(('Lecture'))


def VoteChange(request):
    if userName == "x":
        data = {'valid': "No"}
    else:
        pdfID = request.GET.get('pdfID', None)
        if UserVoteTable.objects.filter(Email=userEmail, pdfID=pdfID).exists():
            VoteType = "Vote"
        else:
            VoteType = "UnVote"

        results = pdf_table.objects.filter(pdfID=pdfID)
        for i in results: CurrentVote = i.vote

        if VoteType == 'UnVote':
            results.update(vote=CurrentVote + 1)
            UserVoteTable(Email=userEmail, pdfID=pdfID).save()
        else:
            results.update(vote=CurrentVote - 1)
            UserVoteTable.objects.filter(Email=userEmail, pdfID=pdfID).delete()

        results = course_pdf.objects.filter(course=SelectedCourse, Institution=InstitutionName)
        Lectures = []
        for i in results:
            print(i.pdfID)
            a = []
            a = pdf_table.objects.filter(pdfID=i.pdfID)
            for j in a:
                b = {}
                b['pdfID'] = j.pdfID
                b['fileName'] = j.fileName
                b['CourseTeacher'] = j.CourseTeacher
                b['uploadDate'] = j.uploadDate
                b['lastAccessed'] = j.lastAccessed
                b['vote'] = j.vote
                if UserVoteTable.objects.filter(Email=userEmail, pdfID=j.pdfID).exists():
                    b['VoteButton'] = "UnVote"
                else:
                    b['VoteButton'] = "Vote"
                Lectures.append(b)
        Lectures.sort(key=lambda x: x[SortVariable], reverse=True)
        for item in Lectures: item['uploadDate'] = item['uploadDate'].strftime("%b %d, %Y  %I:%M %p")

        data = {'updated_results': Lectures, 'valid': "Yes"}
        for item in Lectures: print(item['uploadDate'])

    return JsonResponse(data)


def SendUserName(request):
    data = {'UserName': userName}
    return JsonResponse(data)

def GetRecommendation():
    trainMachine()
    results = pdf_table.objects.filter();
    views = []
    for item in results:
        viewCount = UserPreviewTable.objects.filter(pdfID=item.pdfID).count()
        views.append([viewCount])

    file1 = open('ml_models/scaler_X.save', 'rb')
    sc_X = joblib.load(file1)
    file1.close()

    file2 = open('ml_models/scaler_y.save', 'rb')
    sc_y = joblib.load(file2)
    file2.close()

    file = open('ml_models/estimator.save', 'rb')
    regressor = joblib.load(file)
    file.close()

    X = np.array(views, np.int32)
    X = X + 1
    X_test = sc_X.transform(X)
    y_pred = sc_y.inverse_transform(regressor.predict(X_test))

    recommended = []
    for i in range(0, len(y_pred)):
        CurrentData = {}
        CurrentData['pdfID'] = results[i].pdfID
        currentVote = UserVoteTable.objects.filter(pdfID=item.pdfID).count()
        CurrentData['Increase'] = y_pred[i] - currentVote
        recommended.append(CurrentData)
    recommended.sort(key=lambda x: x['Increase'], reverse=True)

    Reco = []
    for i in range(0, 5):
        CurrentReco = {}
        ID=recommended[i]['pdfID']
        CurrentReco['pdfID']=ID
        CurrentReco['fileName']=pdf_table.objects.get(pdfID=ID).fileName
        CurrentReco['CourseTeacher']=pdf_table.objects.get(pdfID=ID).CourseTeacher
        CurrentReco['uploadDate']=pdf_table.objects.get(pdfID=ID).uploadDate
        CurrentReco['vote']=pdf_table.objects.get(pdfID=ID).vote
        if UserVoteTable.objects.filter(Email=userEmail, pdfID=ID).exists():
            CurrentReco['VoteButton'] = "UnVote"
        else:
            CurrentReco['VoteButton'] = "Vote"
        Reco.append(CurrentReco)
    return Reco

def GetTopFavourites():
    my_Tags = UserTagTable.objects.filter(Email=userEmail);

    TopTagVote = []
    for item in my_Tags:
        results=PdfTagTable.objects.filter(Tag=item.Tag)
        for p in results:
            CurrentFav = {}
            thisPDF=pdf_table.objects.filter(pdfID=p.pdfID)
            if thisPDF.exists() :
                thisPDF = pdf_table.objects.get(pdfID=p.pdfID)

                ID = thisPDF.pdfID
                CurrentFav['pdfID'] = ID
                CurrentFav['fileName'] = thisPDF.fileName
                CurrentFav['CourseTeacher'] = thisPDF.CourseTeacher
                CurrentFav['uploadDate'] = thisPDF.uploadDate
                CurrentFav['vote'] = thisPDF.vote
                if UserVoteTable.objects.filter(Email=userEmail, pdfID=ID).exists():
                    CurrentFav['VoteButton'] = "UnVote"
                else:
                    CurrentFav['VoteButton'] = "Vote"
                TopTagVote.append(CurrentFav)

    TopTagVote.sort(key=lambda x: x['vote'], reverse=True)

    return TopTagVote


def UserProfile(request):
    All_Tags = UserTagTable.objects.filter(Email="admin@gmail.com");
    TagTable = []

    for item in All_Tags:
        NewTag = {}
        NewTag['TagName'] = item.Tag
        results = UserTagTable.objects.filter(Email=userEmail, Tag=item.Tag)
        if results: NewTag['Int'] = "true"
        else: NewTag['Int'] = "false"
        print(item.Tag + " " + NewTag['Int'] + " " + userEmail)
        TagTable.append(NewTag)

    myUploads = pdf_table.objects.filter(uploader=userEmail)
    List = []

    for item in myUploads:
        pdfInstance = {}

        pdfID = item.pdfID
        fileName = item.fileName
        CourseData = course_pdf.objects.filter(pdfID=pdfID)
        Institution = CourseData[0].Institution
        course = CourseData[0].course
        LevelTermData = course_table.objects.filter(Institution=Institution, course=course)
        TermNo = (LevelTermData[0].LevelTerm + 1) % 2 + 1
        LevelNo = (LevelTermData[0].LevelTerm + 2 - TermNo) // 2

        pdfInstance['pdfID'] = pdfID
        pdfInstance['fileName'] = fileName
        pdfInstance['Institution'] = Institution
        pdfInstance['course'] = course
        pdfInstance['LevelNo'] = LevelNo
        pdfInstance['TermNo'] = TermNo
        List.append(pdfInstance)
        print(fileName)

    Dictionary = {
        'Name': userName,
        'Email': userEmail,
        'Institution': user_data.objects.get(Email=userEmail).Institution,
        'Interests': TagTable,
        'query_results': List,
        'Reco_results': GetRecommendation(),
        'tag_results' : GetTopFavourites()
    }
    return render(request, "UserProfile.html", Dictionary)


def UpdateInterest(request):
    selchbox = request.GET.get('q')
    CurrentTags = selchbox.split('#')
    UserTagTable.objects.filter(Email=userEmail).delete()

    for Tag in CurrentTags:
        print((Tag))
        if Tag: UserTagTable(Email=userEmail, Tag=Tag).save()
    return HttpResponse(UserProfile)


def ChangeInfo(request):
    if request.method == 'POST':
        form = DoubleLineForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['field1']
            institution = form.cleaned_data['field2']

        results = user_data.objects.filter(Email=userEmail)
        results.update(Name=name, Institution=institution)
        global userName
        userName = name
    return UserProfile(request)


def deletePdf(request):
    if request.method == 'POST':
        form = SingleLineForm(request.POST)
        if form.is_valid():
            ID = form.cleaned_data['Field']

    pdf_table.objects.filter(pdfID=ID).delete()
    course_pdf.objects.filter(pdfID=ID).delete()
    UserVoteTable.objects.filter(pdfID=ID).delete()
    return UserProfile(request)

def trainMachine():
    results = pdf_table.objects.filter()
    TrainDataX = []
    TrainDatay = []
    for item in results:
        TrainDataX.append([UserPreviewTable.objects.filter(pdfID=item.pdfID).count()])
        TrainDatay.append([UserVoteTable.objects.filter(pdfID=item.pdfID).count()])
        print(
            str(pdf_table.objects.get(pdfID=item.pdfID).fileName)+" "+
            str(UserPreviewTable.objects.filter(pdfID=item.pdfID).count())+" "+
            str(UserVoteTable.objects.filter(pdfID=item.pdfID).count())
        )

    X = np.array(TrainDataX, dtype=np.int32)
    y = np.array(TrainDatay, dtype=np.int32)

    # Splitting the dataset into the Training set and Test set
    from sklearn.cross_validation import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0, random_state=0)

    # Feature Scaling
    from sklearn.preprocessing import StandardScaler
    sc_X = StandardScaler()
    X_train = sc_X.fit_transform(X_train)
    # X_test = sc_X.transform(X_test)
    sc_y = StandardScaler()
    y_train = sc_y.fit_transform(y_train)
    # y_test = sc_y.transform(y_test)

    # Fitting Random Forest Regression to the dataset
    from sklearn.ensemble import RandomForestRegressor
    regressor = RandomForestRegressor(n_estimators=100, random_state=0)
    regressor.fit(X_train, y_train)

    # save the scalers to disk
    # scaler_file_X = django_settings.MEDIA_ROOT + 'ml_models/scaler_X.save'
    file1 = open('ml_models/scaler_X.save', mode='wb')
    joblib.dump(sc_X, file1)
    file1.close()

    # scaler_file_y = django_settings.MEDIA_ROOT + 'ml_models/scaler_y.save'
    file2 = open('ml_models/scaler_y.save', mode='wb')
    joblib.dump(sc_y, file2)
    file2.close()

    # save the model to disk
    file3 = open('ml_models/estimator.save', mode='wb')
    joblib.dump(regressor, file3)
    file3.close()

    # y_pred = sc_y.inverse_transform(regressor.predict(X_test))

def VoteUpdate(request):
    pdfID = request.GET.get('pdfID', None)
    if UserVoteTable.objects.filter(Email=userEmail, pdfID=pdfID).exists():
        VoteType = "Vote"
    else:
        VoteType = "UnVote"

    results = pdf_table.objects.filter(pdfID=pdfID)
    for i in results: CurrentVote = i.vote

    if VoteType == 'UnVote':
        results.update(vote=CurrentVote + 1)
        UserVoteTable(Email=userEmail, pdfID=pdfID).save()
    else:
        results.update(vote=CurrentVote - 1)
        UserVoteTable.objects.filter(Email=userEmail, pdfID=pdfID).delete()

    data={}
    return JsonResponse(data)

def getHash(UserName):
    HashVal=0
    Mul=1
    for i in range(0,len(UserName)):
        HashVal+=ord(UserName[i])*Mul
        Mul=Mul*19
        HashVal=HashVal%1000000007
    return str(HashVal)