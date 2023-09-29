from pypi_deploy_test import VERSION, GIT_REVISION, GIT_REVISION_DATETIME


def main() -> None:
    data = f"""
Version: {VERSION}
Git revision: {GIT_REVISION}
Git revision date: {GIT_REVISION_DATETIME.isoformat()}
"""
    print(data)


if __name__ == '__main__':
    main()
