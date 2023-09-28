import os
import argparse


def find_files_with_extension(directory, extension):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extension):
                file_paths.append(os.path.join(root, file))
    return file_paths


def create_md_links(file_paths):
    md_links = []
    current_section = None

    for path in file_paths:
        section = os.path.basename(os.path.dirname(path))
        if section != current_section:
            md_links.append(f"\n## {section}\n")
            current_section = section
        link_name = os.path.splitext(os.path.basename(path))[0]
        md_links.append(f"- [{link_name}](<{path}>)")

    return md_links


def save_to_md_file(file_paths, output_file):
    md_links = create_md_links(file_paths)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_links))


def main():
    parser = argparse.ArgumentParser(
        description="Generate Markdown links for specified files."
    )
    parser.add_argument("output_file", help="Output Markdown file name")
    parser.add_argument("extension", help="File extension to search for (e.g., .pdf)")
    parser.add_argument("directory", nargs="+", help="Directories to search for files")

    args = parser.parse_args()

    file_paths = []
    for directory in args.directory:
        file_paths.extend(find_files_with_extension(directory, args.extension))

    save_to_md_file(file_paths, args.output_file)
    print(f"Markdown links saved to {args.output_file}")


if __name__ == "__main__":
    main()
