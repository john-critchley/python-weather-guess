# Things which are not implemented for demo
## These need to be done for full productionizing

## Kubernetes

This will also help with ending it being AWS specific

## Docker images

Each service in each docker image should have a health report (url /health on exposed API)
Docker HEALTHCHECK line for each service
Docker compose / monitoring should check these.

## Image storage

Images are currently stored on a shared Docker volume.

This should be replaces with S3 storage.
This helps eliminate the coupling between the kocker images categorize and dispatcher.
Then multi instance deployments are possible.

Also:
Retention time needs to be decided and cleanup schedule needs to be implemented; images
should be cleaned out in convert with database records about them.

## Kafka

Kafka clients are retried until broker is available.
In production it would be better to wait until health checks confirm it is ready.

## Replace development web servers

Flask servers are currently used, and need to be replaced with proper production hardened ones , I suggest Gunicorn.

### TLS

Production setup should include:

- SSL/TLS termination
- reverse proxy (e.g. nginx, apache2 or cloud load balancer)
- secure headers and best current cipher configuration

## Performance improvement

The database gets a hash/checksum of the image and if an image is already processed use previous answer.

## Testing

Full end to end test required - maybe using selenium.
Load testing should also be included in this.

More security testing is needed.

# Model

This should be fetced from a repo; investigate if it suitable to download from huggingface
investigate cenerally caching images also, in case it is not available on huggingface.

## Monitoring

Plug into Prometheus or other monitoring; reporting via Grafana or similar.
Need to have metrics and alerting for things like:

Key metrics to expose:

service availability

endpoint latency

database health and growth

Kafka health and queue depth

model processing latency

model error rate;  model error rate accuracy, precision, recall, f1 etc

Resource limits
- CPU (especially for categorize)
- Memory (categorize)

## Logging

Structured logging with externalized logs

## Further planning

Estimate capacity and make decisions on number and sizinga for production deployment
