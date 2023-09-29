from __future__ import annotations

from collections.abc import Callable
import os
import pathlib

from typing import Any, Generic, TypeVar

from mknodes import buildcollector, paths
from mknodes.info import contexts, folderinfo, linkprovider, packageregistry
from mknodes.jinja import environment
from mknodes.navs import mknav
from mknodes.theme import theme as theme_
from mknodes.utils import classhelpers, helpers, jinjahelpers, log, reprhelpers


logger = log.get_logger(__name__)


T = TypeVar("T", bound=theme_.Theme)


class Project(Generic[T]):
    """MkNodes Project."""

    def __init__(
        self,
        theme: T,
        repo: str | os.PathLike | None | folderinfo.FolderInfo = None,
        build_fn: str | Callable = paths.DEFAULT_BUILD_FN,
        build_kwargs: dict[str, Any] | None = None,
        base_url: str = "",
        use_directory_urls: bool = True,
        clone_depth: int = 100,
    ):
        """The main project to create a website.

        Arguments:
            theme: The theme to use
            repo: Path to the git repository
            build_fn: Callable to create the website with
            build_kwargs: Keyword arguments for the build function
            base_url: Base url of the website
            use_directory_urls: Whether urls are in directory-style
            clone_depth: Amount of commits to clone in case repository is remote.
        """
        self.linkprovider = linkprovider.LinkProvider(
            base_url=base_url,
            use_directory_urls=use_directory_urls,
            include_stdlib=True,
        )
        self.env = environment.Environment(undefined="strict", load_templates=True)
        self.env.filters["get_link"] = self.linkprovider.get_link
        self.env.filters["get_url"] = self.linkprovider.get_url
        jinjahelpers.set_markdown_exec_namespace(self.env.globals)
        self.theme: T = theme
        self.theme.associated_project = self
        match repo:
            case folderinfo.FolderInfo():
                self.folderinfo = repo
            case _ if helpers.is_url(str(repo)):
                self.folderinfo = folderinfo.FolderInfo.clone_from(
                    str(repo),
                    depth=clone_depth,
                )
            case _:
                self.folderinfo = folderinfo.FolderInfo(repo)

        self.context = contexts.ProjectContext(
            metadata=self.folderinfo.context,
            git=self.folderinfo.git.context,
            # github=self.folderinfo.github.context,
            theme=self.theme.context,
            links=self.linkprovider,
            env=self.env,
        )

        self._root: mknav.MkNav | None = None
        self.build_fn = classhelpers.to_callable(build_fn)
        self.build_kwargs = build_kwargs or {}

    def build(self, show_page_info: bool = False):
        logger.debug("Building page...")
        self.build_fn(project=self, **self.build_kwargs)
        logger.debug("Finished building page.")
        if not self._root:
            msg = "No root for project created."
            raise RuntimeError(msg)

        mapping = {
            node.resolved_file_path: node
            for _level, node in self._root.iter_nodes()
            if hasattr(node, "resolved_file_path")
        }

        paths = [pathlib.Path(i).stem for i in mapping]
        self.linkprovider.set_excludes(paths)

        self.env.globals |= self.context.as_dict()
        collector = buildcollector.BuildCollector(show_page_info=show_page_info)
        ctx = collector.collect(self._root, self.theme)
        self.env.globals |= ctx.as_dict()
        return ctx

    def __repr__(self):
        return reprhelpers.get_repr(self, repo_path=str(self.folderinfo.path))

    @classmethod
    def for_mknodes(cls, config=None) -> Project:
        from mknodes import mkdocsconfig

        config = mkdocsconfig.Config(config)
        kls = cls(
            base_url=config.site_url or "",
            use_directory_urls=config.use_directory_urls,
            theme=theme_.Theme.get_theme(config.theme.name, data=config.theme._vars),
            build_fn=config.plugins["mknodes"].config.build_fn,
        )
        kls.build()
        return kls

    @classmethod
    def for_path(cls, path: str, config=None) -> Project:
        from mknodes import mkdocsconfig

        config = mkdocsconfig.Config(config)
        kls = cls(
            base_url=config.site_url or "",
            use_directory_urls=config.use_directory_urls,
            theme=theme_.Theme.get_theme(config.theme.name, data=config.theme._vars),
            repo=folderinfo.FolderInfo.clone_from(path),
        )
        kls.build()
        return kls

    def set_root(self, nav: mknav.MkNav):
        """Set the root MkNav."""
        self._root = nav
        nav.associated_project = self

    def get_root(self, **kwargs: Any) -> mknav.MkNav:
        """Return the root MkNav.

        This MkNav should get populated in order to build
        the website.

        Arguments:
            kwargs: Keyword arguments passed to MkNav constructor.
        """
        self._root = mknav.MkNav(project=self, **kwargs)
        return self._root

    def populate_linkprovider(self):
        invs = self.folderinfo.mkdocs_config.get_inventory_infos()
        mk_urls = {i["url"]: i.get("base_url") for i in invs if "url" in i}
        for url, base_url in mk_urls.items():
            self.linkprovider.add_inv_file(url, base_url=base_url)
        for url in packageregistry.registry.inventory_urls:
            if url not in mk_urls:
                self.linkprovider.add_inv_file(url)


if __name__ == "__main__":
    project = Project.for_mknodes()
    from mknodes.manual import root

    log.basic()
    root.build(project)
    project.populate_linkprovider()
