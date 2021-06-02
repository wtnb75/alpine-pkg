import click
import requests
import subprocess
import yaml
import os
import sys
import json
import re
import glob
import functools
from typing import List
from lxml import etree
from lxml.cssselect import CSSSelector
from natsort import natsorted
from logging import getLogger

_log = getLogger(__name__)
_apkdir = os.path.realpath(os.path.join(
    os.path.dirname(__file__), "..", "apk"))
_templatedir = os.path.realpath(os.path.join(
    os.path.dirname(__file__), "..", "templates"))


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version="0.1", prog_name="mgmt")
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
]


def common_option(decs):
    def deco(f):
        for dec in reversed(decs):
            f = dec(f)
        return f
    return deco


def cli_option(func):
    @functools.wraps(func)
    def wrap(verbose, *args, **kwargs):
        set_verbose(verbose)
        return func(*args, **kwargs)
    return common_option(_common_option)(wrap)


class VersionChecker:
    default_stopwords = ["dev", "alpha", "beta", "test", "rc", "RC"]

    def read_apkfile(self, apkfile) -> dict:
        kwd = ["pkgname", "pkgver", "pkgrel", "pkgdesc", "url", "arch", "license",
               "depends", "makedepends", "install", "subpackages", "source", "builddir"]
        res = {}
        for line in apkfile.readlines():
            m = re.match("^(?P<var>[a-z0-9_]+)=(?P<val>.*)$", line.strip())
            if m is None:
                continue
            if m.group("var") in kwd:
                v = m.group("val")
                v = v.strip('"').strip("'")
                res[m.group("var")] = v
        return res

    def fix_by_regexp(self, regexp, val):
        # val = val.replace("-", ".")
        if regexp is None:
            return val
        m = re.match(regexp, val)
        if m is None:
            return val
        return m.group("version")

    def usable(self, v, stopwords):
        if v is None:
            return False
        if v[0] not in "0123456789":
            return False
        for s in stopwords:
            if s in v:
                return False
        return True

    def get_newest(self, regexp, val: List[str], stopwords=None) -> str:
        _log.debug("choose newest: %s", val)
        if stopwords is None:
            stopwords = self.default_stopwords
        vers = [self.fix_by_regexp(regexp, x) for x in val]
        _log.debug("filtered: %s", vers)
        vers = natsorted([x for x in vers if self.usable(x, stopwords)])
        _log.debug("sorted: %s", vers)
        if len(vers) != 0:
            return vers[-1].replace("-", ".")

    def get_version_general(self, url, regexp=None, parser="html",
                            binary=False, stopwords=None, **kwargs):
        _log.debug("kwargs=%s, regexp=%s", kwargs, regexp)
        if parser == "html":
            ps = etree.HTMLParser()
        else:
            ps = etree.XMLParser()

        if binary:
            text = requests.get(url).content
        else:
            text = requests.get(url).text
        tree = etree.fromstring(text, parser=ps)
        _log.debug("tree %s", tree)
        if "xpath" in kwargs:
            found = tree.xpath(kwargs["xpath"])
            _log.debug("xpath %s -> %s", kwargs["xpath"], found)
        if "css" in kwargs:
            sel = CSSSelector(kwargs["css"])
            found = sel(tree)
            _log.debug("css %s -> %s", kwargs["css"], found)
        if "attribute" in kwargs:
            found = [x.get(kwargs["attribute"]) for x in found]
            _log.debug("atrrib %s -> %s", kwargs["attribute"], found)
        if kwargs.get("text"):
            found = [x.text for x in found]
            _log.debug("text -> %s", found)
        return self.get_newest(regexp, found, stopwords=stopwords)

    def get_version_sourceforge(self, id, directory, regexp=None, stopwords=None):
        url = f"https://sourceforge.net/projects/{id}/files/{directory}/"
        texts = requests.get(url).text.splitlines()
        for i in texts:
            if 'net.sf.files' not in i:
                continue
            ll = i.split("=", 1)
            if len(ll) == 2:
                data = json.loads(ll[1].rstrip(";"))
                versions = list(data.keys())
                return self.get_newest(regexp, versions, stopwords)

    def get_version_autoindex(self, url, regexp=None, prefix=None, suffix=None, stopwords=None):
        tree = etree.fromstring(requests.get(url).text, parser=etree.HTMLParser())
        atags = tree.xpath("//a")
        _log.debug("atags %s", len(atags))
        links = [os.path.basename(x.get("href")) for x in atags]
        _log.debug("links %s", links)
        if prefix:
            links = [x[len(prefix):] for x in links if x.startswith(prefix)]
            _log.debug("prefix %s", links)
        if suffix:
            links = [x[:-len(suffix)] for x in links if x.endswith(suffix)]
            _log.debug("suffix %s", links)
        return self.get_newest(regexp, links, stopwords=stopwords)

    def get_version_git_tag(self, url, regexp="^v?(?P<version>.*)$", stopwords=None):
        tags = []
        for line in subprocess.check_output(["git", "ls-remote", "--tags", url], text=True).splitlines():
            v = line.strip().split()
            tagstr = v[-1].split("/")[-1]
            if tagstr.endswith("{}"):
                continue
            tags.append(tagstr)
        return self.get_newest(regexp, tags, stopwords=stopwords)

    def get_version_github_tag(self, id,
                               regexp=r"^v?(?P<version>.*)(\\^\\{\\})?$", stopwords=None):
        return self.get_version_git_tag(
            url=f"https://github.com/{id}",
            regexp=regexp, stopwords=stopwords)

    def get_version_cargo(self, id, regexp=None, stopwords=None):
        baseurl = "https://raw.githubusercontent.com/rust-lang/crates.io-index/master/"
        if len(id) == 1:
            path = f"1/{id}"
        elif len(id) == 2:
            path = f"2/{id}"
        elif len(id) == 3:
            path = f"3/{id}"
        else:
            path = f"{id[:2]}/{id[2:4]}/{id}"
        url = baseurl + path
        versions = [json.loads(x)["vers"] for x in requests.get(url).text.splitlines()]
        return self.get_newest(regexp, versions, stopwords=stopwords)

    def get_version_pypi(self, id, regexp=None, stopwords=None):
        baseurl = "https://pypi.org/pypi/"
        url = f"{baseurl}{id}/json"
        versions = list(requests.get(url).json()["releases"].keys())
        return self.get_newest(regexp, versions, stopwords=stopwords)

    def get_version_github_release(self, id,
                                   regexp=r"^v?(?P<version>.*)(\\^\\{\\})?$",
                                   stopwords=None):
        res = requests.get(f"https://api.github.com/repos/{id}/releases/latest").json()
        return self.get_newest(regexp, [res.get("tag_name")], stopwords=stopwords)

    def get_version_hg_tag(self, url, method="json", regexp=None, stopwords=None):
        if method == "json":
            res = requests.get(f"{url}/json-tags").json()
            tags = [x.get("tag") for x in res.get("tags", []) if "tag" in x]
        elif method == "raw":
            res = requests.get(f"{url}/raw-tags").text.splitlines()
            tags = [x.split()[0] for x in res]
        return self.get_newest(regexp, tags, stopwords=stopwords)

    def get_version(self, args):
        if args.get("skip"):
            return None
        typ = args.pop("type", "git")
        fn = f"get_version_{typ}"
        if hasattr(self, fn):
            try:
                return getattr(self, fn)(**args)
            except Exception:
                _log.exception("get version failed: %s", args)
        return f"no_type:{typ}"

    def check(self, apkfile, check_value):
        pass


@cli.command()
@cli_option
@click.argument("apkfile", type=click.File('r'))
def read_apkfile(apkfile):
    print(VersionChecker().read_apkfile(apkfile))


@cli.command()
@cli_option
@click.argument("yamlfile", type=click.File('r'))
@click.argument("names", nargs=-1)
def get_version(yamlfile, names):
    data = yaml.safe_load(yamlfile)
    for k, args in data.items():
        if len(names) == 0 or k in names:
            print(k, VersionChecker().get_version(args))


@cli.command()
@cli_option
@click.argument("yamlfile", type=click.File('r'))
@click.argument("names", nargs=-1)
def check_version(yamlfile, names):
    data = yaml.safe_load(yamlfile)
    build_files = glob.glob(os.path.join(_apkdir, "*", "APKBUILD"))
    build_dirs = {os.path.basename(os.path.dirname(x)) for x in build_files}
    keys = set(data.keys())
    click.echo("not found: %s" % (build_dirs - keys))
    click.echo("too many: %s" % (keys - build_dirs))

    for k, args in data.items():
        if len(names) == 0 or k in names:
            vchk = VersionChecker()
            if os.path.exists(os.path.join(_apkdir, k, "APKBUILD")):
                with open(os.path.join(_apkdir, k, "APKBUILD")) as apkfile:
                    metainfo = vchk.read_apkfile(apkfile)
                current_ver = vchk.get_version(args)
                meta_ver = metainfo.get("pkgver")
                if current_ver is None or meta_ver is None:
                    continue
                if meta_ver != current_ver:
                    click.echo(f"new version: {k} pkg({meta_ver})!=current({current_ver})")


@cli.command()
@cli_option
@click.argument("wheelfile", type=click.Path(
    exists=True, file_okay=True, dir_okay=False, readable=True))
def whl2apk(wheelfile):
    raise NotImplementedError("whl2apk")


@cli.command()
@cli_option
@click.argument("gemfile", type=click.Path(
    exists=True, file_okay=True, dir_okay=False, readable=True))
def gem2apk(wheelfile):
    raise NotImplementedError("gem2apk")


@cli.command()
@cli_option
@click.argument("debfile", type=click.Path(
    exists=True, file_okay=True, dir_okay=False, readable=True))
def deb2apk(debfile):
    raise NotImplementedError("deb2apk")


@cli.command()
@cli_option
@click.argument("rpmfile", type=click.Path(
    exists=True, file_okay=True, dir_okay=False, readable=True))
def rpm2apk(rpmfile):
    raise NotImplementedError("rpm2apk")


@cli.command("template")
@cli_option
@click.option("--template", required=True, type=click.Choice(
    [x.rsplit(".", 1)[-1] for x in glob.glob(
        os.path.join(_templatedir, "APKBUILD.*"))]))
@click.option("--output", type=click.File("w"), default=sys.stdout)
@click.argument("args", default='{}')
def make_from_template(template, args, output):
    from jinja2 import Template
    ptn = re.compile(r'{{\s*(?P<key>[a-zA-Z0-9]+)\s*}}')
    data = json.loads(args)
    keys = set(data.keys())
    needs = set()
    tmpl = []
    with open(f"{_templatedir}/APKBUILD.{template}") as ifp:
        for line in ifp:
            tmpl.append(line.rstrip())
            for i in ptn.finditer(line):
                needs.add(i.group("key"))
    _log.debug("missing: %s", needs-keys)
    _log.debug("toomany: %s", keys-needs)
    for i in sorted(needs-keys):
        data[i] = input(f"{i}: ")
    click.echo(json.dumps(data, ensure_ascii=False))
    t = Template("\n".join(tmpl))
    click.echo(t.render(**data), file=output)


if __name__ == "__main__":
    cli()
