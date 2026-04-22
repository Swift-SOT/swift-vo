# swift-vo

Swift VO implementation of [ObjObsSAP](https://github.com/ivoa-std/ObjObsSAP) and [ObsLocTAP](https://www.ivoa.net/documents/ObsLocTAP/index.html). This is implemented as a microservice
based upon the [FastAPI](http://fastapi.tiangolo.com) library. Visibility
calculations are performed using the Python API for the [Swift TOO
API](https://www.swift.psu.edu/too_api) contained in the `swifttools` module.

In order to run
locally in dev mode clone this repo:

```shell
git clone git@github.com:Swift-SOT/swift-vo.git
```

Enter the directory created:

```shell
cd swift-vo
```

install requirements and start the development server with the following command:

```shell
make dev
```

Access the ObjObsSAP server with the following example URL:

```url
http://localhost:8000/vo/objobssap/query?POS=25%2C12&TIME=60100%2F60101&MIN_OBS=0
```

Access the ObsLocTAP server with the following example URL:

```url
http://localhost:8000/vo/obsloctap/query?POS=25%2C12&TIME=60100%2F60101
```

or with a custom search radius:

```url
http://localhost:8000/vo/obsloctap/query?POS=25%2C12%2C1.0&TIME=60100%2F60101
```
