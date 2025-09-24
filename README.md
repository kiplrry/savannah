# 🏪 MyStore

[![CI/CD](https://github.com/kiplrry/savannah/actions/workflows/django-test.yml/badge.svg)](https://github.com/kiplrry/savannah/actions)

A **Django + Django REST Framework** application for managing customers, products, and orders.  
This project demonstrates a **modern development stack** including:

- Django + DRF (REST APIs, Swagger docs, JWT auth, social login)
- PostgreSQL (prod) + SQLite (dev/test)
- Dockerized app with Gunicorn
- Kubernetes deployment stack
- GitHub Actions CI/CD pipeline

📦 Repo: [https://github.com/kiplrry/savannah](https://github.com/kiplrry/savannah)

---

## 🚀 Features

- Customer, Product, and Order management
- Nested serializers with order items
- Signals for SMS notifications via Africa’s Talking
- OAutb / Social login via `django-allauth`
- Auto-generated API docs with Swagger (drf-spectacular)
- CI/CD with GitHub Actions
- Deployable via Docker & Kubernetes

---

## API Preview

The **MyStore API** provides endpoints for managing customers, products, orders, and authentication.  
All endpoints are secured with **JWT or session authentication**.

Live API previews are provided by **drf_spectacular** and located at

1. **Swagger [localhost:8000/api/docs/swagger]()**
1. **Redoc [localhost:8000/api/docs/redoc]()**

Make sure to first authenticate at the following link

1. **Admin [localhost:8000/admin]()**
2. **Social and Email [localhost:8000/accounts/login]()**
3. **Api Method**
   ```curl
   curl -X POST http://localhost:8000/auth/login/ \
   -H "Content-Type: application/json" \
   -d '{
       "username": "your_username",
       "password": "your_password"
   }'
   ```
   Use the response key as your token

---

<details>
<summary>
<b>🔑 Authentication
</summary>

- **POST /auth/registration/** — Register a new user
- **POST /auth/login/** — Login and receive a token
- **POST /auth/logout/** — Logout the current user
- **POST /auth/password/change/** — Change password
- **POST /auth/password/reset/** — Request password reset
- **POST /auth/password/reset/confirm/** — Confirm password reset
- **POST /auth/registration/verify-email/** — Verify email
- **GET/PUT/PATCH /auth/user/** — Get or update user details

---

</details>
<details>
<summary><b> 👤 Customers </b>
</summary>

- **GET /api/customers/** — List customers (fields vary for normal users vs. staff)
- **POST /api/customers/** — Create a customer
- **GET /api/customers/{id}/** — Retrieve a customer
- **PUT/PATCH /api/customers/{id}/** — Update a customer
- **DELETE /api/customers/{id}/** — Delete a customer

---

</details>
<details>

<summary><b> 📦 Products </summary>

- **GET /api/products/** — List products (read-only for normal users, full access for admins)
- **POST /api/products/** — Create a new product (admin only)
- **GET /api/products/{id}/** — Retrieve a product
- **PUT/PATCH /api/products/{id}/** — Update a product (admin only)
- **DELETE /api/products/{id}/** — Delete a product (admin only)

---

</details>
<details>
<summary> <b>🛒 Orders </summary>

- **GET /api/orders/** — List orders (normal users see their own, admins can set customer)
- **POST /api/orders/** — Create a new order
- **GET /api/orders/{id}/** — Retrieve an order
- **PUT/PATCH /api/orders/{id}/** — Update an order
- **DELETE /api/orders/{id}/** — Delete an order
  **Order Items (nested under orders):**

- **GET /api/orders/{order_pk}/items/** — List items for an order
- **POST /api/orders/{order_pk}/items/** — Add an item to an order
- **GET /api/orders/{order_pk}/items/{id}/** — Retrieve an item
- **PUT/PATCH /api/orders/{order_pk}/items/{id}/** — Update an item
- **DELETE /api/orders/{order_pk}/items/{id}/** — Remove an item

---

</details>

## 📂 Project Structure

```bash
.
├── .github/workflows/ # GitHub Actions CI/CD pipelines
├── MyStore/ # Main Django project
│ ├── api/ # DRF views, serializers, urls
│ ├── store/ # Core app: models, admin, signals
│ ├── templates/ # Django templates (Swagger UI, auth)
│ ├── static/ # Static files
│ ├── Dockerfile # Docker build instructions
│ ├── .dockerignore
│ ├── entrypoint.sh # Container entrypoint
│ ├── requirements.txt
│ ├── .env # Local dev environment
│ ├── .env.prod # Production environment
│ ├── django-deployment.yml # K8s deployment
│ ├── django-service.yml # K8s service
│ ├── django-job.yml # K8s job (migrations, etc.)
│ └── manage.py
```

---

# 🛠️ Local Development

## 1. Clone the repo

```bash
git clone https://github.com/kiplrry/savannah.git
cd savannah/MyStore
```

## 2. Set up environment

```bash
vi .env.prod
# Edit with your keys (SECRET_KEY, DB, ATSK, etc.)
```

🔑 Environment Variables

| Name | Description |
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Debug mode (`True`/`False`) |
| `DATABASE_URL` | DB connection string |
| `ATSK_API` | Africa’s Talking SMS API key |

For when you want to aytocreate superuser

```bash
python3 manage.py ensure_superuser
```

| Name                        | Description               |
| --------------------------- | ------------------------- |
| `DJANGO_SUPERUSER_USERNAME` | Africa’s Talking username |
| `DJANGO_SUPERUSER_PASSWORD` | Africa’s Talking username |
| `DJANGO_SUPERUSER_EMAIL`    | Africa’s Talking username |

## 3. Run with Django dev server

```bash
python3 -m venv venv #create virtual env
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

# 🐳 Run with Docker

1. Build and run the container:

```bash
#if you copied repo from gh
docker build -t store-app .
docker run -p 8000:8000 --env-file .env store-app
```

```bash
#to use docker image
docker pull kiplarry/store-app:latest
docker run -p 8000:8000 --env-file .env store-app
```

Visit: http://localhost:8000/api/docs/swagger

## 2. ☸️ Deploy with Kubernetes

The k8s manifests are included in the repo (django-deployment.yml, django-service.yml, etc.):

```bash
kubectl apply -f MyStore/django-deployment.yml
kubectl apply -f MyStore/django-service.yml
kubectl apply -f MyStore/django-job.yml
kubectl create secret generic django-env --from-env-file=.env.prod
```

Check pods:

```bash
kubectl get pods
```

# SetUp

## 1. Creating a superuser

```bash
python3 mange.py createsuperuser
```

## 2. Creating OAuth

i. Login to the admin page with the superuser creadentials
ii. Go to the social applications tab and create a social application credential. Eg Google Auth. (Get them from the social apps of your choice, Google or Github)

### If you create anoteher site on the sites tab make sure to alter the settings config to point on the site id correctly.

# Testing

## ⚙️ CI/CD (GitHub Actions)

1. Runs tests with PostgreSQL service

2. Builds Docker image

3. Pushes image to Docker Hub (kiplarry/store-app)

4. (optionally) deploys to k8s

Workflow file: `.github/workflows/django-test.yml`

## Local Tests

The env in the settings is set to `.env.prod`. Create a new `.env` file and point to it in the `/Mystore/settings.py` file

Run locally with:

```bash
pytest -v
```
