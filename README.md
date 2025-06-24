# Flask GIF App

A simple Flask web application that displays a random fun GIF on each refresh. The app is containerized using Docker and runs on port 80.

## 📸 Demo

The app shows a new GIF every time you refresh the browser. Ideal for lightweight testing or just for fun!

## 🛠 Technologies Used

- Python 3.10
- Flask
- HTML/CSS (Jinja templating)
- Docker

## 📁 Folder Structure

Flask-app/
│
├── app.py # Main Flask application
├── Dockerfile # Docker build file
├── requirements.txt # Python dependencies
├── docker-setup.sh # Optional setup script
├── templates/
│ └── index.html # HTML template

## 🚀 How to Build & Run the App

### 1. Clone the Repository

git clone https://github.com/Harshitha-2003-4/flask-gif-app.git
cd flask-gif-app

### 2.Build the Docker Image

docker build -t my-app .

### 3.Run the Docker Container (on Port 80)

docker run -d -p 80:5000 my-app

### 4.Access the App

Open your browser and go to:http://localhost
Or, if running on an EC2 instance:http://<your-ec2-public-ip>

📌 Notes

The app randomly selects a GIF URL from a predefined list.

A refresh button is provided to load a new GIF without restarting the app.


