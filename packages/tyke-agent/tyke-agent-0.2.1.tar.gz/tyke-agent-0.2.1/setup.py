import sys

from setuptools import setup, find_packages

version_tuple = sys.version_info
# install_requires doesn't always work(like if on older versions of pip)
if sys.version_info < (3, 7):
    print("Tyke is not supported on python versions before 3.7")
    sys.exit(1)

exec(open('src/tyke/version.py').read())

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tyke-agent",
    version=__version__,
    author="TykeVision",
    author_email="tech@tyke.ai",
    description="Tyke Python Agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='Tyke Python agent instrumentation',
    url="https://tyke.ai",
    project_urls={
        "Bug Tracker": "https://github.com/tykevision/python-agent/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "opentelemetry-api==1.20.0",
        "opentelemetry-exporter-otlp==1.20.0",
        "opentelemetry-exporter-zipkin==1.20.0",
        "opentelemetry-instrumentation==0.41b0",
        "opentelemetry-instrumentation-aiohttp-client==0.41b0",
        "opentelemetry-instrumentation-aiopg==0.41b0",
        "opentelemetry-instrumentation-asgi==0.41b0",
        "opentelemetry-instrumentation-asyncpg==0.41b0",
        "opentelemetry-instrumentation-aws-lambda==0.41b0",
        "opentelemetry-instrumentation-boto==0.41b0",
        "opentelemetry-instrumentation-botocore==0.41b0",
        "opentelemetry-instrumentation-cassandra==0.41b0",
        "opentelemetry-instrumentation-celery==0.41b0",
        "opentelemetry-instrumentation-confluent-kafka==0.41b0",
        "opentelemetry-instrumentation-django==0.41b0",
        "opentelemetry-instrumentation-elasticsearch==0.41b0",
        "opentelemetry-instrumentation-fastapi==0.41b0",
        "opentelemetry-instrumentation-flask==0.41b0",
        "opentelemetry-instrumentation-grpc==0.41b0",
        "opentelemetry-instrumentation-httpx==0.41b0",
        "opentelemetry-instrumentation-kafka-python==0.41b0",
        "opentelemetry-instrumentation-mysql==0.41b0",
        "opentelemetry-instrumentation-mysqlclient==0.41b0",
        "opentelemetry-instrumentation-psycopg2==0.41b0",
        "opentelemetry-instrumentation-pymongo==0.41b0",
        "opentelemetry-instrumentation-pymysql==0.41b0",
        "opentelemetry-instrumentation-redis==0.41b0",
        "opentelemetry-instrumentation-remoulade==0.41b0",
        "opentelemetry-instrumentation-requests==0.41b0",
        "opentelemetry-instrumentation-sklearn==0.41b0",
        "opentelemetry-instrumentation-sqlalchemy==0.41b0",
        "opentelemetry-instrumentation-urllib3==0.41b0",
        "opentelemetry-instrumentation-urllib==0.41b0",
        "opentelemetry-instrumentation-wsgi==0.41b0",
        "opentelemetry-propagator-b3==1.20.0",
        "opentelemetry-sdk==1.20.0",
        "opentelemetry-util-http==0.41b0",
        "deprecated==1.2.12",
        "google>=3.0.0",
        "pyyaml",
        "protobuf>=3.20.1"
    ],
    entry_points = {
        'console_scripts': [
            'tykeagent = tyke.agent.autoinstrumentation.tyke_instrument:run',
        ],
    }
)
