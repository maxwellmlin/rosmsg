import os
import subprocess
import sys
import argparse


def find_msg_files(base_path):
    """
    Recursively find all .msg files in the directory.

    :param base_path: Path to the base directory.
    :return: List of relative paths to .msg files.
    """
    msg_files = []
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".msg"):
                msg_files.append(os.path.relpath(os.path.join(root, file), base_path))
    return msg_files


def process_msg_files(base_path, fixed_base_path):
    """
    Process each .msg file with the npx gendeps2 command and write to a mirrored directory structure.

    :param base_path: Path to the base directory containing .msg files.
    :param fixed_base_path: Path to the base directory for fixed .msg files.
    """
    msg_files = find_msg_files(base_path)

    for relative_path in msg_files:
        full_msg_path = os.path.join(base_path, relative_path)
        fixed_msg_path = os.path.join(fixed_base_path, relative_path)

        # Ensure the directory exists for the fixed path
        os.makedirs(os.path.dirname(fixed_msg_path), exist_ok=True)

        # Run the command
        try:
            result = subprocess.run(
                ["npx", "gendeps2", base_path, full_msg_path],
                capture_output=True,
                text=True,
                check=True
            )

            # Write the output to the fixed .msg file
            with open(fixed_msg_path, "w") as msg_file:
                msg_file.write(result.stdout)

            print(f"Processed: {relative_path} -> {fixed_msg_path}")

        except subprocess.CalledProcessError as e:
            print(f"Error processing {relative_path}: {e.stderr}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Process .msg files with npx gendeps2 and write to a fixed directory structure.")
    parser.add_argument("source", type=str, help="Path to the ros2jazzy directory.")
    parser.add_argument("destination", type=str, help="Path to the ros2jazzy_fixed directory.")

    args = parser.parse_args()
    base_path = os.path.abspath(args.source)
    fixed_base_path = os.path.abspath(args.destination)

    if not os.path.isdir(base_path):
        print(f"Error: {base_path} is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    process_msg_files(base_path, fixed_base_path)


if __name__ == "__main__":
    main()
