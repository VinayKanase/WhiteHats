from django.shortcuts import render
from django.http import HttpResponseRedirect
from decouple import config
from django.urls import reverse
import pyrebase
from django.contrib import messages
import json

# FIREBASE CONIFGURATION
firebaseConfig = {
    'apiKey': config('FIREBASE_APIKEY'),
    'authDomain': config('FIREBASE_AUTHDOMAIN'),
    'projectId': config('FIREBASE_PROJECTID'),
    'storageBucket': config('FIREBASE_STORAGEBUCKET'),
    'messagingSenderId': config('FIREBASE_MESSAGINGSENDERID'),
    'appId': config('FIREBASE_APPID'),
    'measurementId': config('FIREBASE_MEASUREMENTID'),
    'databaseURL': config('FIREBASE_DATABASEURL')
}

app = pyrebase.initialize_app(firebaseConfig)
auth = app.auth()
database = app.database()
storage = app.storage()
refreshToken = ""


def checkIfAuthUser(request):
    """
        Function to check if user is logged in
    """
    try:
        userId = request.session['uid']
    except:
        return False
    try:
        auth.get_account_info(userId)
        return userId
    except:
        try:
            user = auth.refresh(refreshToken)
            request.session['uid'] = user
            return True
        except:
            return ''


def index(request):
    """
        Controller for index or home page
    """
    try:
        # gets id list of sholarships
        data = list(database.child('scholarships').get().val())
    except TypeError as e:
        # TypeError happens when unable to fetch data from database.
        print(e)
        messages.info(
            request, 'Please check your internet. Unable to fetch data')
        return HttpResponseRedirect(reverse('index'))
    totalCount = len(data)  # Gets length of data list
    context = {
        'totalScholarshipsAvailable': totalCount
    }
    try:
        request.session['uid']
        context['userLoggedIn'] = True
    except KeyError:
        pass
    try:
        context['isAdmin'] = database.child('users').child(auth.get_account_info(request.session['uid'])[
            'users'][0]['localId']).child('role').get().val() == 'admin'
    except:
        pass
    return render(request, 'index.html', context)


def search(request):
    """
        Controller for search scholarships page
    """
    scholarships = []
    for s in database.child("scholarships").get().each():
        if(s.item[1]['verified']):
            # if verified scholarship then append to sholarships
            scholarships.append(s.val())
    # Actions according to different search by values
    if(request.GET.get('searchBy')):
        tempScholarships = scholarships
        scholarships = []
        searchBy = request.GET.get("searchBy")
        query = request.GET.get("q").lower()
        if(searchBy == "all"):
            for s in tempScholarships:
                if(s['name'].lower().find(query) != -1):
                    scholarships.append(s)
                elif(s['provider'].lower().find(query) != -1):
                    scholarships.append(s)
        elif(searchBy == "topGrossing"):
            if(query):
                tempScholarships = sorted(tempScholarships,
                                          key=lambda item: item['likes'], reverse=True)
                for s in tempScholarships:
                    if(s['name'].lower().find(query) != -1):
                        scholarships.append(s)
                    elif(s['provider'].lower().find(query) != -1):
                        scholarships.append(s)
            else:
                scholarships = sorted(tempScholarships,
                                      key=lambda item: item['likes'], reverse=True)
        else:
            for s in tempScholarships:
                if(s[searchBy].lower().find(query) != -1):
                    scholarships.append(s)

    context = {
        'scholarships': scholarships
    }
    try:
        request.session['uid']
        context['userLoggedIn'] = True
    except:
        print("User is anonymous")
    try:
        context['isAdmin'] = database.child('users').child(auth.get_account_info(request.session['uid'])[
            'users'][0]['localId']).child('role').get().val() == 'admin'
    except:
        pass
    return render(request, 'search.html', context)


def new(request):
    """
        Controller to add new scholarships
        Authorized to logged in users only 
    """
    checkAtLeastOneSocialLink = False
    localId = checkIfAuthUser(request)
    if(localId == False):
        messages.warning(
            request, 'Please login to access add new scholarships')
        return HttpResponseRedirect(reverse('login'))
    elif(localId == ''):
        messages.warning(request, 'Please Log out and log in.')
        return HttpResponseRedirect(reverse('profile'))
    if(request.method == 'POST'):
        name = request.POST.get('name')
        uploaded_file_url = ""
        applyUrl = ""
        procedureOfApplication = request.POST.get('procedureOfApplication')
        try:
            img = request.FILES['img']
            check = False
            imageTypesAllowed = ['png', 'jpg', 'jpeg', 'gif']
            for type in imageTypesAllowed:
                if(img.find('.' + type)):
                    check = True
                    break
            if(not check):
                messages.error(
                    request, 'File type must be png, jpg, jpeg, gif')
                return HttpResponseRedirect(reverse('new'))

            file_name = name + img.name
            filename = storage.child(file_name).put(img)
            uploaded_file_url = "https://firebasestorage.googleapis.com/v0/b/whitehats-hackathon.appspot.com/o/" + \
                file_name + "?alt=media&token=" + filename['downloadTokens']
        except:
            print("No Image Added")
        provider = request.POST.get('provider')
        eligibility = request.POST.get('eligibility')
        conditions = []
        conditionCount = int(request.POST.get('conditionCount'))
        for i in range(1, conditionCount+1):
            conditions.append(request.POST.get('condition'+str(i)))
        duration = request.POST.get('duration')
        rate = request.POST.get('rate')
        try:
            evaluation = request.POST.get('evaluation')
        except:
            print("No eval")
        try:
            applyUrl = request.POST.get('applyUrl')
        except:
            print("No form url")
        personalSectionTotalCount = int(request.POST.get('personalCountTotal'))
        try:
            email = request.POST.get('email')
            checkAtLeastOneSocialLink = True
        except:
            print("No email found")
        try:
            instagram = request.POST.get('instagram')
            checkAtLeastOneSocialLink = True
        except:
            print("No instagram url")
        uid = database.generate_key()
        try:
            linkedin = request.POST.get('linkedin')
            checkAtLeastOneSocialLink = True
        except:
            print("No linkedin url")
        try:
            website = request.POST.get('website')
            checkAtLeastOneSocialLink = True
        except:
            print("No website url")
        try:
            phone = request.POST.get('phone')
            checkAtLeastOneSocialLink = True
        except:
            pass
        try:
            facebook = request.POST.get('facebook')
            checkAtLeastOneSocialLink = True
        except:
            pass
        personalSections = []
        for i in range(1, personalSectionTotalCount+1):
            personalSectionHeading = request.POST.get('heading' + str(i))
            personalSectionDetails = request.POST.get('information' + str(i))
            personalSections.append({
                'id': i,
                'heading': personalSectionHeading,
                'information': personalSectionDetails
            })
        data = {
            'uid': uid,
            'name': name,
            'provider': provider,
            'eligibility': eligibility,
            'conditions': conditions,
            'procedureOfApplication': procedureOfApplication,
            'rateOfScholarship': rate,
            'duration': duration,
            'socials': {
            },
            'likes': 0,
            'likedBy': [],
            'verified': False,
            'reports': 0,
            'scholarshipAddedBy': {
                'email': auth.get_account_info(request.session['uid'])['users'][0]['email'],
                "uid": request.session['uid'],
            }
        }
        if(evaluation):
            data['evaluation'] = evaluation
        if(uploaded_file_url):
            data['bannerUrl'] = uploaded_file_url
        if(personalSections):
            data['additionalSections'] = personalSections
        if(applyUrl):
            data['applyUrl'] = applyUrl
        if(phone):
            data['socials']['phone'] = phone
        if(facebook):
            data['socials']['facebook'] = facebook
        if(instagram):
            data['socials']['instagram'] = instagram
        if(email):
            data['socials']['email'] = email
        if(linkedin):
            data['socials']['linkedin'] = linkedin
        if(website):
            data['socials']['website'] = website

        database.child("scholarships").child(uid).set(data)
        return HttpResponseRedirect(reverse('search'))
    try:
        context = {}
        if(request.session['uid']):
            context['userLoggedIn'] = True
        try:
            context['isAdmin'] = database.child('users').child(auth.get_account_info(request.session['uid'])[
                'users'][0]['localId']).child('role').get().val() == 'admin'
        except:
            pass
        return render(request, 'new.html', context)
    except:
        messages.warning(request, 'Please Login to add new Scholarship')
        return HttpResponseRedirect(reverse('login'))


def login(request):
    """
        Controller to login page
    """
    if(request.method == 'POST'):
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            # Try to login users
            user = auth.sign_in_with_email_and_password(email, password)
        except Exception as e:
            # if error happens return error
            messages.error(request, json.loads(e.args[1])['error']['message'])
            return HttpResponseRedirect(reverse('login'))

        if(user):
            userInfo = auth.get_account_info(user['idToken'])['users']
            if(not userInfo[0]['emailVerified']):
                # Check if email was verified
                messages.error(
                    request, 'Verification link as been send on your email please verify it to login your account.')
                return HttpResponseRedirect(reverse('login'))
            else:
                request.session['uid'] = str(user['idToken'])
    if(not request.session.get('uid')):
        return render(request, 'login.html')
    else:
        messages.info(request, "You are already logged in.")
        return HttpResponseRedirect(reverse('index'))


def signUp(request):
    """
        Controller to sign up new user
    """
    if(request.method == 'POST'):
        name = request.POST.get('name')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password = request.POST.get('password')
        # Creaate new user with email and password
        user = auth.create_user_with_email_and_password(email, password)
        # Will send email verification link to user
        auth.send_email_verification(user['idToken'])
        # Add new user info to database
        if(user):
            session_id = user['localId']
            data = {
                'name': name,
                'email': email,
                'role': 'student'
            }
            database.child('users').child(session_id).set(data)
            messages.info(
                request, 'Account was successfully created please verify email and login to use.')
            return HttpResponseRedirect(reverse('login'))
    return render(request, 'signUp.html')


def scholarship(request, id):
    """
        Controller to see information of each scholarship
    """
    context = {}
    try:
        data = {}
        for i in database.child("scholarships").child(id).get().each():
            data[i.key()] = i.val()
        try:
            # If scholarship has comments
            for comment in data['comments']:
                commentby = comment['by']
                name = database.child('users').child(
                    commentby).child('name').get().val()
                role = database.child('users').child(
                    commentby).child('role').get().val()
                # Adds user name and role in comments
                comment['by'] = {
                    'name': name,
                    'role': role,
                }
        except Exception as e:
            print("ERROR:")
            print(e)
        context['data'] = data
        try:
            # Checks if scholarship has socials and adds them to context
            context['socials'] = data['socials']
        except:
            print("No socials")
    except TypeError:
        messages.error(
            request, 'Please check your internet. Unable to fetch data')
        return HttpResponseRedirect(reverse('search'))
    except:
        messages.info(request, 'No such scholarship found')
        return HttpResponseRedirect(reverse('search'))
    try:
        request.session['uid']
        context['userLoggedIn'] = True
    except KeyError as e:
        print(e)
    try:
        context['isAdmin'] = database.child('users').child(auth.get_account_info(request.session['uid'])[
            'users'][0]['localId']).child('role').get().val() == 'admin'
    except:
        pass
    return render(request, 'scholarship.html', context)


def liked(request):
    """
        Controller to see total liked scholarships by you
        Authorized to logged in users only 
    """
    localId = checkIfAuthUser(request)
    if(localId == False):
        messages.warning(
            request, 'Please login to access your liked scholarships')
        return HttpResponseRedirect(reverse('login'))
    elif(localId == ''):
        messages.warning(request, 'Please Log out and log in.')
        return HttpResponseRedirect(reverse('profile'))
    localId = auth.get_account_info(localId)['users'][0]['localId']
    username = database.child("users").child(localId).child('name').get().val()
    likedScholarships = []
    for sc in database.child("scholarships").get().each():
        # Only allow to like verified scholarships
        if(sc.val()['verified']):
            for uid in sc.val()['likedBy']:
                if(uid == str(localId)):
                    likedScholarships.append(sc.val())
    if(len(likedScholarships) == 0):
        messages.info(request, 'No active liked scholarships found')
    context = {
        'username': username,
        "userLoggedIn": True,
        'likedScholarships': likedScholarships
    }
    return render(request, 'liked.html', context)


def logout(request):
    """
        Logouts user
    """
    try:
        # Removes uid from session and logouts user
        del request.session['uid']
    except KeyError:
        print("Unable to log out")
        messages.info(request, 'Unable to log out')
    return HttpResponseRedirect(reverse('index'))


def change_password(request):
    """
        Sends chage password mail to user
    """
    localId = checkIfAuthUser(request)
    if(localId == False):
        messages.error(request, 'Please Login to Change Password')
        return HttpResponseRedirect(reverse('login'))
    elif(localId == ''):
        messages.warning(request, 'Please Log out and log in.')
        return HttpResponseRedirect(reverse('profile'))
    # Sends password reset email
    auth.send_password_reset_email(auth.get_account_info(
        request.session['uid'])['users'][0]['email'])
    messages.info(request, 'Password reset email has been send please check.')
    return HttpResponseRedirect(reverse('profile'))


def post_like(request, id):
    """
        Likes scholarship
    """
    localId = checkIfAuthUser(request)
    if(localId == False):
        messages.error(request, 'Please Login to Like Scholarships')
        return HttpResponseRedirect(reverse('login'))
    elif(localId == ''):
        messages.warning(request, 'Please Log out and log in.')
        return HttpResponseRedirect(reverse('profile'))
    userId = auth.get_account_info(localId)[
        'users'][0]['localId']

    totalLikes = database.child("scholarships").child(
        id).child('likes').get().val()
    if(totalLikes > 0):
        for likedBy in database.child("scholarships").child(id).child("likedBy").get().val():
            if(likedBy == userId):
                messages.info(
                    request, 'You have already liked this scholarship.')
                return HttpResponseRedirect(reverse('search'))
        likedBy = database.child("scholarships").child(
            id).child('likedBy').get().val()
        likedBy.append(userId)
        database.child("scholarships").child(id).update(
            {"likes": totalLikes + 1, 'likedBy': likedBy})
    else:
        likedBy = [userId]
        database.child("scholarships").child(id).update(
            {"likes": totalLikes + 1, 'likedBy': likedBy})
        return HttpResponseRedirect(reverse('search'))


def post_report(request, id):
    """
        Reports Scholarship
    """
    localId = checkIfAuthUser(request)
    if(localId == False):
        messages.error(request, 'Please Login to Report Scholarships')
        return HttpResponseRedirect(reverse('login'))
    elif(localId == ''):
        messages.warning(request, 'Please Log out and log in.')
        return HttpResponseRedirect(reverse('profile'))
    totalReports = database.child("scholarships").child(
        id).child('reports').get().val() + 1
    database.child("scholarships").child(id).update({"reports": totalReports})
    return HttpResponseRedirect(reverse('scholarship', args=[id]))


def post_comment(request):
    """
        Add comment to scholarship
    """
    localId = checkIfAuthUser(request)
    if(localId == False):
        messages.error(request, 'Please Login to Report Scholarships')
        return HttpResponseRedirect(reverse('login'))
    elif(localId == ''):
        messages.warning(request, 'Please Log out and log in.')
        return HttpResponseRedirect(reverse('profile'))
    userId = auth.get_account_info(localId)['users'][0]['localId']
    if(request.method == 'POST'):
        id = request.POST.get('id')
        comment = request.POST.get('comment')
        commentData = {
            'by': userId,
            'comment': comment
        }
        try:
            comments = database.child('scholarships').child(
                id).child('comments').get().val()
        except:
            comments = []
        comments.append(commentData)
        database.child('scholarships').child(
            id).update({"comments": comments})
        return HttpResponseRedirect(reverse('scholarship', args=[id]))


def post_delete(request):
    """
        Delete scholarship Only can be done by admin
    """
    userId = checkIfAuthUser(request)
    if(userId == False):
        messages.error(request, 'Please Login')
        return HttpResponseRedirect(reverse('login'))
    elif(userId == ''):
        messages.warning(request, 'Please Log out and log in.')
        return HttpResponseRedirect(reverse('profile'))
    localId = auth.get_account_info(userId)['users'][0]['localId']
    if(not database.child('users').child(localId).child('role').get().val() == 'admin'):
        messages.warning(request, 'Unauthorized Page')
        return HttpResponseRedirect(reverse('index'))
    if(request.method == 'POST'):
        scId = request.POST.get('id')
        database.child('scholarships').child(scId).remove()
        return HttpResponseRedirect(reverse('admin_verify'))


def admin(request):
    """
        Controller to admin page
        Only admin can be allowed
    """
    userId = checkIfAuthUser(request)
    if(userId == False):
        messages.error(request, 'Please Login')
        return HttpResponseRedirect(reverse('login'))
    elif(userId == ''):
        messages.warning(request, 'Please Log out and log in.')
        return HttpResponseRedirect(reverse('profile'))
    localId = auth.get_account_info(userId)['users'][0]['localId']
    if(not database.child('users').child(localId).child('role').get().val() == 'admin'):
        messages.warning(request, 'Unauthorized Page')
        return HttpResponseRedirect(reverse('index'))
    name = database.child('users').child(localId).child('name').get().val()

    context = {
        'name': name,
        'userLoggedIn': True,
        'isAdmin': True
    }
    return render(request, 'admin.html', context)


def admin_verify(request):
    """
        Controller to admin verify/unverify scholarships page
        Only admin can be allowed
    """
    userId = checkIfAuthUser(request)
    if(userId == False):
        messages.error(request, 'Please Login')
        return HttpResponseRedirect(reverse('login'))
    elif(userId == ''):
        messages.warning(request, 'Please Log out and log in.')
        return HttpResponseRedirect(reverse('profile'))
    localId = auth.get_account_info(userId)['users'][0]['localId']
    if(not database.child('users').child(localId).child('role').get().val() == 'admin'):
        messages.warning(request, 'Unauthorized Page')
        return HttpResponseRedirect(reverse('index'))
    if(request.method == 'POST'):
        id = request.POST.get('id')
        newvalue = not database.child("scholarships").child(
            id).child('verified').get().val()
        database.child("scholarships").child(id).update({'verified': newvalue})
    scholarships = []
    for s in database.child("scholarships").get().each():
        scholarships.append(s.val())
    context = {
        'verify_active': 'active',
        'scholarships': scholarships,
        'userLoggedIn': True,
        'isAdmin': True,
    }
    return render(request, 'admin_verify.html', context)


def admin_users(request):
    """
        Controller to admin to veiw users page
        Only admin can be allowed
    """
    userId = checkIfAuthUser(request)
    if(userId == False):
        messages.error(request, 'Please Login')
        return HttpResponseRedirect(reverse('login'))
    elif(userId == ''):
        messages.warning(request, 'Please Log out and log in.')
        return HttpResponseRedirect(reverse('profile'))
    localId = auth.get_account_info(userId)['users'][0]['localId']
    if(not database.child('users').child(localId).child('role').get().val() == 'admin'):
        messages.warning(request, 'Unauthorized Page')
        return HttpResponseRedirect(reverse('index'))
    usersList = []
    for user in database.child("users").get().each():
        u = user.val()
        u['id'] = user.key()
        usersList.append(u)
    context = {
        'users_active': 'active',
        'users': usersList,
        'userLoggedIn': True,
        'isAdmin': True,
    }
    return render(request, 'admin_users.html', context)


def profile(request):
    """
        Controller to profile 
        Authorized to logged in users only 
    """
    localId = checkIfAuthUser(request)
    if(localId == False):
        messages.error(request, 'Please Login to View your profile')
        return HttpResponseRedirect(reverse('login'))
    elif(localId == ''):
        messages.info(request, 'Please Login Again')
        return HttpResponseRedirect(reverse('logout'))
    userId = auth.get_account_info(localId)['users'][0]['localId']
    userInfo = {}
    for data in database.child('users').child(userId).get().each():
        userInfo[data.key()] = data.val()
    context = {
        'userLoggedIn': True,
        'userInfo': userInfo
    }
    try:
        context['isAdmin'] = database.child('users').child(auth.get_account_info(request.session['uid'])[
            'users'][0]['localId']).child('role').get().val() == 'admin'
    except:
        pass
    return render(request, 'profile.html', context)
