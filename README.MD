# Comic Scans

<p align="center">
A project to index a manga and make the entirety of its text searchable.
<br>
<img src="mayonaka.png" alt="example-mayonaka-heart-tune" width="300"/>
<p align="center"><em>Sauce: Mayonaka Heart Tune</em></p>
</p> <br>

This project is powered by [cubari.moe](https://cubari.moe) for the images.
The OCR modes can be chosen between [Surya OCR](https://github.com/VikParuchuri/surya)/[EasyOCR](https://github.com/JaidedAI/EasyOCR) (default: surya).
Will be adding more options in the future

Included example inputs and outputs to help gauge understanding on how it's to be used ([eg. using easyocr](<examples/outputs/Renai Daikou_text.json>))

## Usage

You can run
```
python comic_ocr.py -i <manga-link>
```

Or you can skip the parameter and it'll ask you automatically


### Demo

Run `demo.py` to draw bboxes and annotate a sample image.


### Running on local images

Running the OCR on local images is possible (though arguably not in the best manner)
You'd have to prepend file:/// before your filepaths and then run:

```
python comic_ocr.py -i file:///<json_path> --no_cubari
```

### Advanced Usages

Using gists hosted on Github or elsehwere is possible a similar manner (Using the `--no_cubari` flag)
To switch between models, use the `-m` flag. Currently supported options are surya and easyocr.

## License

This project is licensed under MIT

> [!NOTE] : 
> Not affiliated with Comic Sans MS