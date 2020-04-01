# COVID-19 in Italy and in the World

> This is a fork from the original project. I would like to thank the original developer [tommasobonomo](https://covid19dashboards.com) for his work.
>
> Original forking reasons include refactored code to use classes and improved translations and performances
> but with time, new features were added, including multiple source support for showing grapsh for all the World
>
> The original project can be found [here](https://github.com/tommasobonomo/covid19-italy/)

Quick streamlit dashboard to visualise the impact of COVID-19 in Italy and in the World

## Demos

A demo site can be found at the following link [link](http://covid-19.electro.tips/).

## Install and run

- Clone the repository
- `pip install -r requirements.txt`
- `PORT=8501 ./setup.sh`
- `streamlit run src/COVID-19-Italy.py`

## Docker

A docker image is available [here](https://hub.docker.com/r/mprenditore/covid-19-dash):

```sh
docker run -p 8501:8501 mprenditore/covid-19-ita-dashboard:latest
```

## Translations

Adding/managing languages can be done without recompile the code.
Inside folder *src/translations* there is a file called ***lang_mapping.yml***. It contains on each line a mapping in the form

> `<language_name>: <language_file`

where:

- **language_name** is the one shown in the language radio selection
- **language_file** is the name *without extension* of the file that contains the translation variables

## Attribution

### Italy data

All the data displayed in this dashboard is provided by the Italian Ministry of Health (Ministero della Salute) and elaborated by Dipartimento della Protezione Civile.
This work is therefore a derivative of [COVID-19 Italia - Monitoraggio situazione](https://github.com/pcm-dpc/COVID-19) licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

### World data

All the data displayed in this dashboard is provided by the Johns Hopkins University Center for Systems Science and Engineering (JHU CSSE). Also, Supported by ESRI Living Atlas Team and the Johns Hopkins University Applied Physics Lab (JHU APL).
This work is therefore a derivative of [Novel Coronavirus (COVID-19) Cases, provided by JHU CSSE] (https://github.com/CSSEGISandData/COVID-19) copyright 2020 Johns Hopkins University.