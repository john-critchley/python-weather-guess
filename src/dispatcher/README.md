# Dispatcher

> Please note: ML model is currently under active development (accuracy is a bit low).
For testing correctness, please use images from the provided `example-images` directory.

## Howto

- Install dependencies, run kafka from infra, run flask app (```app.py``` script)
- Upload any image to localhost:8080/categorize via curl/postman, with Body fields:
    - file: image itself
    - user_name: any string
- You will get request id, which you can use to get your response
- You will get a records like:
```
{"_tz_created": "2021-09-22 19:20:05.421366", "_id": "52065ac9-26d1-412d-a445-f03fe814f4ed", "correlation_id": "52065ac9-26d1-412d-a445-f03fe814f4ed", "image_path": "/tmp/2cdbb9a3-b7d8-489b-b5d7-810b666dd7df.jpeg", "image_size": 70284, "image_format": "jpeg", "user_name": "abyr"}
{"_tz_created": "2021-09-22 19:20:07.940878", "_id": "d0c22ac2-6f11-48f4-8d78-8e027ff56f88", "correlation_id": "d0c22ac2-6f11-48f4-8d78-8e027ff56f88", "image_path": "/tmp/57a8a85a-74c0-4fd7-882e-f98e66640a4d.jpeg", "image_size": 70284, "image_format": "jpeg", "user_name": "abyr"}
```

- ML model will listen for that record and produce response like
```
{"_tz_created": "2021-09-22 19:20:07.940878", "_id": "d0c22ac2-6f11-48f4-8d78-8e027ff56f88", "correlation_id": "d0c22ac2-6f11-48f4-8d78-8e027ff56f88", "image_class": "foggy"}
```

- You can get response to your request via localhost:8080/categorize/request_id
