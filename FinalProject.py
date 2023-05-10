from flask import Flask, render_template, request
import requests
import pandas as pd
from twilio.rest import Client

app = Flask(__name__)

# Weather API key from OpenWeatherMap
weatherApiKey = "aa76cf70a8f2c043cc058f454835cfbc"

# Twilio account SID and auth token
twilioSid = "AC98fa068e2ee20d8966ea3ab8fdc98d9c"
twilioToken = "f885d36094430fd1b357a326a96a3b45"

# Twilio phone number and recipient phone number
twilioPhoneNumber = "+18622414672"
recipientPhoneNumber = "+18622414672"

def get_weather_data(zip_code):
    url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={weatherApiKey}&units=imperial"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        description = data['weather'][0]['description']
        rain_chance = data['clouds']['all']

        weather_data = pd.DataFrame({
            'temperature': [temperature],
            'humidity': [humidity],
            'wind_speed': [wind_speed],
            'description': [description],
            'rain_chance': [rain_chance]
        })

        return weather_data
    else:
        return None

@app.route('/', methods=['POST', 'GET'])
def home_page():
    if request.method == 'POST':
        zip_code = request.form['zipCode']
        weather_data = get_weather_data(zip_code)

        if weather_data is not None:
            # Send a weather alert if the temperature is below a certain threshold
            if weather_data['temperature'][0] < 40:
                client = Client(twilioSid, twilioToken)
                message = client.messages.create(
                    body="Temperature is below 40 degrees Fahrenheit in your area. Stay warm!",
                    from_=twilioPhoneNumber,
                    to=recipientPhoneNumber
                )
                print(message.sid)

            return render_template('HomePage.html', weather_data=weather_data.to_dict())
        else:
            return "Error retrieving weather data."
    else:
        return render_template('HomePage.html')

if __name__ == '__main__':
    app.run(debug=True)
