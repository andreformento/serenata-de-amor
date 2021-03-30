# Rosie, the robot

A Python application reading receipts from the Quota for Exercising Parliamentary Activity from Brazilian's Chamber of Deputies and Federal Senate. Rosie flag suspicious reimbursements and, in that case, offer a list of reasons why it was considered suspicious.

## Running

### With Docker

#### Running

```console
$ docker run --rm -v /tmp/serenata-data:/tmp/serenata-data serenata/rosie python rosie.py run <module-name>
```

TODO
```console
docker rm -f rosie || true
docker build . -t andreformento/serenata-de-amor-rosie
docker run --name rosie --memory="25g" -e LOG_LEVEL=debug andreformento/serenata-de-amor-rosie rosie.py run chamber_of_deputies --output /home/test_user/output
rm -rf output && docker cp rosie:/home/test_user/output output
```

Test [reference](https://pandas.pydata.org/pandas-docs/stable/user_guide/scale.html)
```
docker build . -t andreformento/serenata-de-amor-rosie
docker run --memory="25g" --rm andreformento/serenata-de-amor-rosie rosie.py test chamber_of_deputies
```

`<module-name>` might be either `chamber_of_deputies` or `federal_senate`. After running it, check your `/tmp/serenata-data/` directory in you host machine for `suspicions.xz`. It's a compacted CSV with all the irregularities Rosie was able to find.

#### Testing

```console
$ docker run --rm -v /tmp/serenata-data:/tmp/serenata-data serenata/rosie python rosie.py test
```

### Without Docker

#### Setup

There are a few options to setup your environment and download dependencies. The simplest way is [installing Anaconda](https://docs.anaconda.com/anaconda/install/) then run:

```console
$ conda update conda
$ conda create --name serenata python=3
$ conda activate serenata
$ pip install -r requirements.txt
```

#### Running


```console
$ python rosie.py run <module-name>
```

`<module-name>` might be either `chamber_of_deputies` or `federal_senate`.

A `/tmp/serenata-data/suspicions.xz` file will be created. It's a compacted CSV with all the irregularities Rosie was able to find.

You can choose a custom a target directory:

```console
$ python rosie.py run chamber_of_deputies --output /my/serenata/directory/
```

#### Testing

You can either run all tests with:

```console
$ python rosie.py test
```

Or test each submodule a time by passing a name:

```console
$ python rosie.py test core
$ python rosie.py test chamber_of_deputies
$ python rosie.py test federal_senate
```