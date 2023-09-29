from __future__ import annotations

import collections
import itertools
import pathlib

import mknodes as mk

from mknodes.info import contexts
from mknodes.utils import log, requirements


logger = log.get_logger(__name__)


class BuildCollector:
    """A class to assist in extracting build stuff from a Node tree + Theme."""

    def __init__(self, show_page_info: bool = False):
        """Constructor.

        Arguments:
            show_page_info: Add a admonition box containing page build info to each page
        """
        self.show_page_info = show_page_info
        self.node_files: dict[str, str | bytes] = {}
        self.extra_files: dict[str, str | bytes] = {}
        self.node_counter: collections.Counter[str] = collections.Counter()
        self.requirements = requirements.Requirements()
        self.mapping: dict[str, mk.MkNode] = dict()

    def collect(self, root: mk.MkNode, theme):
        """Collect build stuff from given node + theme.

        Arguments:
            root: A node to collect build stuff from
            theme: A theme to collect build stuff from.
        """
        logger.debug("Collecting theme requirements...")
        iterator = itertools.chain(theme.iter_nodes(), root.iter_nodes())
        nodes = [i[1] for i in iterator]
        for node in nodes:
            self.node_counter.update([node.__class__.__name__])
            self.extra_files |= node.files
            match node:
                case mk.MkPage() as page:
                    self.collect_page(page)
                case mk.MkNav() as nav:
                    self.collect_nav(nav)
        logger.debug("Setting default markdown extensions...")
        reqs = theme.get_requirements()
        self.requirements.merge(reqs)
        logger.debug("Adapting collected extensions to theme...")
        theme.adapt_extensions(self.requirements)
        return contexts.BuildContext(
            page_mapping=self.mapping,
            requirements=self.requirements,
            node_counter=self.node_counter,
            build_files=self.node_files | self.extra_files,
        )

    def collect_page(self, page: mk.MkPage):
        if not page.inclusion_level:
            return
        path = page.resolved_file_path
        self.mapping[path] = page
        req = page.get_requirements()
        self.requirements.merge(req)
        if page.template:
            node_path = pathlib.Path(path)
        elif any(i.page_template for i in page.parent_navs):
            nav = next(i for i in page.parent_navs if i.page_template)
            node_path = pathlib.Path(nav.resolved_file_path)
        else:
            node_path = None
        if node_path:
            html_path = node_path.with_suffix(".html").as_posix()
            page._metadata.template = html_path
            page.template.filename = html_path
            for nav in page.parent_navs:
                if nav.page_template:
                    p = pathlib.Path(nav.resolved_file_path)
                    parent_path = p.with_suffix(".html").as_posix()
                    page.template.extends = parent_path
                    break
        if self.show_page_info:
            adm = mk.MkAdmonition([], title="Page info", typ="theme", collapsible=True)

            if page.created_by:
                typ = "section" if page.is_index() else "page"
                details = mk.MkAdmonition(
                    mk.MkCode.for_object(page.created_by),
                    title=f"Code for this {typ}",
                    collapsible=True,
                    typ="quote",
                )
                adm += details

            title = "Requirements"
            pretty = mk.MkPrettyPrint(req)
            details = mk.MkAdmonition(pretty, title=title, collapsible=True, typ="quote")
            adm += details

            title = "Metadata"
            code = mk.MkCode(str(page.metadata), language="yaml")
            details = mk.MkAdmonition(code, title=title, collapsible=True, typ="quote")
            adm += details

            page += adm
        md = page.to_markdown()
        self.node_files[path] = md

    def collect_nav(self, nav: mk.MkNav):
        logger.info("Processing section %r...", nav.section)
        path = nav.resolved_file_path
        self.mapping[path] = nav
        if nav.page_template:
            html_path = pathlib.Path(path).with_suffix(".html").as_posix()
            for parent_nav in nav.parent_navs:
                if parent_nav.page_template:
                    p = pathlib.Path(parent_nav.resolved_file_path)
                    parent_path = p.with_suffix(".html").as_posix()
                    nav.page_template.extends = parent_path
                    break
            nav.metadata.template = html_path
            nav.page_template.filename = html_path
        md = nav.to_markdown()
        self.node_files[path] = md


if __name__ == "__main__":
    project = mk.Project.for_mknodes()
    from mknodes.manual import root

    log.basic()
    root.build(project)
    if project._root:
        collector = BuildCollector()
        ctx = collector.collect(project._root, project.theme)
        print(ctx)
