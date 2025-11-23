
from fastapi import FastAPI, Request
from fastapi.responses import Response
import time
from starlette.middleware.base import BaseHTTPMiddleware
from app.routes import auth, posts, users, activities
from app.routes.activities_filters import router as activities_filters_router
import logging

app = FastAPI()

class RateLimitMiddleware(BaseHTTPMiddleware):
	RATE_LIMIT = 100  # requests
	WINDOW = 60  # seconds
	requests = {}

	async def dispatch(self, request, call_next):
		ip = request.client.host
		now = int(time.time())
		window_start = now - self.WINDOW
		self.requests.setdefault(ip, []).append(now)
		self.requests[ip] = [t for t in self.requests[ip] if t > window_start]
		if len(self.requests[ip]) > self.RATE_LIMIT:
			return Response("Rate limit exceeded", status_code=429)
		response = await call_next(request)
		return response

app.add_middleware(RateLimitMiddleware)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
	response = await call_next(request)
	response.headers["X-Content-Type-Options"] = "nosniff"
	response.headers["X-Frame-Options"] = "DENY"
	response.headers["X-XSS-Protection"] = "1; mode=block"
	return response

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
	logger.info(f"Request: {request.method} {request.url}")
	response = await call_next(request)
	logger.info(f"Response status: {response.status_code}")
	return response

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(activities.router)
app.include_router(activities_filters_router)

@app.middleware("http")
async def log_requests(request: Request, call_next):
	logger.info(f"Request: {request.method} {request.url}")
	response = await call_next(request)
	logger.info(f"Response status: {response.status_code}")
	return response

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(activities.router)
