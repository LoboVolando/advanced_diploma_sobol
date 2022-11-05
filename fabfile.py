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
            c.run("git stash clear")
            c.run("git stash -m 'to drop'")
            c.run("git pull origin dev --rebase")
            c.run("docker-compose -f docker-compose.test.yml down")
            c.run("docker-compose -f docker-compose.deploy.yml down")
            c.run("docker-compose -f docker-compose.deploy.yml up --build -d backend frontend postgres pgadmin")

@task
def test(ctx):
    with Connection(
            host=os.getenv('DEV_HOST'),
            user=os.getenv('DEV_USER'),
            connect_kwargs={"key_filename": os.getenv('DEV_PRIVATE_KEY')}
    ) as c:
        with c.cd("/home/svv/projects/py/advanced_diploma"):
            c.run("ls")
            c.run("git stash clear")
            c.run("git stash -m 'to drop'")
            c.run("git pull origin dev --rebase")
            # c.run("docker-compose -f docker-compose.test.yml stop postgres")
            # c.run("docker-compose -f docker-compose.test.yml rm postgres")
            c.run("python3 -m venv venv")
            c.run("source ./venv/bin/activate")
            c.run('python -c "import sys; print(sys.executable)"')
