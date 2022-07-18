
from geopy.geocoders import Nominatim
locator = Nominatim(user_agent="Jamie")
location = locator.geocode("Cincinnati, Ohio, US")
print("Latitude = {}, Longitude = {}".format(location.latitude, location.longitude))