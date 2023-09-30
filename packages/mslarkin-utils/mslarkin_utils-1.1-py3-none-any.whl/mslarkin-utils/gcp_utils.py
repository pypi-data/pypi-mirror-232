import os, re
import requests 

def get_resource_from_path(resource_path):
    result = re.search(r'.*/(.*)$',resource_path) 
    return result.group(1)

def get_project_id():
    gcp_project_id = requests.get(
        'http://metadata.google.internal/computeMetadata/v1/project/project-id', headers={'Metadata-Flavor': 'Google'}).text
    return gcp_project_id

def get_project_number():
    gcp_project_number = requests.get(
        'http://metadata.google.internal/computeMetadata/v1/project/numeric-project-id', headers={'Metadata-Flavor': 'Google'}).text
    return gcp_project_number

def get_instance_id():
    instance_id = requests.get(
        'http://metadata.google.internal/computeMetadata/v1/instance/id', headers={'Metadata-Flavor': 'Google'}).text
    return instance_id

def get_instance_id_short():
    instance_id = get_instance_id()
    short_id = re.search(r'.*(.{10})$', instance_id)
    return short_id.group(1)

def get_gcp_region():
    r = requests.get(
        'http://metadata.google.internal/computeMetadata/v1/instance/region', headers={'Metadata-Flavor': 'Google'}).text
    region = get_resource_from_path(r)
    return region

def get_service_id():
    service_id = os.environ.get('K_SERVICE', os.environ.get('GAE_SERVICE'))
    return service_id

def get_revision_id():
    revision_id = os.environ.get('K_REVISION', os.environ.get('GAE_VERSION'))
    return revision_id



