# Comic Scans

<p align="center">
A project to index a manga and make the entirety of its text searchable.
</p>

This project is powered by [cubari.moe](https://cubari.moe) for the images.
The OCR model used is [GLM OCR](https://huggingface.co/zai-org/GLM-OCR), which is the most effective from our tests.


## Setup

Ideally you should use a package manager to set this thing up like [uv](https://github.com/astral-sh/uv)
```
uv venv --python 3.12
source .venv/bin/activate
uv pip install -qr requirements.txt
```


## Usage

Run
```
python comic_ocr.py -i <manga-link>
```

Or you can skip the parameter and it'll ask you automatically

### Running on local images

TBA

## License

This project is licensed under MIT