def noindex_middleware(get_response):
    '''
    Drží prostredie mimo vyhľadávačov. Hlavička a nie robots.txt: crawler musí
    URL smieť stiahnuť, aby noindex uvidel, a len noindex vyhodí z indexu aj
    URL, ktoré už pozná. Platí len pre to, čo odpovedá Django - /media
    servuje nginx na serveri.
    '''
    def middleware(request):
        response = get_response(request)
        response['X-Robots-Tag'] = 'noindex, nofollow'
        return response

    return middleware
