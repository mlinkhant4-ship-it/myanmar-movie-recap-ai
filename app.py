import os, uuid, subprocess, shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

ROOT = Path(__file__).parent.resolve()
DATA = ROOT / "jobs"
DATA.mkdir(exist_ok=True)
app = FastAPI(title="Myanmar Movie Recap AI")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr[-2500:])
    return p.stdout.strip()

def process_job(job_id, video_path, voice, style):
    folder = DATA / job_id
    try:
        (folder / "status.txt").write_text("Extracting audio...")
        client = OpenAI()
        audio = folder / "movie_audio.mp3"
        run(["ffmpeg", "-y", "-i", str(video_path), "-vn", "-ac", "1", "-ar", "16000",
             "-b:a", "48k", str(audio)])

        # Split into 10-minute chunks to avoid oversized transcription requests.
        duration = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "default=noprint_wrappers=1:nokey=1", str(audio)]))
        transcripts = []
        chunk_seconds = 600
        for start in range(0, int(duration) + 1, chunk_seconds):
            part = folder / f"audio_{start}.mp3"
            run(["ffmpeg", "-y", "-ss", str(start), "-i", str(audio), "-t", str(chunk_seconds),
                 "-c:a", "libmp3lame", "-b:a", "48k", str(part)])
            if part.stat().st_size < 1000:
                continue
            (folder / "status.txt").write_text(f"Transcribing audio: {min(start+chunk_seconds, int(duration))}/{int(duration)} seconds")
            with open(part, "rb") as f:
                result = client.audio.transcriptions.create(model="gpt-4o-mini-transcribe", file=f)
            transcripts.append(result.text)
            part.unlink(missing_ok=True)

        transcript = "\n".join(transcripts)
        (folder / "transcript.txt").write_text(transcript, encoding="utf-8")
        (folder / "status.txt").write_text("Writing Burmese recap script...")
        prompt = f"""You are a Burmese-language movie recap writer. Create an original, concise Burmese recap narration based on the plot information below.
Style: {style}
Requirements:
- Write natural spoken Myanmar Burmese, not a literal line-by-line translation.
- Retell the main story in your own words, in chronological order.
- Do not reproduce dialogue or long passages from the film.
- Avoid inventing events not supported by the transcript.
- Use clear paragraphs suitable for voice narration.
- Keep it reasonably concise.
TRANSCRIPT:
{transcript[:100000]}"""
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        script = response.output_text.strip()
        if not script:
            raise RuntimeError("AI did not return a recap script.")
        (folder / "recap.txt").write_text(script, encoding="utf-8")

        (folder / "status.txt").write_text("Generating Burmese voiceover...")
        # TTS is chunked by paragraph to keep each request manageable.
        paragraphs = [p.strip() for p in script.split("\n") if p.strip()]
        audio_parts = []
        for i, paragraph in enumerate(paragraphs):
            out = folder / f"voice_{i:03}.mp3"
            speech = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice=voice,
                input=paragraph,
                instructions="Speak clearly and naturally in Myanmar Burmese, like a calm movie recap narrator."
            )
            speech.stream_to_file(out)
            audio_parts.append(out)

        concat_file = folder / "concat.txt"
        concat_file.write_text("".join(f"file '{p.as_posix()}'\n" for p in audio_parts), encoding="utf-8")
        voiceover = folder / "voiceover.mp3"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
             "-c:a", "libmp3lame", "-b:a", "128k", str(voiceover)])

        # SRT from narration paragraph timings, using measured TTS segment durations.
        def fmt(t):
            ms = int(round(t * 1000))
            h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
            return f"{h:02}:{m:02}:{s:02},{ms:03}"
        cursor, srt_lines = 0.0, []
        for i, (paragraph, part) in enumerate(zip(paragraphs, audio_parts), 1):
            d = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                           "-of", "default=noprint_wrappers=1:nokey=1", str(part)]))
            srt_lines += [str(i), f"{fmt(cursor)} --> {fmt(cursor+d)}", paragraph, ""]
            cursor += d
        (folder / "subtitles.srt").write_text("\n".join(srt_lines), encoding="utf-8")

        # Draft montage: samples short clips at regular intervals and uses the generated narration.
        # This is a rough first cut, not intelligent scene selection.
        (folder / "status.txt").write_text("Building draft recap video...")
        clips_dir = folder / "clips"
        clips_dir.mkdir(exist_ok=True)
        source_duration = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                     "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)]))
        voice_duration = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                    "-of", "default=noprint_wrappers=1:nokey=1", str(voiceover)]))
        clip_len = 5.0
        n = max(1, int(voice_duration // clip_len) + 1)
        clip_paths = []
        for i in range(n):
            start = min(max(0, source_duration - clip_len), (i / max(1, n-1)) * max(0, source_duration - clip_len))
            cp = clips_dir / f"clip_{i:04}.mp4"
            run(["ffmpeg", "-y", "-ss", str(start), "-i", str(video_path), "-t", str(clip_len),
                 "-an", "-vf", "scale=1280:-2,fps=25,format=yuv420p", "-c:v", "libx264",
                 "-preset", "veryfast", "-crf", "25", str(cp)])
            clip_paths.append(cp)
        montage_list = folder / "clips.txt"
        montage_list.write_text("".join(f"file '{p.as_posix()}'\n" for p in clip_paths), encoding="utf-8")
        silent_video = folder / "montage.mp4"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(montage_list),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "25", str(silent_video)])
        output = folder / "recap_video.mp4"
        run(["ffmpeg", "-y", "-i", str(silent_video), "-i", str(voiceover), "-map", "0:v:0",
             "-map", "1:a:0", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", str(output)])
        (folder / "status.txt").write_text("DONE")
    except Exception as e:
        (folder / "status.txt").write_text("ERROR: " + str(e))

@app.get("/", response_class=HTMLResponse)
def home():
    return (ROOT / "static" / "index.html").read_text(encoding="utf-8")

@app.post("/api/jobs")
async def create_job(background_tasks: BackgroundTasks, movie: UploadFile = File(...),
                     voice: str = Form("alloy"), style: str = Form("စိတ်ဝင်စားဖွယ်၊ ရှင်းလင်းပြီး သဘာဝကျသော recap")):
    if not movie.filename.lower().endswith((".mp4", ".mov", ".mkv", ".webm")):
        raise HTTPException(400, "MP4, MOV, MKV သို့မဟုတ် WEBM ဖိုင်သာ တင်ပါ။")
    job_id = uuid.uuid4().hex[:10]
    folder = DATA / job_id
    folder.mkdir()
    video_path = folder / ("source" + Path(movie.filename).suffix.lower())
    with video_path.open("wb") as f:
        shutil.copyfileobj(movie.file, f)
    background_tasks.add_task(process_job, job_id, video_path, voice, style)
    return {"job_id": job_id}

@app.get("/api/jobs/{job_id}")
def job_status(job_id: str):
    folder = DATA / job_id
    if not folder.exists():
        raise HTTPException(404, "Job not found")
    status = (folder / "status.txt").read_text(encoding="utf-8") if (folder / "status.txt").exists() else "Queued"
    return {"status": status, "done": status == "DONE", "error": status.startswith("ERROR")}

@app.get("/api/jobs/{job_id}/files/{filename}")
def get_file(job_id: str, filename: str):
    allowed = {"recap_video.mp4", "recap.txt", "voiceover.mp3", "subtitles.srt", "transcript.txt"}
    if filename not in allowed:
        raise HTTPException(404, "Not found")
    path = DATA / job_id / filename
    if not path.exists():
        raise HTTPException(404, "File is not ready")
    return FileResponse(path, filename=filename)
