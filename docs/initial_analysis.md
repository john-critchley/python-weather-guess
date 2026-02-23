Below is a structured assessment and plan, explicitly tying observations back to the provided files.

---

## 1. Restating the assignment (from README)  

According to `/home/john/py/TechTest/python-weather-guess-main/README.md`, your assignment is:

- You inherit a PoC for a “weather from image” app.
- The client now wants:
  - A **cloud‑native solution** (top cloud provider, IaC, container orchestration).
  - A **production‑grade SDLC** with a **fully implemented CI/CD pipeline**.
  - Environments & DB in the cloud.
  - **SAST and DAST** integrated.
  - A **product demo deployed to a production‑like environment**.
  - IaC pilot using best practices.
  - You to **lead architecture and CI/CD**, being the only one on it for now.
  - Ability to demonstrate CI/CD on any of several SCMs (GitHub, GitLab, Bitbucket, Azure DevOps, Forgejo).
  - Be ready for **live coding** and design discussions.

The README also notes:
- Cloud bits can be **free-tier**, and some parts (like real tests) can be stubbed.
- You should have code and, ideally, a deployed app by around day 5.

---

## 2. What the current codebase implements

### 2.1 High-level architecture

From the code layout and descriptions:

- **`categorize` service**  
  - ML inference using VGG-19 model.
  - Consumes Kafka messages with requests; produces Kafka messages with responses.
  - Flask API only exposes `/stats`, but not the actual inference endpoints (inference runs on background thread).
  - References:
    - `/home/john/py/TechTest/python-weather-guess-main/src/categorize/runtime/app.py`
    - `/home/john/py/TechTest/python-weather-guess-main/src/categorize/config/default.ini`
    - `/home/john/py/TechTest/python-weather-guess-main/src/categorize/requirements.txt`

- **`dispatcher` service**  
  - Flask HTTP API to:
    - Accept image uploads at `POST /categorize`.
    - Return request status/classification at `GET /categorize/<request_id>`.
    - Track stats at `/stats`.
  - Publishes `Request` events to Kafka; consumes `Response` events to update in-memory result cache.
  - References:
    - `/home/john/py/TechTest/python-weather-guess-main/src/dispatcher/src/app.py`
    - `/home/john/py/TechTest/python-weather-guess-main/src/dispatcher/config/default.ini`
    - `/home/john/py/TechTest/python-weather-guess-main/src/dispatcher/README.md`

- **`reporting` service**  
  - Listens on Kafka and writes both `Request` and `Response` events to PostgreSQL.
  - Exposes `/stats` for counts.
  - No real reporting UI yet; only an endpoint returning a text representation of a counter dict.
  - References:
    - `/home/john/py/TechTest/python-weather-guess-main/src/reporting/src/app.py`
    - `/home/john/py/TechTest/python-weather-guess-main/src/reporting/config/default.ini`
    - DB schema: `/home/john/py/TechTest/python-weather-guess-main/src/reporting/database/v1_tables.sql`

- **`common` library**  
  - **Storage abstraction** with file and S3 backends:
    - `/home/john/py/TechTest/python-weather-guess-main/src/common/storage/storage.py`
    - `/home/john/py/TechTest/python-weather-guess-main/src/common/storage/backend.py`
    - `/home/john/py/TechTest/python-weather-guess-main/src/common/storage/file_backend.py`
    - `/home/john/py/TechTest/python-weather-guess-main/src/common/storage/s3_backend.py`
  - **Queue abstraction** with Kafka backend:
    - `/home/john/py/TechTest/python-weather-guess-main/src/common/queue/queue.py`
    - `/home/john/py/TechTest/python-weather-guess-main/src/common/queue/kafka_backend.py`
    - `/home/john/py/TechTest/python-weather-guess-main/src/common/queue/backend.py`
  - **Events DTOs**:
    - `/home/john/py/TechTest/python-weather-guess-main/src/common/event/event.py`
    - `/home/john/py/TechTest/python-weather-guess-main/src/common/event/request_dto.py`
    - `/home/john/py/TechTest/python-weather-guess-main/src/common/event/response_dto.py`
  - **Configuration**:
    - `/home/john/py/TechTest/python-weather-guess-main/src/common/config/config.py`
    - Sample configs:
      - `/home/john/py/TechTest/python-weather-guess-main/src/common/config/default_full.ini`
      - `/home/john/py/TechTest/python-weather-guess-main/src/common/config/default_full.env`

- **UI (Angular)**  
  - Angular 12 app (`img-uploader`) that:
    - Lets user choose an image (only partial template right now).
    - Calls dispatcher `POST /categorize` and then polls `GET /categorize/{id}` until a result is received.
  - References:
    - Angular workspace: 
      - `/home/john/py/TechTest/python-weather-guess-main/src/ui/angular.json`
      - `/home/john/py/TechTest/python-weather-guess-main/src/ui/package.json`
      - `/home/john/py/TechTest/python-weather-guess-main/src/ui/tsconfig*.json`
    - Component & service:
      - `/home/john/py/TechTest/python-weather-guess-main/src/ui/src/app/core/components/img-uploader/img-uploader.component.ts`
      - `/home/john/py/TechTest/python-weather-guess-main/src/ui/src/app/core/components/img-uploader/img-uploader.component.html`
      - `/home/john/py/TechTest/python-weather-guess-main/src/ui/src/app/core/services/file-upload.service.ts`
      - `/home/john/py/TechTest/python-weather-guess-main/src/ui/src/app/app.component.ts`
    - UI docs & scripts:
      - `/home/john/py/TechTest/python-weather-guess-main/src/ui/README.md`
      - `/home/john/py/TechTest/python-weather-guess-main/src/ui/start.sh`
      - `/home/john/py/TechTest/python-weather-guess-main/src/ui/install_deps.sh`

- **Infra (local)**  
  - Kafka + Zookeeper docker-compose:
    - `/home/john/py/TechTest/python-weather-guess-main/env/infra/kafka.compose.yaml`
  - PostgreSQL docker-compose:
    - `/home/john/py/TechTest/python-weather-guess-main/env/infra/postgres.compose.yaml`

- **Root dependencies**  
  - Backend Python deps:
    - `/home/john/py/TechTest/python-weather-guess-main/requirements.txt`
  - No global Dockerfiles, no CI/CD workflow files yet.

- **Docs**  
  - `/home/john/py/TechTest/python-weather-guess-main/docs/README.md` is empty.

So, architecturally, the original developer already moved towards a “microservices + queue + DB + UI” design, but it’s not productionized.

---

## 3. Gaps between assignment expectations and current project

Below I contrast the requirements in `/README.md` with what the codebase currently provides.

### 3.1 Cloud-native, container orchestration, IaC

**What’s required (from `/README.md`):**

- Cloud-native solution on a top cloud vendor.
- Container orchestration (Kubernetes is implied in the architect’s proposal).
- IaC for all environments (infrastructure, DB, etc).
- DB hosted in cloud.

**What we currently have:**

- Only **local Docker Compose** for Kafka and PostgreSQL:
  - `/env/infra/kafka.compose.yaml`
  - `/env/infra/postgres.compose.yaml`
- **No Dockerfiles** for the three Python services (`dispatcher`, `categorize`, `reporting`) or the Angular UI.
- **No Kubernetes manifests**, Helm charts, or cloud-native manifests.
- **No IaC** (Terraform, Pulumi, ARM/Bicep, CloudFormation) to provision:
  - Cloud VMs or managed Kubernetes cluster
  - Managed DB
  - Networking, IAM, etc.
- **No cloud provider integration** – storage is file or S3-capable (in `/src/common/storage/storage.py` and `/src/common/storage/s3_backend.py`), but:
  - No provisioning of the S3 bucket via IaC.
  - S3 usage is not configured in default configs (`default_full.ini` uses `file` backend in `/src/common/config/default_full.ini`).

**Gap:**  
- Need containers for each service and orchestrated deployment (K8s or similar).
- Need IaC for the underlying infra (cluster, DB, buckets).
- Need environment separation (dev / staging / prod) defined via IaC and configuration.

### 3.2 Production-grade SDLC & CI/CD (with SAST, DAST)

**What’s required:**

- Fully automated SDLC:
  - Build, test (can stub), image build, deploy.
- CI/CD integrated with SCM (GitHub/GitLab/etc).
- SAST and DAST integrated into pipeline.

**What we currently have:**

- No CI/CD definition files in the repo (no `.github/workflows`, `.gitlab-ci.yml`, `azure-pipelines.yml`, etc.).
- No pipeline scripts or makefiles.
- Tests:
  - Only **Angular boilerplate tests**:
    - `/src/ui/src/app/app.component.spec.ts`
    - `/src/ui/src/app/core/components/img-uploader/img-uploader.component.spec.ts`
    - `/src/ui/src/app/core/services/tests/file-upload.service.spec.ts`
  - No Python unit tests for backend.
- No SAST/DAST tooling or configuration:
  - No eslint/tslint rules for Angular.
  - No Bandit, Flake8, mypy, etc for Python.
  - No OWASP ZAP or similar DAST integration scripts.

**Gap:**  
- Need a CI/CD pipeline (e.g., GitHub Actions) that:
  - Checks out code.
  - Installs dependencies.
  - Runs linting and tests (or placeholders).
  - Runs SAST on Python and TS.
  - Builds Docker images.
  - Runs DAST (on deployed test environment or ephemeral).
  - Deploys to chosen environment (k8s etc.).
- Need minimal test suite / or stubbed steps.

### 3.3 Production-like deployment & demo

**What’s required:**

- Application deployed to a production‑like environment (even if test/demo).
- Accessible for demo.

**What we currently have:**

- Local run only:
  - Flask servers run locally from `if __name__ == "__main__"` blocks in:
    - `/src/dispatcher/src/app.py`
    - `/src/categorize/runtime/app.py`
    - `/src/reporting/src/app.py`
  - Angular app served via `npm start` on port 8088:
    - `/src/ui/package.json`
    - `/src/ui/start.sh`
- Dependencies run via local Docker Compose:
  - Kafka, Zookeeper, Postgres in `/env/infra/*.compose.yaml`.
- No documentation on running everything end-to-end together (no single docker-compose top-level file linking all services).
- No deployed version in the cloud.

**Gap:**
- Need:
  - Containerized services.
  - Environment definition for a “prod-like” cluster.
  - Automated or at least scripted deployment.
  - Public endpoint or at least a stable demo environment.

### 3.4 IaC Pilot & Best Practices

**What’s required:**

- Client wants to **run a pilot using IaC best practices** (per `/README.md`).
- Should cover:
  - Networking.
  - K8s cluster or equivalent.
  - Database and storage.
  - Possibly CI/CD infra.

**What we currently have:**

- Only docker-compose files (not IaC for cloud).
- No Terraform/Pulumi/CloudFormation at all.
- No environment separation (dev/test/prod) in IaC.

**Gap:**
- Need at least a Terraform project that:
  - Provisions infra on one chosen cloud.
  - Uses state, variables, modules.
  - Demonstrates best practices (remote state, separation by workspace or env).

### 3.5 Documentation & diagrams

**What’s required:**

- “Systems design with supporting diagrams and documentation” (/README.md).
- Should be understandable by project managers, architects, and tech lead.
- Explain:
  - Services, flows, responsibilities.
  - CI/CD pipeline design.
  - Deployment topology.

**What we currently have:**

- Sparse documentation:
  - Root `/README.md` describes the task, but not the solution details.
  - `/src/dispatcher/README.md` describes dispatcher usage manually (curl, request/response flows).
  - `/src/ui/README.md` only explains how to run the Angular app and change ports.
  - `/docs/README.md` is empty.
- No diagrams (no PNG/SVG in `/docs` referenced; only empty `README.md`).

**Gap:**
- Need:
  - High-level architecture diagram (services, Kafka, DB, UI).
  - Deployment diagram (k8s components, cloud resources).
  - CI/CD pipeline diagram.
  - Documentation on local dev vs cloud deployment vs CI/CD.

### 3.6 Code quality / correctness issues

Some issues surfaced on inspection:

- **Config typing and defaults**:
  - In `/src/common/config/config.py`, all values coming from file/env are **strings**:
    - `config_obj.get(...)` returns strings; no type casting is done.
    - `os.getenv(..., default=...)` always returns strings when env var is set.
  - But code assumes booleans and ints in many places:
    - Example: `LOGLEVEL_DEBUG = config.categorize_app_debug` in `/src/categorize/runtime/app.py` passed to `app.run(..., debug=LOGLEVEL_DEBUG)`.
    - Same for ports where they cast to `int()` but other fields may remain wrong types (e.g., allowed extensions set).
- **Categorize model usage bug:**
  - In `/src/categorize/runtime/app.py`:
    ```python
    global MODEL_EXEC
    ...
    MODEL_EXEC = load_model(MODEL_PATH, compile=False)
    ```
  - But inside `infer()`:
    ```python
    image_class = model.predict(image)
    resp.image_class = image_classes[image_class[0]]
    ```
    `model` is not defined; should be `MODEL_EXEC`.
  - Also `image_class` prediction likely returns a numpy array of probabilities, not an integer index:
    - Access `image_class[0]` probably yields a vector, not an index.
    - More logic is needed (e.g., `np.argmax`).
- **Kafka config inconsistency:**
  - `/src/common/queue/kafka_backend.py` expects `config` to be a dict:
    ```python
    self.group_id = config["group_id"] if "group_id" in config else ...
    self.brokers = config["connection"] if "connection" in config else "localhost:29092"
    ```
  - But `Configuration` defines `queue_config` as a simple string, default `"localhost:29092"` (`/src/common/config/config.py`).
  - Dispatcher passes:
    ```python
    QUEUE_CONFIG = config.queue_config
    queue = Queue(QUEUE_BACKEND, QUEUE_CONFIG)
    ```
    in `/src/dispatcher/src/app.py`.
  - So currently, `config` is a string and `config["group_id"]` will fail. The original author maybe expected `{"connection": "localhost:29092"}`.
- **Queue filter logic**:
  - `/src/common/queue/queue.py` uses `Filter` with questionable logic (e.g., uses `self.filters[field]` even when not initialized with value, may raise KeyError; using `filter` as var name). This isn’t critical for MVP but is brittle.
- **CORS / security**:
  - Dispatcher explicitly sets `Access-Control-Allow-Origin: *` in `/src/dispatcher/src/app.py`. That’s fine for PoC, but not production-grade.
  - No authentication / authorization anywhere.
- **Error handling**:
  - `infer()` in `/src/categorize/runtime/app.py` has a bare `except:` that just randomizes an image class. That’s okay as a PoC, but not okay for production.
  - `scan_topic()` in `/src/reporting/src/app.py` has a bare `except:` swallowing DB errors.
- **Angular UI template** is incomplete:
  - `/src/ui/src/app/core/components/img-uploader/img-uploader.component.html` only contains static text strings:
    ```text
    File Upload
    Only images are allowed!
    Browse for your image!
    Submit!
    ```
  - No Angular bindings (no `<input type="file">`, no `(click)` handlers). The TS code in `/img-uploader.component.ts` expects there to be `uploadFile()` bound somewhere and a file input with `(change)="onFileChange($event)"`.
- **Docs incomplete**:
  - `/docs/README.md` is empty.

These code-level issues must be fixed before a credible “production-like” demo.

---

## 4. Plan / Checklist of what needs doing

Below is a prioritized checklist, from “get it working locally” through “production-grade with CI/CD and IaC.”

### 4.1 Stabilize and validate the existing PoC locally

**Goal:** Make the current system actually work end-to-end on a developer machine.

**Tasks:**

1. **Fix categorize model usage**  
   - In `/src/categorize/runtime/app.py`:
     - Replace `image_class = model.predict(image)` with `MODEL_EXEC.predict(image)`.
     - Convert prediction to class index (e.g., `idx = int(np.argmax(pred[0]))` and use that against `image_classes`).
   - Ensure the VGG-19 model file path (`../model/vgg19-weather.h5`) from `/src/categorize/config/default.ini` actually exists and is correct relative to runtime.

2. **Fix Kafka config passing**  
   - Decide on config structure, e.g.:
     - Change `queue_config` in `/src/common/config/config.py` to be JSON or adjust how it is used.
     - Easiest: in dispatcher, categorize, reporting:
       - When instantiating `Queue`, wrap string into dict:
         ```python
         QUEUE_CONFIG = {"connection": config.queue_config}
         ```
       - Adjust `KafkaBackend.__init__` in `/src/common/queue/kafka_backend.py` if needed.
   - Verify that queues function (publish/subscribe) with local Kafka from `/env/infra/kafka.compose.yaml`.

3. **Fix dispatcher allowed extensions**  
   - In `/src/dispatcher/src/app.py`, `ALLOWED_EXTENSIONS = config.dispatcher_allowed_extensions` but `dispatcher_allowed_extensions` in `/src/common/config/config.py` is a `set`, and environment / INI may override it as a **string** (`"{'jpg', 'jpeg', 'png'}"` in `/src/common/config/default_full.env` and `/src/common/config/default_full.ini`).
   - Normalize this config to a `set` during load (e.g., parse string if needed).

4. **Complete Angular UI template**  
   - Update `/src/ui/src/app/core/components/img-uploader/img-uploader.component.html` to include:
     - `<input type="file" (change)="onFileChange($event)">`
     - A button calling `(click)="uploadFile()"`.
     - An area showing the classification via `@Output() word` from `img-uploader` to `/src/ui/src/app/app.component.html`.
   - Possibly adjust CSS in `/src/ui/src/app/core/components/img-uploader/img-uploader.component.css` and `/src/ui/src/app/app.component.css` accordingly.

5. **End-to-end smoke test locally**  
   - Start:
     - Kafka & Zookeeper via `/env/infra/kafka.compose.yaml`.
     - Postgres via `/env/infra/postgres.compose.yaml` and apply `/src/reporting/database/v1_tables.sql`.
     - Python apps (`dispatcher`, `categorize`, `reporting`) from their main scripts.
     - Angular UI via `/src/ui/start.sh`.
   - Use browser to:
     - Access UI at `http://localhost:8088`.
     - Upload image; track call to dispatcher (`http://localhost:8080/categorize` as per `/src/ui/src/app/core/services/file-upload.service.ts`).
     - Confirm inference result shows up and is consistent.

### 4.2 Harden code & add minimal tests

**Goal:** Address obvious issues and have enough tests to justify CI steps (even if trivial).

**Tasks:**

1. **Fix error handling**  
   - Replace bare `except:` in:
     - `/src/categorize/runtime/app.py` (wrap exceptions, log them).
     - `/src/reporting/src/app.py` in `scan_topic()` (log DB errors).
   - Consider fallback behavior (e.g., classification error returns explicit “unknown” rather than random).

2. **Add simple Python tests**  
   - Introduce `tests/` directory for backend:
     - Unit test for `Event` class in `/src/common/event/event.py` (serialization/deserialization).
     - Unit test for `Storage` and file backend in `/src/common/storage/*.py`.
     - Simple test for dispatcher’s `allowed_file()` function in `/src/dispatcher/src/app.py`.
   - These can be minimal but will allow CI to run `pytest`.

3. **Add Angular linting/test config (reuse existing)**  
   - Use existing setup:
     - `/src/ui/karma.conf.js`
     - `/src/ui/src/test.ts`
     - `/src/ui/tsconfig.spec.json`
   - Ensure `npm test` at `/src/ui` works (even if tests are default).

4. **Add documentation for local dev**  
   - Fill `/docs/README.md` with:
     - How to run Kafka/Postgres.
     - How to run each service.
     - How to run UI.
     - Example curl commands similar to `/src/dispatcher/README.md`.

### 4.3 Containerization

**Goal:** Dockerize all services for consistent deployment.

**Tasks:**

1. **Create Dockerfiles:**

   - For Python backend (can share a base or have one per service):

     - Base Python image (e.g., `python:3.10-slim`).
     - Install system packages for `psycopg2` (if needed).
     - Install `requirements.txt` from `/requirements.txt` plus TensorFlow/Keras (note: `categorize/requirements.txt` lists TensorFlow and Keras; decide whether to share or separate).
     - Set `WORKDIR` per service and appropriate `CMD`.

   - For `dispatcher`:
     - Entrypoint: `python -m dispatcher.src.app` or `python src/dispatcher/src/app.py` with appropriate `CONFIG_FILE` env variable.

   - For `categorize`:
     - Entrypoint: `python src/categorize/runtime/app.py`.
     - Ensure model file is available in image (copy from `model/`).

   - For `reporting`:
     - Entrypoint: `python src/reporting/src/app.py`.

   - For UI:
     - Option 1: serve via `ng serve` in container (dev-like).
     - Option 2: build Angular app (`ng build`) and serve via Nginx; add a Dockerfile in `/src/ui`.

2. **Create a top-level docker-compose for all services**  
   - Compose file referencing:
     - dispatcher, categorize, reporting, ui.
     - Kafka and Postgres (can reuse from `/env/infra/*.compose.yaml`).
   - Configure environment variables for each service (storage backend, queue config, DB config).

3. **Test docker-compose locally**  
   - `docker-compose up` should start entire stack.
   - Validate that UI calls dispatcher and flows through to categorize and reporting.

### 4.4 Choose SCM and design CI/CD

**Goal:** Pick one SCM (e.g., GitHub) and implement CI/CD.

**Tasks:**

1. **Pick SCM**  
   - Given the requirement in `/README.md` that any of GitHub/GitLab/Bitbucket/Azure DevOps/Forgejo is OK, choose one:
     - Assume GitHub for concreteness.

2. **CI pipeline definition**  
   - Add `.github/workflows/ci.yml` to:
     - Trigger on `push` and `pull_request`.
     - Jobs:
       1. **Lint & test backend**:
          - Setup Python.
          - Install dependencies from `/requirements.txt` + TensorFlow etc.
          - Run `pytest` on backend tests.
       2. **Lint & test frontend**:
          - `cd src/ui`, run `npm ci`, `npm test`.
       3. **SAST**:
          - Run Bandit or similar on Python (e.g., `bandit -r src`).
          - Run `npm run lint` (if you add lint script) or at least `ng lint` on the Angular project.
       4. **Build Docker images**:
          - Use Docker buildx or similar.
          - Optionally push to a container registry (Docker Hub or cloud provider registry).
     - These steps are enough to show a "production-grade" SDLC even with stub tests.

3. **CD pipeline definition**  
   - Add `.github/workflows/cd.yml` (or extend CI job) to:
     - Trigger on `push` to `main` or tags.
     - Deploy to a chosen environment:
       - For k8s, use `kubectl` or GitOps (ArgoCD/Flux) if you have time.
       - Or use a simpler target, like a single VM with docker-compose as an interim “prod-like” environment.

4. **DAST integration**  
   - In a later pipeline stage (after deployment to a test environment), run:
     - OWASP ZAP baseline scan against UI/dispatcher endpoints.
     - Fail or just report on high findings.
   - This can be a separate GitHub Actions job in CI/CD.

5. **Document the pipeline**  
   - Update `/docs/README.md` and root `/README.md` with:
     - CI/CD architecture.
     - Tooling used (GitHub Actions + Bandit + ZAP, etc.).
     - Link to pipeline runs.

### 4.5 Kubernetes & IaC

**Goal:** Provide a cloud-native deployment and IaC pilot.

**Tasks:**

1. **Kubernetes manifests**  
   - For each service:
     - `Deployment` and `Service` YAML manifests.
   - For external access:
     - Ingress or LoadBalancer Service for UI and dispatcher.
   - ConfigMaps/Secrets for:
     - Kafka connection string.
     - DB credentials.
     - Storage backend choice and S3 bucket settings (if using S3 per `/src/common/storage/s3_backend.py`).

2. **Terraform (or other IaC)**  
   - In a new directory, e.g. `/infra/terraform`:
     - Provision:
       - Kubernetes cluster (e.g., EKS, AKS, GKE, or managed K8s on chosen provider).
       - Managed Postgres (e.g., RDS, Cloud SQL, Azure Database).
       - S3 bucket or equivalent blob storage if you decide to use S3 backend.
     - Provide variables and example `terraform.tfvars`.
     - Use remote state (e.g., S3 + DynamoDB, Terraform Cloud, etc.).
   - OPTIONAL (if short on time):  
     - Provide Terraform only for DB + S3 + networking and assume k8s is pre-existing (e.g., a kind cluster or local cluster). This still counts as an IaC pilot.

3. **Deployment automation**  
   - Add a small deployment script or GitHub Action job that:
     - Uses `kubectl apply` for manifests.
     - Or triggers a GitOps tool if used.

4. **Document IaC**  
   - In `/docs/README.md`:
     - Describe the Terraform setup.
     - How to bootstrap, apply, and destroy.
     - Security concepts (secrets, IAM roles for S3, etc.).

### 4.6 Observability and production polish (optional but nice)

**Optional “nice-to-have” given time:**

1. **Logging**  
   - Standardize logging format and level (use `logging` config).
   - Ensure logs include correlation IDs for tracing (`_id`, `correlation_id` from `/src/common/event/event.py`).

2. **Monitoring & metrics**  
   - Add simple `/health` endpoints to each Flask app.
   - Expose metrics (e.g., Prometheus) if desired.

3. **Security improvements**  
   - Scope CORS more narrowly than `*` in `/src/dispatcher/src/app.py`.
   - Introduce API keys or basic authentication for some endpoints (at least as concept, if not fully implemented).

4. **Reporting UI**  
   - Extend Angular UI or create a separate small dashboard to:
     - Read counts from `/reporting/src/app.py`’s `/stats`.
     - Or query DB for a simple table of recent classification events.

---

## 5. Summary

- The current project already has a **good PoC architecture**: services for upload (`dispatcher`), inference (`categorize`), reporting (`reporting`), shared `common` library, Angular UI, plus Kafka and Postgres via docker-compose (see all the code paths under `/src` and `/env`).
- However, compared to the **assignment in `/README.md`**, it **lacks**:
  - Cloud-ready containerization and orchestration.
  - IaC for cloud infra.
  - CI/CD, SAST, DAST.
  - Production-like deployment and documentation/diagrams.
- There are also some **code correctness issues** (e.g., Kafka config, model usage, UI template) that must be fixed for a credible demo.

The checklist in section 4 gives you a concrete plan from “get this running locally and reliably” through to “fully integrated CI/CD and IaC pilot on a cloud provider.”
