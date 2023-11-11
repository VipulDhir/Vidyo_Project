from flask import request,send_file
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip
import os
import datetime
from main import app,mongo
from flask_cors import cross_origin

UPLOAD_FOLDER='uploads'
DOWNLOAD_FOLDER='downloads'

app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER']=DOWNLOAD_FOLDER

ALLOWED_EXTENSIONS={'mp4','avi','mkv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


def check_mongo_connection():
    try:
        # Attempt to connect to the "users" collection in the MongoDB
        mongo.db.users.find_one()
        return True
    except Exception as e:
        print(f'Failed to connect to MongoDB: {str(e)}')
        return False


# Check MongoDB connection on application startup
if check_mongo_connection():
    print('Connected to MongoDB')
else:
    print('Failed to connect to MongoDB')


def extract_audio(video_path):
    clip=VideoFileClip(video_path)
    audio=clip.audio

    # Create a path for the audio file
    audio_filename=f"{secure_filename(os.path.splitext(os.path.basename(video_path))[0])}.mp3"
    audio_filepath=os.path.join(app.config['DOWNLOAD_FOLDER'],audio_filename)

    # Write the audio to the file
    audio.write_audiofile(audio_filepath,codec='mp3')

    # Release the resources held by VideoFileClip
    audio.close()
    clip.close()

    # Return the path of the saved audio file
    return audio_filepath


@cross_origin()
def extract_audio_endpoint():
    if 'file' not in request.files:
        return {'error': 'No file part'},400

    file=request.files['file']

    if file.filename == '':
        return {'error': 'No selected file'},400

    if file and allowed_file(file.filename):
        filename=secure_filename(file.filename)
        filepath=os.path.join(app.config['UPLOAD_FOLDER'],filename)
        file.save(filepath)

        try:
            # Extract audio
            audio_filepath=extract_audio(filepath)

            # Save information in the database
            user=request.form.get('user','unknown_user')
            timestamp=datetime.datetime.now()

            db=mongo.db.videos
            db.insert_one({
                'user': user,
                'timestamp': timestamp,
                'filename': filename,
            })

            # Return the saved audio file as a response
            return send_file(audio_filepath,as_attachment=True)

        except Exception as e:
            return {'error': f'An error occurred: {str(e)}'},500

    return {'error': 'Invalid file format'},400
