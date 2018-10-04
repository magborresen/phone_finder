import http.client
import urllib
import ssl


def send_to_mag(json_data, description):

    context = ssl._create_unverified_context()

    split_data = json_data['name'].split(',')

    model = split_data[0]
    storage = split_data[1]
    color = split_data[2]
    phone_link = json_data['url']
    price = (json_data['offers']['price'] + " " +
             json_data['offers']['priceCurrency'])

    message = (model + " " + storage + " " + color + " " + price +
               description + "\n" + phone_link)

    conn = http.client.HTTPSConnection("api.pushover.net:443", context=context)
    conn.request("POST", "/1/messages.json",
                 urllib.parse.urlencode({
                  "token": "amixpwygaccoj63h31amtebvm1tdt5",
                  "user": "up7pvqk3daesi4bp3bc6h85qbsf2ha",
                  "message": message,
                  "title": "Ny {} til salg".format(model)
                  }), {"Content-type": "application/x-www-form-urlencoded"})
    conn.getresponse()
