# Vidyo_Project
step-1 open this project in any ide.

step-2 add username and password in main.py file of mongodb atlas cloud

Step-3 make 2 folders in the root directory of the project "uploads" and "downloads" and then copy one video and and an image in uploads folder for the processing

Step-4 run the main.py file

Step-5 we will get a URL link copy that url link on postman and for audio extraction add the endpoint /extract_audio at the end and then go to body section in postman and select form-data in that give key name as file and select type as file and then select value as file fom the uploads folder

Step-6 for watermarking add the endpoint /add_watermark at the end of the url and then go to body section under that select form-data add 3 key-values pairs
      first set key as video type as file and select value as video file
      second set key as watermark and type as file and value as image 
      third set key as position type as text and value as bottom-right , bottom-left, top-left, top-right

step-7 we will get the audio file and watermarked video in downloads folder


----------------------------------------------------------------------------------------

inorder to use docker 

step-1 inside the terminal build a docker image using "docker build -t <image-name> ."

step-2 build a docker container from the image using "docker run -p 5000:5000 <image-name>"

step-3 after the container has been made use command "run docker <container-name>"

step-4 using the docker desktop open the url and test for api using postman like in above steps

