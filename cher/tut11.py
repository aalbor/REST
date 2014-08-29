


@login_required(login_url='/login/')
def getdisk(request):
    try:
        diskusage = get_disk()
    except Exception:
        diskusage = None

    data = json.dumps(diskusage)
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(data)
    return response
