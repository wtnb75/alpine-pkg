import click
import requests
import functools
from logging import getLogger

_log = getLogger(__name__)


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version="0.1", prog_name="napi")
def cli(ctx):
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


def set_verbose(flag):
    from logging import basicConfig, DEBUG, INFO
    fmt = '%(asctime)s %(levelname)s %(message)s'
    if flag:
        basicConfig(level=DEBUG, format=fmt)
    else:
        basicConfig(level=INFO, format=fmt)


_common_option = [
    click.option("--verbose/--no-verbose", default=False, show_default=True),
    click.option("--token", required=True, envvar="NETLIFY_AUTH_TOKEN"),
    click.option("--site-id", envvar="NETLIFY_SITE_ID"),
    click.option("--endpoint"),
]


def common_option(decs):
    def deco(f):
        for dec in reversed(decs):
            f = dec(f)
        return f
    return deco


def cli_option(func):
    @functools.wraps(func)
    def wrap(verbose, token, endpoint, site_id, *args, **kwargs):
        set_verbose(verbose)
        api = NetlifyAPI(token)
        if endpoint:
            api.baseurl = endpoint
        return func(api=api, site_id=site_id, *args, **kwargs)
    return common_option(_common_option)(wrap)


class NetlifyAPI:
    baseurl = "https://api.netlify.com/api/v1/"

    def __init__(self, token):
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get(self, path, **kwargs):
        return self.session.get(self.baseurl+path, **kwargs).json()

    def list_site(self):
        return self.get("sites")

    def get_deploy(self, site_id):
        return self.get(f"sites/{site_id}/deploys")

    def list_files(self, site_id):
        return self.get(f"sites/{site_id}/files")

    def get_file_meta(self, site_id, filename):
        return self.get(f"sites/{site_id}/files/{filename}")

    def get_file_data(self, site_id, filename):
        url = f"{self.baseurl}sites/{site_id}/files/{filename}"
        hdrs = {"Content-Type": "application/vnd.bitballoon.v1.raw"}
        return self.session.get(url, headers=hdrs).content

    def walk_files(self, site_id):
        for i in self.list_files(site_id):
            yield i, self.get_file_data(site_id, i["path"])


@cli.command()
@cli_option
def list(api, site_id):
    if not site_id:
        for s in api.list_site():
            click.echo(f"{s['id']} {s['created_at']}  {s['url']}")
        return
    for i in api.list_files(site_id):
        click.echo("%s %8d %s" % (i['sha'], i['size'], i['path']))


@cli.command()
@cli_option
@click.option("--output", type=click.Path())
def tar(api, site_id, output):
    import sys
    import tarfile
    import io
    import time
    if not site_id:
        click.echo(api.list_site())
        sys.exit(0)

    if not output:
        output = f"{site_id}.tar"
    tf = tarfile.open(output, "w")
    for meta, data in api.walk_files(site_id):
        ti = tarfile.TarInfo()
        ti.name = meta["path"].lstrip("/")
        ti.size = meta["size"]
        ti.mode = 0o644
        ti.uname = "root"
        ti.gname = "root"
        ti.mtime = time.time()
        tf.addfile(ti, io.BytesIO(data))
    tf.close()


@cli.command()
@cli_option
@click.option("--output", type=click.Path())
def zip(api, site_id, output):
    import sys
    import zipfile
    import time
    if not site_id:
        click.echo(api.list_site())
        sys.exit(0)

    if not output:
        output = f"{site_id}.zip"
    zf = zipfile.ZipFile(file=output, mode="w")
    for meta, data in api.walk_files(site_id):
        zi = zipfile.ZipInfo()
        zi.filename = meta["path"].lstrip("/")
        zi.date_time = time.localtime()
        zi.file_size = meta["size"]
        zi.external_attr = 0o644 << 16
        zf.writestr(zi, data)
    zf.close()


@cli.command()
@cli_option
@click.option("--output", type=click.Path(dir_okay=True))
def download(api, site_id, output):
    import sys
    import os
    if not site_id:
        click.echo(api.list_site())
        sys.exit(0)

    if not output:
        output = f"{site_id}"
    with click.progressbar(api.list_files(site_id)) as bar:
        for meta in bar:
            filename = os.path.join(output, meta["path"].lstrip("/"))
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "wb") as ofp:
                ofp.write(api.get_file_data(site_id, meta["path"]))


if __name__ == "__main__":
    cli()
