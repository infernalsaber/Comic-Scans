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

Or you can skip the parameter and it'll ask you automatically.

Additional flags:

- `--chapters 1 2 5` — only OCR the specified chapter numbers
- `-f` / `--force` — re-OCR chapters that are already present in the output JSON

### Running on local images

If your image URLs inside the cubari JSON point to locally stored files, they must use the `file:///` scheme. For example:

```json
{
  "title": "My Manga",
  "chapters": {
    "1": {
      "groups": {
        "Group": [
          "file:///home/user/manga/ch1/page01.jpg",
          "file:///home/user/manga/ch1/page02.jpg"
        ]
      }
    }
  }
}
```

To use a local cubari-compatible JSON instead of a cubari link, pass `--file`:

```
python comic_ocr.py --file ./my_series.json
python comic_ocr.py --file ./my_series.json --chapters 1 5 10
python comic_ocr.py --file ./my_series.json -f
```

The JSON must have at minimum a `title` field and a `chapters` field following the cubari series format.
`--file` and `-i` are mutually exclusive.

## License

This project is licensed under MIT