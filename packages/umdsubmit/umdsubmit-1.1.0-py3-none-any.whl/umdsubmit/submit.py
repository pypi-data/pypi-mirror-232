import os
import requests
import shutil


def get_course_name():
    f = open(".submit", "r")
    for line in f:
        if line.startswith('courseName'):
            k, v = line.split('=')
            return v.strip()

def get_semester():
    f = open(".submit", "r")
    for line in f:
        if line.startswith('semester'):
            k, v = line.split('=')
            return v.strip()

def get_project_number():
    f = open(".submit", "r")
    for line in f:
        if line.startswith('projectNumber'):
            k, v = line.split('=')
            return v.strip()

def get_course_key():
    f = open(".submit", "r")
    for line in f:
        if line.startswith('courseKey'):
            k, v = line.split('=')
            return v.strip()
        
def get_authtype():
    f = open(".submit", "r")
    for line in f:
        if line.startswith('authentication.type'):
            k, v = line.split('=')
            return v.strip()

def get_base_url():
    f = open(".submit", "r")
    for line in f:
        if line.startswith('baseURL'):
            k, v = line.split('=')
            return v.strip()

def get_submit_url():

    f = open(".submit", "r")
    for line in f:
        if line.startswith('submitURL'):
            k, v = line.split('=')
            return v.strip()
def get_cvs_account():
    if os.path.isfile(".submitUser"):
        f = open(".submitUser", "r")
        for line in f:
            if line.startswith('cvsAccount'):
                k, v = line.split('=')
                return v.strip()
    else:
        auth()
        return get_cvs_account()

def get_one_time_password():
    if os.path.isfile(".submitUser"):
        f = open(".submitUser", "r")
        for line in f:
            if line.startswith('oneTimePassword'):
                k, v = line.split('=')
                return v.strip()
    else:
        auth()
        return get_one_time_password()

def walk_and_add_files(zip_writer):
    for folder, _, files in os.walk("."):
        for file in files:

            if file != ".submitUser":
                file_path = os.path.join(folder, file)
                with open(file_path, "rb") as f:
                    zip_writer.writestr(file_path, f.read())

def auth():
    print("Enter UMD Directory ID: ")
    username = input()
    print("Enter UMD Password: ")
    password = input()
    data = {"loginName" : username, "password" : password, "courseKey" : get_course_key(), "projectNumber" : get_project_number()}
    url_part = f"/eclipse/NegotiateOneTimePassword"
    response = requests.post(get_base_url() + url_part, data = data)
    f = open(".submitUser", "x")
    f.write(response.text)
    print(response.text)

def main():
    
    shutil.make_archive('submit', 'zip', os.getcwd())
    
    
    submit_zip_object =  open('submit.zip', 'rb')
    files = {"submittedFiles": ("submit.zip", submit_zip_object)}
    
    
    
    data = {"courseName" : get_course_name(), "projectNumber" : get_project_number(), "semester" : get_semester(), "courseKey" : get_course_key(), "authentication.type" : get_authtype(), "baseURL" : get_base_url(), "submitURL" : get_submit_url(), "cvsAccount" : get_cvs_account(), "oneTimePassword" : get_one_time_password(), "submitClientTool" : "umdsubmit", "submitClientVersion" : "1.0"}
    response = requests.post(get_submit_url(), files = files, data = data)
    print(response.text)
    os.remove("submit.zip")
