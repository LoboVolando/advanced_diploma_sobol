import os

from fabric import Connection, task


@task
def deploy(ctx):
    with Connection(
            host="192.168.0.193",
            user="svv",
    ) as c:
        with c.cd("/home/svv/projects/py/red"):
            c.run("ls -la")
            c.run("docker-compose down")
            c.run("git pull origin update_admin --rebase")
            c.run("docker-compose up --build -d")

@task
def gitlab_deploy(ctx):
    with Connection(
            host=os.getenv('DEV_HOST'),
            user=os.getenv('DEV_USER'),
            connect_kwargs={"key_filename": os.getenv('DEV_PRIVATE_KEY')}
    ) as c:
        with c.cd("/home/svv/projects/py/advanced_diploma"):
            c.run("ls -la")
            c.run("docker-compose down")
            c.run("git pull origin db_and_migrations --rebase")
            c.run("docker-compose up --build -d")
