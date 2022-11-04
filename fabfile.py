import os

from fabric import Connection, task


@task
def deploy(ctx):
    with Connection(
            host=os.getenv('DEV_HOST'),
            user=os.getenv('DEV_USER'),
            connect_kwargs={"key_filename": os.getenv('DEV_PRIVATE_KEY')}
    ) as c:
        with c.cd("/home/svv/projects/py/advanced_diploma"):
            c.run("ls -la")
            c.run("docker-compose down")
            c.run("git stash clear")
            c.run("git stash -m 'to drop'")
            c.run("git pull origin dev --rebase")
            c.run("docker-compose up --build -d backend frontend postgres pgadmin")
