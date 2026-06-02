from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/extract")
def extract(url: str):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = []
            
            # itag 18 = 360p mp4 with audio+video combined
            # itag 22 = 720p mp4 with audio+video combined
            COMBINED_ITAGS = [18, 22]
            
            for f in info.get('formats', []):
                itag = f.get('format_id')
                try:
                    itag_int = int(itag)
                except:
                    itag_int = -1
                
                if itag_int in COMBINED_ITAGS and f.get('url'):
                    quality = f.get('format_note') or f.get('height')
                    filesize = f.get('filesize') or f.get('filesize_approx')
                    
                    formats.append({
                        'quality': f"{quality}p" if isinstance(quality, int) else quality,
                        'ext': f.get('ext'),
                        'url': f.get('url'),
                        'filesize_mb': round(filesize / (1024 * 1024), 2) if filesize else None,
                    })

            # sort by quality ascending
            quality_order = {'360p': 1, '720p': 2}
            formats.sort(key=lambda x: quality_order.get(x['quality'], 99))

            return {
                "success": True,
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration'),
                "channel": info.get('channel'),
                "formats": formats
            }

    except Exception as e:
        return {"success": False, "error": str(e)}
