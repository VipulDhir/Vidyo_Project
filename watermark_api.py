from flask import request, send_file
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import os
import datetime
from main import app, mongo
from flask_cors import cross_origin

UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER


ALLOWED_VIDEO_EXTENSIONS={'mp4','avi','mkv'}
ALLOWED_IMAGE_EXTENSIONS={'png','jpg','jpeg'}


def allowed_file(filename,allowed_extensions):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in allowed_extensions


def add_watermark(video_path,watermark_path,position='bottom-right'):
    video_clip=VideoFileClip(video_path)
    watermark_clip=ImageClip(watermark_path,duration=video_clip.duration)

    # Set position based on user input
    if position == 'top-left':
        watermark_position=(0,0)
    elif position == 'top-right':
        watermark_position=(video_clip.size[0] - watermark_clip.size[0],0)
    elif position == 'bottom-left':
        watermark_position=(0,video_clip.size[1] - watermark_clip.size[1])
    else:  # Default to 'bottom-right'
        watermark_position=(video_clip.size[0] - watermark_clip.size[0],video_clip.size[1] - watermark_clip.size[1])

    # Composite video with watermark
    watermarked_clip=CompositeVideoClip([video_clip,watermark_clip.set_position(watermark_position).set_opacity(0.5)])

    # Create a path for the watermarked video file
    watermarked_filename=f"{secure_filename(os.path.splitext(os.path.basename(video_path))[0])}_watermarked.mp4"
    watermarked_filepath=os.path.join(app.config['DOWNLOAD_FOLDER'],watermarked_filename)

    # Write the watermarked video to the file
    watermarked_clip.write_videofile(watermarked_filepath,codec='libx264',audio_codec='aac')

    # Close the clips to release resources
    video_clip.close()
    watermark_clip.close()
    watermarked_clip.close()

    return watermarked_filepath

@cross_origin()
def add_watermark_endpoint():
    if 'video' not in request.files or 'watermark' not in request.files:
        return {'error': 'No file part for video or watermark'},400

    video_file=request.files['video']
    watermark_file=request.files['watermark']
    position=request.form.get('position','bottom-right')

    if video_file.filename == '' or watermark_file.filename == '':
        return {'error': 'No selected video or watermark file'},400

    if allowed_file(video_file.filename,ALLOWED_VIDEO_EXTENSIONS) and \
            allowed_file(watermark_file.filename,ALLOWED_IMAGE_EXTENSIONS):
        video_filename=secure_filename(video_file.filename)
        video_filepath=os.path.join(app.config['UPLOAD_FOLDER'],video_filename)
        video_file.save(video_filepath)

        watermark_filename=secure_filename(watermark_file.filename)
        watermark_filepath=os.path.join(app.config['UPLOAD_FOLDER'],watermark_filename)
        watermark_file.save(watermark_filepath)

        try:
            # Add watermark to the video
            watermarked_filepath=add_watermark(video_filepath,watermark_filepath,position)

            # Save information in the database
            user=request.form.get('user','unknown_user')
            timestamp=datetime.datetime.now()

            db=mongo.db.videos
            db.insert_one({
                'user': user,
                'timestamp': timestamp,
                'video_filename': video_filename,
                'watermark_filename': watermark_filename,
                'watermark_position': position,
                'watermarked_filename': os.path.basename(watermarked_filepath),
            })

            # Return the watermarked video file as a response
            return send_file(watermarked_filepath,as_attachment=True)

        except Exception as e:
            return {'error': f'An error occurred: {str(e)}'},500

    return {'error': 'Invalid file format'},400