from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="sentinel_mcp",
    version="0.1.0",
    author="@egallis31",
    author_email="",
    description="A Python-based MCP server for Microsoft Sentinel integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gallis-local/SentinelMCPServer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "azure-identity",
        "azure-monitor-query",
        "pyyaml",
        "msgraph-sdk",
        "python-dotenv",
        "pandas",
        "fastmcp",
        "mcp"
    ],
    entry_points={
        "console_scripts": [
            "sentinel-mcp=sentinel_mcp.server:main",
        ],
    },
)

