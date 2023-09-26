from os.path import getctime
from datetime import datetime
from pkg_resources import working_set

# This module is deprecated. Users are directed to importlib.resources,
# importlib.metadata and packaging instead.


def main():
    installed_packages = list(working_set)
    package_info = []
    for package in installed_packages:
        package_name = package.project_name
        package_version = package.version
        package_location = package.location

        timestamp = datetime.fromtimestamp(getctime(package_location)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        package_info.append(
            (package_name, package_version, timestamp, package_location)
        )

    sorted_packages = sorted(
        package_info,
        key=lambda x: datetime.strptime(x[2], "%Y-%m-%d %H:%M:%S"),
        reverse=True,
    )

    # a function for outputing Two-dimensional list in a tabular form at the terminal
    def print_table(data):
        column_widths = [
            max(len(str(item)) for item in column) for column in zip(*data)
        ]

        # Print the table header border
        for width in column_widths:
            print(f"+{'-' * (width + 2)}", end="")
        print("+")

        # Print head
        for item, width in zip(data[0], column_widths):
            print(f"| {item:{width}} ", end="")
        print("|")

        # Print form border
        for width in column_widths:
            print(f"+{'-' * (width + 2)}", end="")
        print("+")

        # Print row
        for row in data[1:]:
            for item, width in zip(row, column_widths):
                print(f"| {item:{width}} ", end="")
            print("|")

        # Print table bottom border
        for width in column_widths:
            print(f"+{'-' * (width + 2)}", end="")
        print("+")

    # data
    data = [
        [
            f"Module: {len(sorted_packages)} total",
            "Version",
            "Last Modified",
            "Location",
        ]
    ] + sorted_packages

    # Call the function to print a table with borders
    print_table(data)


if __name__ == "__main__":
    main()
