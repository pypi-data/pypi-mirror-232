### Installation
```bash
$ pip install django-bulk_delete
```

### Features
*   multiple models aggregator

### Examples
```python
from django_bulk_delete import bulk_delete
from apps.app.models import Model1, Model2

delete_list = []
for obj in Model1.objects.all():
	if delete_condition:
		delete_list+=[obj]
for obj in Model2.objects.all():
	if delete_condition:
		delete_list+=[obj]

bulk_delete(delete_list)
```

