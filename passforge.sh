#!/bin/bash

# Start the Angular frontend
cd pass_componenet
ng serve &
ANGULAR_PID=$!

# Start the Flask backend app

cd ..
python app.py &
FLASK_PID=$!

echo "Both the Flask backend and Angular frontend are running!"

# Wait for either process to finish
wait $FLASK_PID $ANGULAR_PID

