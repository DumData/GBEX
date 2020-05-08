def upload_a_file_to_gbex(file_path: str, auth_token: str, object_url: str, field_name: str, max_chunk_size_bytes: int=10000000):
    """
    This function uploads a file to GBEX.
    Basically it first uploads the file to the server and then it tells GBEX that there is a file that it would like to associate with an row object+field

    file_path: Path to file (e.g. /some/place/file.txt)
    client_session: a requests session object
    object_url: url to the object for which you wish to upload a file (e.g. http://localhost/api/Strain/1/)
    field_name: Name of file field on the object
    max_chunk_size_bytes: File gets split into chunks of "max_chunk_size_bytes". Depending on your internet connection, a higher number might be faster.
    """
    from os.path import getsize, basename
    from urllib.parse import unquote
    import requests
    # create a session and add the auth token to it
    client_session = requests.session()
    client_session.headers.update({'Authorization': f'Token {auth_token}'})
    # first we do a pre-upload of the file. This can be done in multiple chunks.
    # We need a file_dict, a data dict and a url for the pre_upload
    the_file = open(file_path, 'rb')
    file_size = getsize(file_path)
    full_chunks = int(file_size/max_chunk_size_bytes)
    size_of_last_chunk = file_size-(full_chunks*max_chunk_size_bytes)
    
    if size_of_last_chunk == 0:  # last chunk is special so if the file happens to be divisible by chunk size then remove last chunk
        full_chunks -= 1
    url_parts = object_url.split("/")
    pre_upload_url = f"{url_parts[0]}//{url_parts[2]}/resumable_upload"
    print(f"Attempting to pre-upload file in {full_chunks+1} chunk(s)")
    for chunk_i in range(full_chunks):
        print(f"Uploading chunk {chunk_i+1}")
        data = {
            "resumableChunkNumber":chunk_i+1,
            "resumableCurrentChunkSize": max_chunk_size_bytes,
            "resumableTotalSize":file_size,
            "resumableFilename":basename(file_path),
        }
        res = client_session.post(pre_upload_url, files={'file': the_file.read(max_chunk_size_bytes)}, data=data)
        print(f"\t{res}: {res.content.decode()}")
    
    # upload last chunk
    print("Uploading final chunk")
    data = {
        "resumableChunkNumber":full_chunks+1,
        "resumableCurrentChunkSize": size_of_last_chunk,
        "resumableTotalSize":file_size,
        "resumableFilename":basename(file_path),
    }
    res = client_session.post(pre_upload_url, files={'file': the_file.read()}, data=data)
    uploaded_as = unquote(res.content.decode())
    print(f"\t{res}: File successfully uploaded and named: {basename(uploaded_as)}")
    # if everything went well, the server now has the file in a temporary directory.
    # We now got a filename in res.content because the server might have changed the name to ensure uniqueness of the filename
    
    empty_file_dict = {field_name: (basename(uploaded_as), ' ')}
    if not object_url.endswith("/"):
        object_url = object_url + "/"
    print("Attempting to attach file to object")
    res2 = client_session.patch(object_url, files=empty_file_dict)
    print(res2)
    return res2.json()
