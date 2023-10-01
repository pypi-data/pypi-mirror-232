"""Builds the README Markdown file for your codebase."""

from pathlib import Path
from typing import List, Tuple

from pkg_resources import resource_filename

from . import conf, factory, logger, utils

logger = logger.Logger(__name__)


def build_readme_file(
    config: conf.AppConfig,
    helper: conf.ConfigHelper,
    packages: list,
    code_summary: tuple,
) -> None:
    """Builds the README Markdown file for your codebase."""
    readme_sections = build_markdown_sections(
        config, helper, packages, code_summary
    )
    readme_file = "\n".join(readme_sections)
    readme_path = Path(config.paths.readme)

    factory.FileHandler().write(readme_path, readme_file)
    logger.info(f"README file generated at: {readme_path}")


def build_markdown_sections(
    config: conf.AppConfig,
    helper: conf.ConfigHelper,
    packages: list,
    code_summary: tuple,
) -> List[str]:
    """Constructs each section of the README file."""
    name = config.git.name
    repository = config.git.repository
    user_repo = utils.get_user_repository_name(repository)

    badges_path = resource_filename(__package__, f"{config.paths.badges}")
    badges_dict = factory.FileHandler().read(badges_path)
    markdown_badges = config.md.badges.format(
        get_badges(badges_dict, packages), user_repo
    )
    markdown_badges = (
        utils.remove_substring(markdown_badges)
        if "invalid" in user_repo.lower()
        else markdown_badges
    )

    markdown_setup_guide = create_setup_guide(config, helper, code_summary)

    if config.api.offline_mode is False:
        tables = create_markdown_tables(config.md.default, code_summary)
        config.md.tables = create_tables(tables, config.md.dropdown, user_repo)

    markdown_sections = [
        config.md.header,
        markdown_badges,
        config.md.toc.format(name),
        config.md.intro,
        config.md.tree,
        config.md.modules,
        config.md.tables,
        config.md.setup.format(name, repository, *markdown_setup_guide),
        config.md.ending,
    ]
    return markdown_sections


def get_badges(svg_icons: dict, dependencies: list) -> str:
    """Returns a list of badges for the project dependencies."""
    badges = [
        svg_icons[str(dependency).lower()]
        for dependency in dependencies
        if str(dependency).lower() in svg_icons
    ]
    # Sort badges by hex value (from light to dark color)
    badges.sort(key=lambda b: int(b[1], 16) if b[1] else 0, reverse=True)
    badges = [badge[0] for badge in badges]
    return format_badges(badges)


def format_badges(badges: list) -> str:
    """Formats the SVG icons into Markdown image tags."""
    badge_lines = []
    total_badges = len(badges)
    if total_badges < 8:
        badges_per_line = total_badges
    else:
        badges_per_line = total_badges // 2 + (total_badges % 2)

    if badges_per_line == 0:
        return ""

    for i in range(0, total_badges, badges_per_line):
        line = "\n".join(
            [
                f'<img src="{badge}" alt="{badge.split("/badge/")[1].split("-")[0]}" />'
                for badge in badges[i : i + badges_per_line]
            ]
        )
        badge_lines.append(line)

    return "\n\n".join(badge_lines)


def create_setup_guide(
    config: conf.AppConfig, helper: conf.ConfigHelper, summary_list: list
):
    """Creates the 'Getting Started' section of the README file."""
    try:
        default_install_command = (
            default_run_command
        ) = default_test_command = config.md.default

        language_counts = {}
        for module, _ in summary_list:
            language = Path(module).suffix[1:]
            if language and language not in helper.ignore_files:
                if language in language_counts:
                    language_counts[language] += 1
                else:
                    language_counts[language] = 1

        if language_counts:
            language_top = max(language_counts, key=language_counts.get)
            language_name = helper.language_names.get(language_top, "Unknown")
            language_setup = helper.language_setup.get(language_name, [])

            logger.info(f"{language_name} setup guide: {language_setup}")

            if len(language_setup) >= 3:
                default_install_command = language_setup[0]
                default_run_command = language_setup[1]
                default_test_command = language_setup[2]

    except Exception as exc:
        logger.debug(
            f"Error: {exc}\nUsing default setup: {default_run_command}"
        )

    return (default_install_command, default_run_command, default_test_command)


def create_markdown_tables(
    placeholder: str, code_summary: Tuple[str, str]
) -> List[Tuple[str, str]]:
    """Formats the generated code code_summary into a list."""
    summary_list = []
    for summary in code_summary:
        if isinstance(summary, tuple) and len(summary) == 2:
            module, summary_text = summary
        else:
            module, summary_text = summary, placeholder
        summary_list.append((module, summary_text))
    return summary_list


def create_tables(
    summary_list: List[Tuple[str, str]], dropdown: str, user_repo_name: str
) -> str:
    """Creates Markdown tables for each sub-directory in the project."""
    sub_folder_map = {}
    for module, summary in summary_list:
        sub_folder = (
            str(module).split("/")[-2].capitalize()
            if "/" in str(module)
            else "Root"
        )
        if sub_folder in sub_folder_map:
            sub_folder_map[sub_folder].append((module, summary))
        else:
            sub_folder_map[sub_folder] = [(module, summary)]

    tables = []
    for sub_folder, entries in sub_folder_map.items():
        table_data = entries
        table = create_table(table_data, user_repo_name)
        table_wrappers = dropdown.format(sub_folder, table)
        tables.append(table_wrappers)
    return "\n".join(tables)


def create_table(data: List[Tuple[str, str]], user_repo_name: str) -> str:
    """Creates a Markdown table from the given data."""
    headers = ["File", "Summary"]
    lines = [headers, ["---"] * len(headers)]
    for row in data:
        module, summary = row
        filename = str(Path(module).name)
        if "invalid" in user_repo_name.lower():
            link = filename
        else:
            github_url = utils.get_github_file_link(module, user_repo_name)
            link = f"[{filename}]({github_url})"
        lines.append([link, summary])

    max_len = [
        max(len(str(row[i])) for row in lines) for i in range(len(headers))
    ]
    formatted_lines = []
    for line in lines:
        formatted_line = (
            "| "
            + " | ".join(
                str(item).ljust(length) for item, length in zip(line, max_len)
            )
            + " |"
        )
        formatted_lines.append(formatted_line)

    return "\n".join(formatted_lines)


def build_recursive_tables(base_url: str, directory: Path, placeholder) -> str:
    """Creates a Markdown table structure for the given directory."""
    markdown = ""
    markdown += "| File | Summary |\n"
    markdown += "| --- | --- |\n"

    for item in sorted(directory.iterdir()):
        if item.is_file():
            markdown += f"| [{item.name}]({item.name}) | {placeholder} |\n"

    for item in sorted(directory.iterdir()):
        if item.is_dir():
            # If it is a sub-directory, create a collapsible section
            markdown += f"\n<details closed><summary>{item.name}</summary>\n\n"
            # Recursive call for sub-directory
            markdown += build_recursive_tables(base_url, item, placeholder)
            # Close the collapsible section
            markdown += "\n</details>\n\n"

    return markdown


def generate_tree(
    directory: Path,
    repo_url: str,
    prefix: str = "",
    is_last: bool = True,
    parent_prefix: str = "",
) -> str:
    """Recursively generates a tree structure for a given directory."""
    if directory.name == directory:
        return ""
    if directory == repo_url:
        display_name = "."
    else:
        display_name = directory.name

    box_branch = "└── " if is_last else "├── "
    tree_str = parent_prefix + box_branch + display_name

    if directory.is_dir():
        tree_str += "/\n"
        children = sorted(
            [child for child in directory.iterdir() if child.name != ".git"]
        )
        for index, child in enumerate(children):
            is_last_child = index == len(children) - 1
            child_prefix = "    " if is_last else "│   "
            tree_str += generate_tree(
                child,
                repo_url,
                box_branch,
                is_last_child,
                f"{parent_prefix}{child_prefix}",
            )
    else:
        tree_str += "\n"

    return tree_str


def format_tree(name: str, tree_str: str) -> str:
    """Replaces tmp directory name with project name."""
    tree_str = tree_str.split("\n", 1)
    tree_str[0] = f"└── {name}/"
    tree_str = "\n".join(tree_str)
    tree = f"```sh\n{tree_str}```"
    return tree
