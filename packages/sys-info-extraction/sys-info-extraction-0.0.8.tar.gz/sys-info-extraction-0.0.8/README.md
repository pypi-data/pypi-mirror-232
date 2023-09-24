# sys-info-extraction
### Operation Python from
```Python
from extraction import DiskInfo

from extraction import LoadsInfo

from extraction import NetworkInfo
```
### Operation Python import
```python
import extraction.DiskInfo as DiskInfo

import extraction.LoadsInfo as LoadsInfo

import extraction.NetworkInfo as NetworkInfo
```
### Python statements on Linux Release: Centos7/Redhat or Ubuntu
```python
import extraction.NetworkInfo as NetworkInfo

interface = NetworkInfo.network()
ip_info = interface.interfaces()
print(ip_info)
```
