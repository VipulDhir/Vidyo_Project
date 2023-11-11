from main import app
from watermark_api import add_watermark_endpoint
from extracting_audio import extract_audio_endpoint

app.add_url_rule('/extract_audio', view_func=extract_audio_endpoint, methods=['POST'])
app.add_url_rule('/add_watermark', view_func=add_watermark_endpoint, methods=['POST'])
