## CIJ

### Business Use Case

A language learning portal has videos that provide the transcription.
When a user watches the video on the learning portal the user would like
to see the words highlighted as the video is playing.

### Considerations

The school has already provided accurate transcriptions.
So if we use a transcription services eg. WhisperX to produce
transcriptions we would need to compare the transcriptions with the
provided transcriptions or replace them is the with accurate one and
leaving us with the word-by-word timecodes.

https://www.youtube.com/watch?v=mPz4I9nBxCI


### Pull Transcriptions

```sh
pip install yt-dlp
```

```sh
yt-dlp --list-subs https://www.youtube.com/watch?v=mPz4I9nBxCI      
yt-dlp --skip-download --no-write-auto-subs -sub-langs ja-orig --sub-format srt -o "comic-learn.txt" https://www.youtube.com/watch?v=mPz4I9nBxCI
```

>> cant pull original japanese audio without a password why I'm prompted, I don't know.
>> what password it could be, I dont know.

### Pull Audio

Bitrate: 768 kbps
Audio Sample rate 24.000 KHz
Audio sample ssize 32 bit
Channel 1 (mono)

```sh
yt-dlp -f bestaudio --audio-format wav --audio-quality 0 --postprocessor-args "-ar 24000 -sample_fmt s32 -ac 1 -ab 768k" -o "comic-learn.wav" https://www.youtube.com/watch?v=mPz4I9nBxCI
```

## Convert

yt-dlp refurces to use encoding that we want.
```sh
ffmpeg -i output/comic-learn.wav -ar 24000 -sample_fmt s32 -ac 1 -sample_fmt s32 -acodec pcm_s32le output/comic-learn_standard.wav
```

## Chunk audio into 30 second chunks

place them in a folder called output/chunks

```sh
ffmpeg -i output/comic-learn_standard.wav -f segment -segment_time 30 -c copy -reset_timestamps 1 output/chunks/comic-learn_%03d.wav
```

### WhisperX via Docker

#### Attempt 1
```sh
docker run --gpus all -it -v ".:/app" ghcr.io/jim60105/whisperx:large-v3-ja --
--language Japanese \
--chunk_size 30 \
--output_format json \
./output/comic-learn_standard.wav
```


#### Attempt 2
```sh
docker run --gpus all -it -v ".:/app" ghcr.io/jim60105/whisperx:large-v3-ja -- \
--language Japanese \
--chunk_size 30 \
--output_format json \
--output_dir /app/output \
./output/comic-learn_standard.wav
```


# usage example
```sh
python formatter.py --accurate output/og-comic-learn-short.txt \
--whisperx output/comic-learn_standard-short.json \
--output output/comic-learn_aligned-short.json
```

```sh
python formatter_claude.py --accurate output/og-comic-learn.txt \
--whisperx output/comic-learn_standard.json \
--output output/comic-learn_aligned.json
```