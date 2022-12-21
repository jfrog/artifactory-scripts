import requests

def deep_clean():

    base_url = 'http://localhost:8081/artifactory/'
    base_name_to_search = "Test-SNAPSHOT-*.ear"

    headers = {'content-type': 'text/plain'}
    data = 'items.find({"name":{"$match":"%s"}})' % base_name_to_search
    limit_number = 4
    response = requests.post(base_url+'api/search/aql', auth=('admin', 'NewPassword'), headers=headers, data=data)


    for result in eval(response.text)["results"]:

        name = result['name']
        path = result['path'] + '/'
        repo = result['repo']
        if path == './':
            path = ''

        full_path = repo + '/' + path + name

        artifact_url = base_url + full_path
        version = name.split('-')[-1].split('.')[0]

        if int(version) < limit_number:
            print(full_path)
            print(artifact_url)
            requests.delete(artifact_url, auth=('admin', 'NewPassword'))

if __name__ == '__main__':
    deep_clean()

