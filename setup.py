import setuptools  # 导入setuptools打包工具

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="addcomments",
    version="0.0.3",
    author="yangliu",
    author_email="codeliuyang@163.com",
    description="add database table column comments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/codeliuyang/django_mysql_comment",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
