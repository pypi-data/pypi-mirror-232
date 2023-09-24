import logging

from .BitBucketRepoSession import BitBucketRepoSession
from .FeedRepoSession import FeedRepoSession
from .GitHubRepoSession import GitHubRepoSession
from .GitLabRepoSession import GitLabRepoSession
from .GiteaRepoSession import GiteaRepoSession
from .HelmChartRepoSession import HelmChartRepoSession
from .LocalVersionSession import LocalVersionSession
from .MercurialRepoSession import MercurialRepoSession
from .PypiRepoSession import PypiRepoSession
from .SourceForgeRepoSession import SourceForgeRepoSession
from .SystemRepoSession import SystemRepoSession
from .WikipediaRepoSession import WikipediaRepoSession
from .WordPressPluginRepoSession import WordPressPluginRepoSession
from .utils import BadProjectError

log = logging.getLogger(__name__)


class HolderFactory:
    HOLDERS = {
        'github': GitHubRepoSession,
        'gitlab': GitLabRepoSession,
        'bitbucket': BitBucketRepoSession,
        'pip': PypiRepoSession,
        'hg': MercurialRepoSession,
        'sf': SourceForgeRepoSession,
        'website-feed': FeedRepoSession,
        'local': LocalVersionSession,
        'helm_chart': HelmChartRepoSession,
        'wiki': WikipediaRepoSession,
        'system': SystemRepoSession,
        'wp': WordPressPluginRepoSession,
        'gitea': GiteaRepoSession
    }

    DEFAULT_HOLDER = 'github'

    @staticmethod
    def guess_from_homepage(repo, hostname):
        """
        Try to guess the right holder for a given repo and domain.
        Args:
            repo:
            hostname:

        Returns:

        """
        # repo auto-discovery failed for detected/default provider
        # now we simply try website provider based on the hostname/RSS feeds in HTML or GitHub links
        holder = FeedRepoSession(repo, hostname)
        if not holder.is_valid():
            # re-use soup from the feed holder object
            log.info('Have not found any RSS feed for the website %s', hostname)
            github_link = holder.home_soup.select_one("a[href*='github.com']")
            if github_link:
                hostname, repo = GitHubRepoSession.get_host_repo_for_link(github_link['href'])
                holder = GitHubRepoSession(repo, hostname)
        return holder

    @staticmethod
    # go through subclasses in order to find the one that is holding a given project
    # repo is either complete URL or a name allowing to identify a single project
    def get_instance_for_repo(repo, at=None):
        """Find the right hosting for this repo."""
        if at == 'helm_chart' or (at and not repo.startswith(('http:', 'https:'))):
            return HolderFactory.HOLDERS[at](repo, hostname=None)
        holder_class = HolderFactory.HOLDERS[HolderFactory.DEFAULT_HOLDER]
        hostname = None
        known_repo = None

        for k, sc in HolderFactory.HOLDERS.items():
            known_repo = sc.is_official_for_repo(repo)
            if known_repo:
                holder_class = sc
                log.info('Trying %s adapter', k)
                break
            # TODO now easy multiple default hostnames per holder
            hostname = sc.get_matching_hostname(repo)
            if hostname:
                holder_class = sc
                break
        if known_repo:
            repo = known_repo['repo']
            # Known repo tells us hosted domain of e.g., mercurial web
            if 'hostname' in known_repo:
                hostname = known_repo['hostname']
        else:
            hostname, repo = holder_class.get_host_repo_for_link(repo)

        holder = holder_class(repo, hostname)
        if not holder.is_valid() and hostname:
            holder = HolderFactory.guess_from_homepage(repo, hostname)
            if not holder.is_valid():
                raise BadProjectError(
                    'No project found. Could not guess a repo from homepage'
                )

        if known_repo and 'branches' in known_repo:
            holder.set_branches(known_repo['branches'])

        if known_repo and 'only' in known_repo:
            holder.set_only(known_repo['only'])

        if known_repo and 'release_url_format' in known_repo:
            holder.RELEASE_URL_FORMAT = known_repo['release_url_format']

        return holder
