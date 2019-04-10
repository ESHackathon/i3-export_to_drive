from __future__ import print_function
import sys
import json
# import pickle
# import os.path
from googleapiclient.discovery import build
# from google.auth.transport.requests import Request
import mimetypes

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.http import MediaFileUpload


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']


def main():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scopes=SCOPES
    )

    json_file = json.loads(open(sys.argv[1]).read())
    local_filename = json_file["local_filename"]
    target_filename = json_file["target_filename"]
    folder_name = json_file["folder_name"]
    email = json_file["email"]

    service = build('drive', 'v3', credentials=credentials)

    folders = find_files_folder(service, folder_name)
    if len(folders) > 0:
        folder_id = folders[0]["id"]
    else:
        folder_id = create_folder(service, folder_name)

    already_has_permission = check_permissions(service, folder_id, email)

    print("Folder id:", folder_id)

    file_id = update_file(service, local_filename, target_filename, folder_id=folder_id)
    if not file_id:
        file_id = upload_new_file(service, local_filename, target_filename, folder_id=folder_id)
        print("file created:", file_id)
    else:
        print("file updated:", file_id)

    print("File id:", folder_id)

    if not already_has_permission:
        share_files(service, folder_id, email)

    # read_files(service)


def check_permissions(service, file_id, email):
    permissions = service.permissions().list(fileId=file_id).execute()
    already_has_permission = False
    for permission in permissions["permissions"]:
        permission_email = service.permissions().get(
            fileId=file_id,
            permissionId=permission["id"],
            fields='emailAddress'
        ).execute()['emailAddress']
        if permission_email == email:
            already_has_permission = True
    return already_has_permission


def get_mimetype(local_path, mimetype):
    if mimetype is None:
        try:
            mimetype = mimetypes.MimeTypes().guess_type(local_path)[0]
        except:
            pass
    return mimetype


def find_files_folder(service, name, mimetype='application/vnd.google-apps.folder', parent_folder=None):
    mimetype = get_mimetype(name, mimetype)
    query = "name = '%s' and mimeType='%s'" % (name, mimetype)
    if parent_folder is not None:
        query += " and '%s' in parents" % parent_folder
    while True:
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name)',
            pageToken=None
        ).execute()
        return response.get('files', [])


def read_files(service):
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))


def create_folder(service, folder_name):
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    file = service.files().create(
        body=file_metadata,
        fields='id'
    ).execute()
    folder_id = file.get('id')
    return folder_id


def upload_new_file(service, local_path, target_path, mimetype=None, folder_id=None):
    mimetype = get_mimetype(local_path, mimetype)
    file_metadata = {'name': target_path}
    if folder_id is not None:
        file_metadata['parents'] = [folder_id]
    media = MediaFileUpload(local_path, mimetype=mimetype)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    return file.get('id')


def update_file(service, local_path, target_path, mimetype=None, folder_id=None):
    files = find_files_folder(service, target_path, mimetype=None, parent_folder=folder_id)
    if len(files) > 0:
        media = MediaFileUpload(local_path, mimetype=mimetype)
        file = service.files().update(
            fileId=files[0]["id"],
            media_body=media
        ).execute()
        return file.get('id')
    return False


def share_files(service, file_or_folder_id, email):
    def callback(request_id, response, exception):
        if exception:
            # Handle error
            print(exception)
        else:
            print("Permission Id: %s" % response.get('id'))

    batch = service.new_batch_http_request(callback=callback)
    user_permission = {
        'type': 'user',
        'role': 'reader',
        'emailAddress': email
    }
    batch.add(service.permissions().create(
        fileId=file_or_folder_id,
        body=user_permission,
        fields='id',
    ))
    batch.execute()

if __name__ == '__main__':
    main()
