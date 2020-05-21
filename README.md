# PyScript
自用脚本

# explain
## 1. 编码导致中文无法显示
如遇到脚本执行中，出现编码问题
```
UnicodeEncodeError: 'ascii' codec can't encode characters in position 0-8: ordinal not in range(128)
```
可以强制脚本编码，如 ``$ PYTHONIOENCODING=utf-8 ./demo.py`` 来解决
