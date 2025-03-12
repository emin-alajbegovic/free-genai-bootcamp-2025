## Create new Conda Enviroment

Setup conda enviroment for the whisper.ipynb

```bash
conda create -n asr-task python=3.11
conda activate asr-task
conda install -c conda-forge ipykernel
```

## Reset Conda Enviroment

```bash
conda deactivate
conda remove -n asr-task --all
```

## Audio Format File

```sh
ffmpeg -i wake_up.wav -ar 24000 -c:a pcm_f32le -ac 1 wake_up_converted.wav
```

## WhisperX

OpenWhisper does not do word-by-word.
We can use whisperx

```sh
pip install whisperx
whisperx --model large --language ja wake_up_converted.wav
```

whisperx is very hard to install because it needs a specific version of cuda eg. 8 and pytorch version 

Lets try using a docker container:


docker run --gpus all -it -v ".:/app" ghcr.io/jim60105/whisperx:large-v3-ja -- --output_format json wake_up_converted.wav


Possible outputs:
def get_writer(
    output_format: str, output_dir: str
) -> Callable[[dict, TextIO, dict], None]:
    writers = {
        "txt": WriteTXT,
        "vtt": WriteVTT,
        "srt": WriteSRT,
        "tsv": WriteTSV,
        "json": WriteJSON,
    }
https://github.com/m-bain/whisperX/blob/main/whisperx/utils.py