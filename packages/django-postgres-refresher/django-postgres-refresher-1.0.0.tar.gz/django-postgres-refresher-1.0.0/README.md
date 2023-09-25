### Installation
```bash
$ pip install django-postgres-refresher
```

#### `settings.py`
```python
INSTALLED_APPS+=['django_postgres_refresher']
```

#### `migrate`
```bash
$ python manage.py migrate
```

### Features
+   admin interface
+   refresh reports (`duration`,`time`) and stat (`count`,`avg_duration`,`min_duration`,`max_duration`)

### Examples
refresh matviews
```bash
python manage.py postgres_refresher
```

`INSERT` to `postgres_refresher_config`
```sql
INSERT INTO postgres_refresher_config(schemaname,matviewname,"concurrently",seconds)
VALUES
('schemaname','matviewname',true,600),
('schemaname','matviewname2',true,600)
ON CONFLICT(schemaname,matviewname) DO NOTHING;
```


