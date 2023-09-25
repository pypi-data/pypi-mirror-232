### Installation
```bash
$ pip install django-bulk_create
```

### Features
*   multiple models aggregator

### Examples
```python
from django_bulk_create import bulk_create
from apps.app.models import Model1, Model2

create_list = []
create_list+=[Model1(id=42,description='description')]
create_list+=[Model2(key="value")]

model2kwargs = {
    Model1: dict(
        update_conflicts=True,
        unique_fields = ['id'],
        update_fields = [
            'description',
        ]
    ),
    Model2: dict(ignore_conflicts=True)
}
bulk_create(create_list,model2kwargs)
```

