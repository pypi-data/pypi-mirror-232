## Prompter9000
Quick &amp; easy way to edit dictionaries. Console & programmatic usages are supported.

### Programatic

```
from Prompter9000.PyEdit import *
params = {"NAME":'My', "PHONE":'123-456', "EMAIL":'a.Geekbo@zbobo.com'}
EditDict.edit(params)
```
*GUI*: Dictionary results will be returned ONLY IF the data was changed. Otherwise an empty dictionary will be returned.

May also be used from the C.L.I:

### Console

```
python PyEdit.py "{'NAME': 'My', 'PHONE': '123-456', 'EMAIL': 'a.Geekbo@zbobo.com'}"
{'NAME': 'My', 'PHONE': '123-456', 'EMAIL': 'a.Geekbo@zbobo.com', '__btn_ok': True}
```

*CLI*: The **__btn_ok** will be either **True** when user-selected, else **False**.

### PyPi

Now available on [PyPi](https://pypi.org/project/Prompter9000/)
