from math import radians,sin,cos,asin,sqrt

def haversine_km(lat1,lon1,lat2,lon2):
    dlat=radians(lat2-lat1); dlon=radians(lon2-lon1)
    a=sin(dlat/2)**2+cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 6371.0088*2*asin(sqrt(a))
