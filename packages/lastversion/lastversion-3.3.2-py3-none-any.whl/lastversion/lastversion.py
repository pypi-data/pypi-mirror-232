# -*- coding: utf-8 -*-
# License: BSD, see LICENSE for more details.
"""
This is the main module of lastversion package.
To use it, import it and invoke any function documented here. For example:

```python
from lastversion import lastversion
lastversion.has_update(repo='mautic/mautic', current_version='1.2.3')
```
"""

import argparse
import json
import logging
import os
import re
import sys
from os.path import expanduser

try:
    # noinspection PyCompatibility
    from pathlib import Path
except ImportError:
    # noinspection PyUnresolvedReferences
    from pathlib2 import Path  # python 2 backport
import yaml
from packaging.version import InvalidVersion
from six.moves.urllib.parse import urlparse

from .GitHubRepoSession import TOKEN_PRO_TIP
from .HolderFactory import HolderFactory
from .ProjectHolder import ProjectHolder
from .Version import Version
from .__about__ import __self__
from .argparse_version import VersionAction
from .spdx_id_to_rpmspec import rpmspec_licenses
from .utils import download_file, extract_file, rpm_installed_version, ApiCredentialsError, \
    BadProjectError, extract_appimage_desktop_file

log = logging.getLogger(__name__)


# noinspection GrazieInspection
def latest(repo, output_format='version', pre_ok=False, assets_filter=None,
           short_urls=False, major=None, only=None, at=None,
           having_asset=None, exclude=None, even=False):
    r"""Find the latest release version for a project.

    Args:
        major (str): Only consider versions which are "descendants" of this major version string
        short_urls (bool): Whether we should try to return shorter URLs for release data
        assets_filter (Union[str, Pattern]): Regular expression for filtering assets for the latest release
        only (str): Only consider tags with this text. Useful for repos with multiple projects.
                    The argument supports negation and regular expressions. To indicate a regex,
                    start it with tilde sign, to negate the expression, start it with exclamation
                    point. See `Examples`.
        repo (str): Repository specifier in any form.
        output_format (str): Affects the return format. Possible values `version`, `json`, `dict`,
                             `assets`, `source`, `tag`.
        pre_ok (bool): Specifies whether pre-releases can be accepted as a newer version.
        at (str): Specifies repo hosting more precisely, only useful if repo argument was
                  specified as one word.
        having_asset (Union[str, bool]): Only consider releases with the given asset.
                                         Pass `True` for any asset
        exclude (str): Only consider releases NOT containing this text/regular expression.
        even (bool): Consider as stable only releases with even minor component, e.g. 1.2.3

    Examples:
        Find the latest version of Mautic, it is OK to consider betas.

        >>> latest("mautic/mautic", output_format='version', pre_ok=True)
        <Version('4.4.4')>

        Consider only tags without letters:

        >>> latest("openssl/openssl", output_format='version', only=r'!~\w')
        <Version('3.0.7')>

    Returns:
        Union[Version, dict]: Newer version object, if found and `output_format` is `version`.
    Returns:
        str: Single string containing tag, if found and `output_format` is `tag`

    """
    repo_data = {}

    # noinspection HttpUrlsUsage
    if repo.endswith('.yml') and not repo.startswith(('http://', 'https://')):
        with open(repo) as fpi:
            repo_data = yaml.safe_load(fpi)
            if 'repo' in repo_data:
                if 'nginx-extras' in repo:
                    repo_data['module_of'] = 'nginx'
                name = os.path.splitext(os.path.basename(repo))[0]
                if 'module_of' in repo_data:
                    name = '{}-module-{}'.format(repo_data['module_of'], name)
                repo = repo_data['repo']
                repo_data['name'] = name

    if repo.startswith(('http://', 'https://')) and repo.endswith('Chart.yaml'):
        at = 'helm_chart'

    if repo.endswith('.spec'):
        # The repo is specified inside the .spec file
        # GitHub repo is resolved via %{upstream_github} + %{name}/%{upstream_name}
        # no upstream_github global means that the spec was not prepared for lastversion
        # optional: use of spec_tag macros if the source is from GitHub. In edge cases we check
        # new version via GitHub, but prepared sources are elsewhere
        with open(repo) as f:
            name = None
            upstream_github = None
            upstream_name = None
            current_version = None
            spec_repo = None
            spec_url = None
            for line in f.readlines():
                if line.startswith('%global lastversion_repo'):
                    spec_repo = line.split(' ')[2].strip()
                elif line.startswith('%global upstream_github'):
                    upstream_github = line.split(' ')[2].strip()
                elif line.startswith('%global upstream_name'):
                    upstream_name = line.split(' ')[2].strip()
                elif line.startswith('Name:'):
                    name = line.split('Name:')[1].strip()
                elif line.startswith('URL:'):
                    spec_url = line.split('URL:')[1].strip()
                elif line.startswith('%global upstream_version '):
                    current_version = line.split(' ')[2].strip()
                    # influences %spec_tag to use %upstream_version instead of %version
                    repo_data['module_of'] = True
                elif line.startswith('Version:') and not current_version:
                    current_version = line.split('Version:')[1].strip()
            if spec_url:
                spec_host = urlparse(spec_url).hostname
                if spec_host in ['github.com'] and not upstream_github and not spec_repo:
                    log.warning('Neither %upstream_github nor %lastversion_repo macros were found. '
                                'Please prepare your spec file using instructions: '
                                'https://lastversion.getpagespeed.com/spec-preparing.html')
            if not current_version:
                log.critical('Did not find neither Version: nor %upstream_version in the spec file')
                sys.exit(1)
            try:
                if current_version != 'x':
                    repo_data['current_version'] = Version(current_version)
            except InvalidVersion:
                log.critical('Failed to parse current version in %s. Tried %s', repo, current_version)
                sys.exit(1)
            if upstream_name:
                repo_data['name'] = upstream_name
                repo_data['spec_name'] = '%{upstream_name}'
            else:
                repo_data['name'] = name
                repo_data['spec_name'] = '%{name}'
            if upstream_github:
                repo = "{}/{}".format(upstream_github, repo_data['name'])
                log.info('Discovered GitHub repo %s from .spec file', repo)
            elif spec_repo:
                repo = spec_repo
                log.info('Discovered explicit repo %s from .spec file', repo)
            elif spec_url:
                repo = spec_url

    with HolderFactory.get_instance_for_repo(repo, at=at) as project:
        project.set_only(only)
        project.set_exclude(exclude)
        project.set_having_asset(having_asset)
        project.set_even(even)
        release = project.get_latest(pre_ok=pre_ok, major=major)

        # bail out, found nothing that looks like a release
        if not release:
            return None

        from_type = 'Located the latest release tag {} at: {}'.format(
            release['tag_name'], project.get_canonical_link()
        )
        if 'type' in release:
            from_type = '{} via {} mechanism'.format(from_type, release['type'])
        log.info(from_type)

        version = release['version']
        tag = release['tag_name']

        # return the release if we've reached far enough:
        if output_format == 'version':
            return version

        if output_format in ['json', 'dict']:
            if output_format == 'dict':
                release['version'] = version
            else:
                release['version'] = str(version)
                if 'tag_date' in release:
                    release['tag_date'] = str(release['tag_date'])
            release['v_prefix'] = tag.startswith("v")
            version_macro = 'upstream_version' if 'module_of' in repo_data else 'version'
            version_macro = '%{{{}}}'.format(version_macro)
            holder_i = {value: key for key, value in HolderFactory.HOLDERS.items()}
            release['source'] = holder_i[type(project)]
            release['spec_tag'] = tag.replace(
                str(version),
                version_macro
            )
            # spec_tag_no_prefix is the helpful macro that will allow us to know where tarball
            # extracts to (GitHub-specific)
            if release['spec_tag'].startswith('v{}'.format(version_macro)) or \
                    re.match(r'^v\d', release['spec_tag']):
                release['spec_tag_no_prefix'] = release['spec_tag'].lstrip('v')
            else:
                release['spec_tag_no_prefix'] = release['spec_tag']
            release['tag_name'] = tag
            if hasattr(project, 'repo_license'):
                release['license'] = project.repo_license(tag)
            if hasattr(project, 'repo_readme'):
                release['readme'] = project.repo_readme(tag)
            release.update(repo_data)
            try:
                release['assets'] = project.get_assets(release, short_urls, assets_filter)
            except NotImplementedError:
                pass
            release['from'] = project.get_canonical_link()

            if 'license' in release and release['license']:
                spdx_id = release['license']['license']['spdx_id']
                rpmspec_licence = rpmspec_licenses[spdx_id] if spdx_id in rpmspec_licenses else None
                if rpmspec_licence:
                    release['rpmspec_license'] = rpmspec_licence
            return release

        if output_format == 'assets':
            return project.get_assets(release, short_urls, assets_filter)

        if output_format == 'source':
            return project.release_download_url(release, short_urls)

        if output_format == 'tag':
            return tag

    return None


def has_update(repo, current_version, pre_ok=False, at=None):
    """Given an existing version for a repo, checks if there is an update.

    Args:
        repo (str): Repository specifier in any form.
        current_version (str): A version you want to check update for.
        pre_ok (bool): Specifies whether pre-releases can be accepted as a newer version.
        at (str): Specifies repo hosting more precisely, only useful if repo argument was
                  specified as one word.

    Returns:
        Version: Newer version as an object, if found. Otherwise, False

    """
    latest_version = latest(repo, output_format='version', pre_ok=pre_ok, at=at)
    if latest_version and latest_version > Version(current_version):
        return latest_version
    return False


def check_version(value):
    """Given a version string, raises argparse.ArgumentTypeError if it does not contain any version.
    In lastversion CLI app, this is used as argument parser helper for --newer-than (-gt) option.

    Args:
        value (str): Free-format string which is meant to contain a user-supplied version

    Raises:
        argparse.ArgumentTypeError: Exception in a case version was not found in the input string

    Returns:
        Version: Parsed version object

    """
    value = parse_version(value)
    if not value:
        raise argparse.ArgumentTypeError("%s is an invalid version value" % value)
    return value


def parse_version(tag):
    """Parse version to Version object."""
    h = ProjectHolder()
    return h.sanitize_version(tag, pre_ok=True)


def get_rpm_packager():
    try:
        rpmmacros = expanduser("~") + "/.rpmmacros"
        with open(rpmmacros) as f:
            for ln in f.readlines():
                if ln.startswith('%packager'):
                    return ln.split('%packager')[1].strip()
    except IOError:
        log.warning("~/.rpmmacros does not exist. Changelog will not be generated")
    return None


def update_spec(repo, res, sem='minor'):
    print(res['version'])
    if 'current_version' not in res or res['current_version'] < res['version']:
        log.info('Updating spec %s with semantic %s', repo, sem)
        if 'current_version' in res and len(res['version'].release) >= 3:
            current_major = res['current_version'].release[0]
            latest_major = res['version'].release[0]
            current_minor = res['current_version'].release[1]
            latest_minor = res['version'].release[1]
            if sem in ['minor', 'patch']:
                fail_fmt = 'Latest v{} fails semantic {} constraint against current v{}'
                if latest_major != current_major:
                    log.warning(
                        fail_fmt.format(res['version'], sem, res['current_version']))
                    sys.exit(4)
                if sem == 'patch' and latest_minor != current_minor:
                    log.warning(
                        fail_fmt.format(res['version'], sem, res['current_version']))
                    sys.exit(4)
    else:
        log.info('No newer version than already present in spec file')
        sys.exit(2)
    # update %lastversion_tag and %lastversion_dir, Version (?), Release
    out = []
    packager = get_rpm_packager()
    with open(repo) as f:
        for ln in f.readlines():
            if ln.startswith('%global lastversion_tag '):
                out.append('%global lastversion_tag {}'.format(res['spec_tag']))
            elif ln.startswith('%global lastversion_dir '):
                out.append('%global lastversion_dir {}-{}'.format(
                    res['spec_name'], res['spec_tag_no_prefix']))
            elif ln.startswith('%global upstream_version '):
                out.append('%global upstream_version {}'.format(res['version']))
            elif ln.startswith('Version:') and ('module_of' not in res or not res['module_of']):
                version_tag_regex = r'^Version:(\s+)(\S+)'
                m = re.match(version_tag_regex, ln)
                out.append('Version:' + m.group(1) + str(res['version']))
            elif ln.startswith('%changelog') and packager:
                from datetime import datetime
                now = datetime.utcnow()
                today = now.strftime('%a %b %d %Y')
                out.append(ln.rstrip())
                out.append('* {} {}'.format(today, packager))
                out.append('- upstream release v{}'.format(res['version']))
                out.append("\n")
            elif ln.startswith('Release:'):
                release_tag_regex = r'^Release:(\s+)(\S+)'
                m = re.match(release_tag_regex, ln)
                release = m.group(2)
                from string import digits
                release = release.lstrip(digits)
                out.append('Release:' + m.group(1) + '1' + release)
            else:
                out.append(ln.rstrip())
    with open(repo, "w") as f:
        f.write("\n".join(out))


def install_app_image(url, install_name):
    """Install an AppImage from a URL to `~/Applications/<install_name>`

    Args:
        url (str): URL where AppImage file is hosted
        install_name (str): Short name that the AppImage will be renamed to
    """
    home_dir = os.path.expanduser('~')
    apps_dir = os.path.join(home_dir, 'Applications')
    app_file_name = os.path.join(apps_dir, f"{install_name}.AppImage")

    Path(apps_dir).mkdir(exist_ok=True, parents=True)
    download_file(url, app_file_name)
    os.chmod(app_file_name, 0o755)  # skipcq: BAN-B103
    extract_appimage_desktop_file(app_file_name)


def main(argv=None):
    """
    The entrypoint to CLI app.

    Args:
        argv: List of arguments, helps test CLI without resorting to subprocess module.
    """
    epilog = None

    if "GITHUB_API_TOKEN" not in os.environ and "GITHUB_TOKEN" not in os.environ:
        epilog = TOKEN_PRO_TIP
    parser = argparse.ArgumentParser(description='Find the latest software release.',
                                     epilog=epilog,
                                     prog='lastversion')
    parser.add_argument('action', nargs='?', default='get',
                        help='Action to run. Default: get',
                        choices=['get', 'download', 'extract', 'unzip', 'test', 'format', 'install', 'update-spec'])
    parser.add_argument('repo', metavar='<repo URL or string>',
                        help='Repository in format owner/name or any URL that belongs to it, or a version string')
    # affects what is considered last release
    parser.add_argument('--pre', dest='pre', action='store_true',
                        help='Include pre-releases in potential versions')
    parser.add_argument('--sem', dest='sem', choices=['major', 'minor', 'patch', 'any'],
                        help='Semantic versioning level base to print or compare against')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Will give you an idea of what is happening under the hood, '
                             '-vv to increase verbosity level')
    # no --download = False, --download filename.tar, --download = None
    parser.add_argument('-d', '-o', '--download', '--output', dest='download', nargs='?', default=False, const=None,
                        metavar='FILENAME', help='Download with custom filename')
    # how / which data of last release we want to present
    # assets will give download urls for assets if available and sources archive otherwise
    # sources will give download urls for sources always
    # json always includes "version", "tag_name" etc. + whichever json data was
    # used to satisfy lastversion
    parser.add_argument('--format',
                        choices=['version', 'assets', 'source', 'json', 'tag'],
                        help='Output format')
    parser.add_argument('--assets', dest='assets', action='store_true',
                        help='Returns assets download URLs for last release')
    parser.add_argument('--source', dest='source', action='store_true',
                        help='Returns only source URL for last release')
    parser.add_argument('-gt', '--newer-than', type=check_version, metavar='VER',
                        help="Output only if last version is newer than given version")
    parser.add_argument('-b', '--major', '--branch', metavar='MAJOR',
                        help="Only consider releases of a specific major "
                             "version, e.g. 2.1.x")
    parser.add_argument('--only', metavar='REGEX',
                        help="Only consider releases containing this text. "
                             "Useful for repos with multiple projects inside")
    parser.add_argument('--exclude', metavar='REGEX',
                        help="Only consider releases NOT containing this text. "
                             "Useful for repos with multiple projects inside")
    parser.add_argument('--filter', metavar='REGEX', help="Filters --assets result by a regular "
                                                          "expression")
    parser.add_argument('--having-asset', metavar='ASSET',
                        help="Only consider releases with this asset",
                        nargs='?', const=True)
    parser.add_argument('-su', '--shorter-urls', dest='shorter_urls', action='store_true',
                        help='A tiny bit shorter URLs produced')
    parser.add_argument('--even', dest='even', action='store_true',
                        help='Only even versions like 1.[2].x, or 3.[6].x are considered as stable')
    parser.add_argument('--at', dest='at',
                        help='If the repo argument is one word, specifies where to look up the '
                             'project. The default is via internal lookup or GitHub Search',
                        choices=HolderFactory.HOLDERS.keys())
    parser.add_argument('-y', '--assumeyes', dest='assumeyes', action='store_true',
                        help='Automatically answer yes for all questions')
    parser.add_argument('--version', action=VersionAction)
    parser.set_defaults(validate=True, verbose=False, format='version',
                        pre=False, assets=False, newer_than=False, filter=False,
                        shorter_urls=False, major=None, assumeyes=False, at=None,
                        having_asset=None, even=False)
    args = parser.parse_args(argv)

    if args.repo == "self":
        args.repo = __self__

    # "expand" repo:1.2 as repo --branch 1.2
    if ':' in args.repo and \
            not (args.repo.startswith(('https://', 'http://')) and args.repo.count(':') == 1):
        # right split ':' once only to preserve it in protocol of URLs
        # https://github.com/repo/owner:2.1
        repo_args = args.repo.rsplit(':', 1)
        args.repo = repo_args[0]
        args.major = repo_args[1]

    # instead of using root logger, we use
    logger = logging.getLogger('lastversion')
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    # create formatter
    fmt = '%(name)s - %(levelname)s - %(message)s' if args.verbose else '%(levelname)s: %(message)s'
    formatter = logging.Formatter(fmt)
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        log.info("Verbose %s level output.", args.verbose)
        if args.verbose >= 2:
            cachecontrol_logger = logging.getLogger('cachecontrol')
            cachecontrol_logger.removeHandler(logging.NullHandler())
            cachecontrol_logger.addHandler(ch)
            cachecontrol_logger.setLevel(logging.DEBUG)

    if args.assets:
        args.format = 'assets'

    if args.source:
        args.format = 'source'

    if args.filter:
        args.filter = re.compile(args.filter)

    if args.action in ['test', 'format']:
        v = parse_version(args.repo)
        if not v:
            log.critical('Failed to parse as a valid version')
            sys.exit(1)
        else:
            # extract the desired print base
            v = v.sem_extract_base(args.sem)
            if args.action == 'test':
                print("Parsed as: {}".format(v))
                print("Stable: {}".format(not v.is_prerelease))
            else:
                print(v)
            return sys.exit(0)

    if args.action == 'install':
        # we can only install assets
        args.format = 'json'
        if args.having_asset is None:
            args.having_asset = r'~\.(AppImage|rpm)$'
            try:
                import apt
                args.having_asset = r'~\.(AppImage|deb)$'
            except ImportError:
                pass

    if args.repo.endswith('.spec'):
        args.action = 'update-spec'
        args.format = 'dict'

    if not args.sem:
        if args.action == 'update-spec':
            args.sem = 'minor'
        else:
            args.sem = 'any'
    # imply source download, unless --assets specified
    # --download is legacy flag to specify download action or name of desired download file
    # --download == None indicates download intent where filename is based on upstream
    if args.action == 'download' and args.download is False:
        args.download = None

    if args.download is not False:
        args.action = 'download'
        if args.format != 'assets':
            args.format = 'source'

    if args.action in ['extract', 'unzip'] and args.format != 'assets':
        args.format = 'source'

    if args.newer_than:
        base_compare = parse_version(args.repo)
        if base_compare:
            print(max([args.newer_than, base_compare]))
            return sys.exit(2 if base_compare <= args.newer_than else 0)

    # other action are either getting release or doing something with release (extend get action)
    try:
        res = latest(args.repo, args.format, args.pre, args.filter,
                     args.shorter_urls, args.major, args.only, args.at,
                     having_asset=args.having_asset, exclude=args.exclude, even=args.even)
    except (ApiCredentialsError, BadProjectError) as error:
        log.critical(str(error))
        if isinstance(error, ApiCredentialsError) and "GITHUB_API_TOKEN" not in os.environ and \
                "GITHUB_TOKEN" not in os.environ:
            log.critical(TOKEN_PRO_TIP)
        sys.exit(4)

    if res:
        if args.action == 'update-spec':
            return update_spec(args.repo, res, sem=args.sem)
        if args.action == 'download':
            # download command
            if args.format == 'source':
                # there is only one source, but we need an array
                res = [res]
            download_name = None
            # save with custom filename if there's one file to download
            if len(res) == 1:
                download_name = args.download
            for url in res:
                log.info("Downloading %s ...", url)
                download_file(url, download_name)
            sys.exit(0)

        if args.action in ['unzip', 'extract']:
            # download command
            if args.format == 'source':
                # there is only one source, but we need an array
                res = [res]
            for url in res:
                log.info("Extracting %s ...", url)
                extract_file(url)
            sys.exit(0)

        if args.action == 'install':
            app_images = [asset for asset in res['assets'] if asset.endswith('.AppImage')]
            if app_images:
                return install_app_image(
                    app_images[0], install_name=res.get('install_name', args.repo)
                )
            rpms = [asset for asset in res['assets'] if asset.endswith('.rpm')]
            if not rpms:
                log.error('No assets found to install')
                sys.exit(1)
            # prevents downloading large packages if we already have newest installed
            # consult RPM database  for current version
            installed_version = rpm_installed_version(args.repo)
            if installed_version is False:
                log.warning('Please install lastversion using YUM or DNF so it can check current '
                            'program version. This is helpful to prevent unnecessary downloads')
            if installed_version and Version(installed_version) >= Version(res['version']):
                log.warning('Newest version {} is already installed'.format(installed_version))
                sys.exit(0)
            # pass RPM URLs directly to package management program
            try:
                import subprocess
                params = ['yum', 'install']
                params.extend(rpms)
                if args.assumeyes:
                    params.append('-y')
                subprocess.call(params)
            except OSError:
                log.critical('Failed to launch package manager. Only YUM/DNF is supported!')
                sys.exit(1)
            # if the system has yum, then lastversion has to be installed from yum and
            # has access to system packages like yum python or dnf python API
            # if install_with_dnf(rpms) is False or install_with_yum(rpms) is False:
            #     log.error('Failed talking to either DNF or YUM for package install')
            #     sys.exit(1)
            sys.exit(0)

        # display version in various formats:
        if args.format == 'assets':
            print("\n".join(res))
        elif args.format == 'json':
            json.dump(res, sys.stdout)
        else:
            # result may be a tag str, not just Version
            if isinstance(res, Version):
                res = res.sem_extract_base(args.sem)
            print(res)
            # special exit code "2" is useful for scripting to detect if no newer release exists
            if args.newer_than:
                # set up same SEM base
                args.newer_than = args.newer_than.sem_extract_base(args.sem)
                if res <= args.newer_than:
                    sys.exit(2)
    else:
        # empty list returned to --assets, emit 3
        if args.format == 'assets' and res is not False:
            sys.exit(3)
        log.critical("No release was found")
        sys.exit(1)


if __name__ == "__main__":
    main()
