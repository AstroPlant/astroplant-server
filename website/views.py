from django.shortcuts import render

def index(request):
    context = {}
    return render(request, 'website/index.html', context)
    
def map(request):
    # Todo: programmatically add the markers of the AstroPlant kits.
    # Note that we don't use GeoDjango; it requires a heavy gdal setup. All
    # we need is a simple map, and a full gdal setup would just make deployment
    # more difficult
    context = {}
    return render(request,'website/map.html', context)
